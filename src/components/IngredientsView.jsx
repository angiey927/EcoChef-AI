import React, { useState, useEffect } from "react";

function IngredientsManager({ userId }) {
  const [ingredients, setIngredients] = useState([]);
  const [newIngredient, setNewIngredient] = useState({
    name: "",
    category: "",
    quantity: 1,
    unit: "unit",
  });
  const [message, setMessage] = useState("");

  // Fetch current inventory
  const fetchIngredients = async () => {
    try {
      const res = await fetch(`http://localhost:5000/api/ingredients/${userId}`);
      const data = await res.json();
      setIngredients(data);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchIngredients();
  }, []);

  // Add new ingredient
  const handleAdd = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch("http://localhost:5000/api/addIngredient", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ userId, ...newIngredient }),
      });

      if (!res.ok) throw new Error("Failed to add ingredient");

      setMessage(await res.text());
      setNewIngredient({ name: "", category: "", quantity: 1, unit: "unit" });
      fetchIngredients();
    } catch (err) {
      console.error(err);
      setMessage("Error adding ingredient");
    }
  };

  // Update ingredient quantity
  const handleUpdate = async (ingredient) => {
    try {
      const res = await fetch(`http://localhost:5000/api/addIngredient`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          userId,
          name: ingredient.name,
          category: ingredient.category,
          quantity: ingredient.quantity,
          unit: ingredient.unit,
        }),
      });

      if (!res.ok) throw new Error("Failed to update ingredient");
      setMessage(await res.text());
      fetchIngredients();
    } catch (err) {
      console.error(err);
      setMessage("Error updating ingredient");
    }
  };

  // Remove ingredient
  const handleRemove = async (ingredient) => {
    try {
      const res = await fetch(`http://localhost:5000/api/removeIngredient`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ userId, name: ingredient.name }),
      });

      if (!res.ok) throw new Error("Failed to remove ingredient");
      setMessage(await res.text());
      fetchIngredients();
    } catch (err) {
      console.error(err);
      setMessage("Error removing ingredient");
    }
  };

  return (
    <div style={{ maxWidth: 600, margin: "auto", padding: 20 }}>
      <h2>Ingredients Inventory</h2>
      {message && <p>{message}</p>}

      {/* Add Ingredient Form */}
      <form onSubmit={handleAdd} style={{ marginBottom: 20 }}>
        <input
          type="text"
          placeholder="Name"
          value={newIngredient.name}
          onChange={(e) => setNewIngredient({ ...newIngredient, name: e.target.value })}
          required
        />
        <input
          type="text"
          placeholder="Category"
          value={newIngredient.category}
          onChange={(e) => setNewIngredient({ ...newIngredient, category: e.target.value })}
          required
        />
        <input
          type="number"
          min="0"
          step="0.1"
          placeholder="Quantity"
          value={newIngredient.quantity}
          onChange={(e) => setNewIngredient({ ...newIngredient, quantity: parseFloat(e.target.value) })}
          required
        />
        <input
          type="text"
          placeholder="Unit"
          value={newIngredient.unit}
          onChange={(e) => setNewIngredient({ ...newIngredient, unit: e.target.value })}
          required
        />
        <button type="submit">Add Ingredient</button>
      </form>

      {/* Current Ingredients List */}
      <table border="1" cellPadding="5" style={{ width: "100%", textAlign: "left" }}>
        <thead>
          <tr>
            <th>Name</th>
            <th>Category</th>
            <th>Quantity</th>
            <th>Unit</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {ingredients.map((ing, idx) => (
            <tr key={idx}>
              <td>{ing.name}</td>
              <td>{ing.category}</td>
              <td>
                <input
                  type="number"
                  value={ing.quantity}
                  onChange={(e) => {
                    const newQuantity = parseFloat(e.target.value);
                    setIngredients((prev) =>
                      prev.map((i, iIdx) => (iIdx === idx ? { ...i, quantity: newQuantity } : i))
                    );
                  }}
                  style={{ width: 60 }}
                />
              </td>
              <td>
                <input
                  type="text"
                  value={ing.unit}
                  onChange={(e) => {
                    const newUnit = e.target.value;
                    setIngredients((prev) =>
                      prev.map((i, iIdx) => (iIdx === idx ? { ...i, unit: newUnit } : i))
                    );
                  }}
                  style={{ width: 60 }}
                />
              </td>
              <td>
                <button onClick={() => handleUpdate(ing)}>Update</button>
                <button onClick={() => handleRemove(ing)} style={{ marginLeft: 5 }}>Remove</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

async function handleMadeThis(recipeId) {
  try {
    const res = await fetch("http://localhost:5000/api/consumeRecipe", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ userId: 1, recipeId }),
    });
    const msg = await res.text();
    console.log(msg);
    // Optionally refresh inventory or recipe suggestions here
  } catch (err) {
    console.error(err);
  }
}

export default IngredientsManager;