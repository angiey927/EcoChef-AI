import 'dotenv/config';
import express from "express";
import cors from "cors";
import pkg from "pg";
import OpenAI from "openai";
import NodeCache from "node-cache";

const { Pool } = pkg;

const app = express();
app.use(cors({
  origin: '*',
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization']
}));
app.use(express.json());

const pool = new Pool({ connectionString: process.env.DATABASE_URL });

// Single OpenAI client
const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

// NodeCache instance
const aiCache = new NodeCache({ stdTTL: 3600 }); // cache 1 hour

// ================= USERS + INVENTORY =================

// Get user ingredients
app.get("/api/ingredients/:userId", async (req, res) => {
  const { userId } = req.params;
  try {
    const result = await pool.query(
      `SELECT i.name, ui.quantity, ui.unit
       FROM user_inventory ui
       JOIN ingredients i ON ui.ingredient_id = i.ingredient_id
       WHERE ui.user_id = $1 AND ui.used=FALSE AND ui.wasted=FALSE`,
      [userId]
    );
    res.json(result.rows);
  } catch (err) {
    console.error(err);
    res.status(500).send("Server error");
  }
});

app.post("/api/addIngredient", async (req, res) => {
  const { name, category, userId, quantity = 1, unit = "unit" } = req.body;

  try {
    const ing = await pool.query(
      `INSERT INTO ingredients (name, category)
       VALUES ($1, $2)
       ON CONFLICT (name) DO NOTHING
       RETURNING ingredient_id`,
      [name, category]
    );

    const ingredientId =
      ing.rows[0]?.ingredient_id ||
      (await pool.query(`SELECT ingredient_id FROM ingredients WHERE name=$1`, [name])).rows[0].ingredient_id;

    await pool.query(
      `INSERT INTO user_inventory (user_id, ingredient_id, quantity, unit)
       VALUES ($1, $2, $3, $4)
       ON CONFLICT (user_id, ingredient_id) DO UPDATE
       SET quantity = user_inventory.quantity + EXCLUDED.quantity`,
      [userId, ingredientId, quantity || 1, unit || "unit"]
    );

    res.send("Ingredient added");
  } catch (err) {
    console.error(err);
    res.status(500).send("Server error");
  }
});

// ================= RECIPES =================

// Get recipes based on user ingredients
app.get("/api/recipes/:userId", async (req, res) => {
  const { userId } = req.params;
  try {
    const userIng = await pool.query(
      `SELECT ingredient_id FROM user_inventory 
       WHERE user_id=$1 AND used=FALSE AND wasted=FALSE`,
      [userId]
    );

    const ingredientIds = userIng.rows.map(row => row.ingredient_id);
    if (!ingredientIds.length) return res.json([]);

    const recipes = await pool.query(
      `SELECT r.recipe_id, r.name, r.instructions
       FROM recipes r
       JOIN recipe_ingredients ri ON r.recipe_id = ri.recipe_id
       WHERE ri.ingredient_id = ANY($1::int[])`,
      [ingredientIds]
    );
    res.json(recipes.rows);
  } catch (err) {
    console.error(err);
    res.status(500).send("Server error");
  }
});

// Generate recipe using OpenAI with caching
app.post("/api/generateRecipe", async (req, res) => {
  const { ingredientNames } = req.body;
  const cacheKey = ingredientNames.join(",");

  try {
    let recipeText = aiCache.get(cacheKey);
    if (!recipeText) {
      const prompt = `Create a simple recipe using only these ingredients: ${ingredientNames.join(", ")}. Include a recipe name and instructions.`;
      const completion = await openai.chat.completions.create({
        model: "gpt-4o-mini",
        messages: [{ role: "user", content: prompt }]
      });
      recipeText = completion.choices[0].message.content;
      aiCache.set(cacheKey, recipeText);
    }

    res.json({ recipe: recipeText });
  } catch (err) {
    console.error(err);
    res.status(500).send("Failed to generate recipe");
  }
});

// Generate personalized recipe with caching
app.post("/api/generatePersonalRecipe", async (req, res) => {
  const { userId, ingredientNames } = req.body;
  const cacheKey = `personal_${userId}_${ingredientNames.join(",")}`;

  try {
    let recipeText = aiCache.get(cacheKey);
    if (!recipeText) {
      const prefResult = await pool.query(
        `SELECT dietary_preferences FROM users WHERE user_id=$1`,
        [userId]
      );
      const preferences = prefResult.rows[0]?.dietary_preferences || "";

      const prompt = `Create a recipe using only these ingredients: ${ingredientNames.join(", ")}. ` +
                     `Follow these dietary preferences: ${preferences}. Include a name, instructions, and approximate cooking time.`;

      const completion = await openai.chat.completions.create({
        model: "gpt-4o-mini",
        messages: [{ role: "user", content: prompt }]
      });

      recipeText = completion.choices[0].message.content;
      aiCache.set(cacheKey, recipeText);
    }

    res.json({ recipe: recipeText });
  } catch (err) {
    console.error(err);
    res.status(500).send("Failed to generate recipe");
  }
});

