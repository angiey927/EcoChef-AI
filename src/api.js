// src/api.js

const API_BASE = process.env.REACT_APP_API_URL || "http://localhost:5000/api";

// ================== Ingredients ==================
export const getIngredients = async (userId) => {
  try {
    const res = await fetch(`${API_BASE}/ingredients/${userId}`);
    return await res.json();
  } catch (err) {
    console.error("Failed to fetch ingredients:", err);
    return [];
  }
};

export const addIngredient = async ({ name, category, quantity = 1, unit = "unit", userId }) => {
  try {
    await fetch(`${API_BASE}/addIngredient`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, category, quantity, unit, userId }),
    });
  } catch (err) {
    console.error("Failed to add ingredient:", err);
  }
};

// ================== Recipes ==================
export const getRecipes = async (userId) => {
  try {
    const res = await fetch(`${API_BASE}/recipes/${userId}`);
    return await res.json();
  } catch (err) {
    console.error("Failed to fetch recipes:", err);
    return [];
  }
};

export const generateRecipe = async (ingredientNames) => {
  try {
    const res = await fetch(`${API_BASE}/generateRecipe`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ingredientNames }),
    });
    const data = await res.json();
    return data.recipe;
  } catch (err) {
    console.error("Failed to generate recipe:", err);
    return "";
  }
};

export const generatePersonalRecipe = async (userId, ingredientNames) => {
  try {
    const res = await fetch(`${API_BASE}/generatePersonalRecipe`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ userId, ingredientNames }),
    });
    const data = await res.json();
    return data.recipe;
  } catch (err) {
    console.error("Failed to generate personal recipe:", err);
    return "";
  }
};

// ================== Substitutions ==================
export const substituteIngredients = async (missingIngredients) => {
  try {
    const res = await fetch(`${API_BASE}/substituteIngredients`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ missingIngredients }),
    });
    const data = await res.json();
    return data.substitutions;
  } catch (err) {
    console.error("Failed to get substitutions:", err);
    return "";
  }
};

// ================== Consume Recipe ==================
export const consumeRecipe = async (userId, recipeId) => {
  try {
    await fetch(`${API_BASE}/consumeRecipe`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ userId, recipeId }),
    });
  } catch (err) {
    console.error("Failed to consume recipe:", err);
  }
};

// ================== Nutrition ==================
export const getNutrition = async (recipeText) => {
  try {
    const res = await fetch(`${API_BASE}/getNutrition`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ recipeText }),
    });
    const data = await res.json();
    return data.nutritionInfo;
  } catch (err) {
    console.error("Failed to fetch nutrition info:", err);
    return "";
  }
};

// ================== Expiring Ingredients ==================
export const getExpiringIngredients = async (userId) => {
  try {
    const res = await fetch(`${API_BASE}/expiringIngredients/${userId}`);
    return await res.json();
  } catch (err) {
    console.error("Failed to fetch expiring ingredients:", err);
    return [];
  }
};

// ================== Analytics ==================
export const getAnalytics = async (userId) => {
  try {
    const res = await fetch(`${API_BASE}/analytics/${userId}`);
    return await res.json();
  } catch (err) {
    console.error("Failed to fetch analytics:", err);
    return { used: [], wasted: [] };
  }
};