// Suggest alternatives for missing ingredients
app.post("/api/substituteIngredients", async (req, res) => {
  const { missingIngredients } = req.body;
  try {
    const prompt = `Suggest substitutes for the following ingredients: ${missingIngredients.join(", ")}. List 1-2 alternatives for each.`;
    const completion = await openai.chat.completions.create({
      model: "gpt-4o-mini",
      messages: [{ role: "user", content: prompt }]
    });

    const substitutions = completion.choices[0].message.content;
    res.json({ substitutions });
  } catch (err) {
    console.error(err);
    res.status(500).send("Failed to get substitutions");
  }
});

// Get nutritional info for a recipe
app.post("/api/getNutrition", async (req, res) => {
  const { recipeText } = req.body;
  try {
    const prompt = `Analyze this recipe and provide nutritional info: calories, protein, fat, carbs. Recipe: ${recipeText}`;
    const completion = await openai.chat.completions.create({
      model: "gpt-4o-mini",
      messages: [{ role: "user", content: prompt }]
    });

    const nutritionInfo = completion.choices[0].message.content;
    res.json({ nutritionInfo });
  } catch (err) {
    console.error(err);
    res.status(500).send("Failed to generate nutrition info");
  }
});

// Check for expiring ingredients
app.get("/api/expiringIngredients/:userId", async (req, res) => {
  const { userId } = req.params;
  try {
    const result = await pool.query(
      `SELECT name, quantity, unit, expiration_date
       FROM user_inventory ui
       JOIN ingredients i ON ui.ingredient_id = i.ingredient_id
       WHERE ui.user_id=$1 AND ui.expiration_date <= CURRENT_DATE + INTERVAL '3 days'`,
      [userId]
    );
    res.json(result.rows);
  } catch (err) {
    console.error(err);
    res.status(500).send("Server error");
  }
});

// Analytics dashboad - usage and waste tracking
app.get("/api/analytics/:userId", async (req, res) => {
  const { userId } = req.params;
  try {
    const usedResult = await pool.query(
      `SELECT i.name, COUNT(*) AS used_count
       FROM user_inventory ui
       JOIN ingredients i ON ui.ingredient_id = i.ingredient_id
       WHERE ui.user_id=$1 AND ui.used=TRUE
       GROUP BY i.name`,
      [userId]
    );

    const wastedResult = await pool.query(
      `SELECT i.name, COUNT(*) AS wasted_count
       FROM user_inventory ui
       JOIN ingredients i ON ui.ingredient_id = i.ingredient_id
       WHERE ui.user_id=$1 AND ui.wasted=TRUE
       GROUP BY i.name`,
      [userId]
    );

    res.json({ used: usedResult.rows, wasted: wastedResult.rows });
  } catch (err) {
    console.error(err);
    res.status(500).send("Server error");
  }
});

// ================= CONSUME RECIPE =================
app.post("/api/consumeRecipe", async (req, res) => {
  const { userId, recipeId } = req.body;

  try {
    // Get all ingredients and required quantities for the recipe
    const ingredientsResult = await pool.query(
      `SELECT ri.ingredient_id, ri.quantity AS required_quantity, ui.quantity AS user_quantity
       FROM recipe_ingredients ri
       JOIN user_inventory ui ON ri.ingredient_id = ui.ingredient_id
       WHERE ri.recipe_id=$1 AND ui.user_id=$2`,
      [recipeId, userId]
    );

    if (ingredientsResult.rows.length === 0) {
      return res.status(404).send("No ingredients found for this recipe in your inventory");
    }

    // Subtract quantities
    for (const row of ingredientsResult.rows) {
      let newQuantity = row.user_quantity - row.required_quantity;
      if (newQuantity <= 0) newQuantity = 0;

      await pool.query(
        `UPDATE user_inventory
         SET quantity = $1, used = CASE WHEN $1 > 0 THEN FALSE ELSE TRUE END
         WHERE user_id=$2 AND ingredient_id=$3`,
        [newQuantity, userId, row.ingredient_id]
      );
    }

    res.send("Ingredients updated after cooking!");
  } catch (err) {
    console.error(err);
    res.status(500).send("Server error");
  }
});

// ================= SERVER START =================
const PORT = process.env.PORT || 5000;
const HOST = process.env.HOST || '0.0.0.0';
app.listen(PORT, HOST, () => {
  console.log(`Server running on http://${HOST}:${PORT}`);
  console.log('For local access, use: http://localhost:' + PORT);
  console.log('For access from other devices on your network, use your computer\'s IP address');
});