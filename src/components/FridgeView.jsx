import React, { useEffect, useState } from "react";
import { getIngredients, addIngredient } from "../api";
import './FridgeView.css';

export default function FridgeView({ userId, refreshIngredients }) {
  const [ingredients, setIngredients] = useState([]);
  const [newIngredient, setNewIngredient] = useState({
    name: "",
    category: "Other",
    quantity: 1,
    unit: "unit"
  });

  const fetchIngredients = async () => {
    const data = await getIngredients(userId);
    setIngredients(data);
  };

  useEffect(() => {
    fetchIngredients();
  }, [userId]);

  const handleAdd = async (e) => {
    e.preventDefault();
    if (!newIngredient.name) return;

    await addIngredient({ ...newIngredient, userId });
    await fetchIngredients();
    if (refreshIngredients) refreshIngredients();
    
    // Reset form
    setNewIngredient({
      name: "",
      category: "Other",
      quantity: 1,
      unit: "unit"
    });
  };

  const categories = [
    "Vegetable",
    "Fruit",
    "Meat",
    "Dairy",
    "Grain",
    "Spice",
    "Other"
  ];

  const units = [
    "unit",
    "g",
    "kg",
    "ml",
    "L",
    "cup",
    "tbsp",
    "tsp",
    "bunch",
    "slice"
  ];

  return (
    <div className="fridge-container">
      <h2 className="fridge-header">Your Fridge</h2>
      <div className="ingredients-list">
        {ingredients.map((item, index) => (
          <div key={index} className="ingredient">
            {item.name} ({item.quantity} {item.unit})
          </div>
        ))}
      </div>
      <form className="add-ingredient-form" onSubmit={handleAdd}>
        <input
          type="text"
          placeholder="Ingredient name"
          value={newIngredient.name}
          onChange={(e) => setNewIngredient({...newIngredient, name: e.target.value})}
          className="ingredient-input"
        />
        <select
          value={newIngredient.category}
          onChange={(e) => setNewIngredient({...newIngredient, category: e.target.value})}
          className="ingredient-select"
        >
          {categories.map(cat => (
            <option key={cat} value={cat}>{cat}</option>
          ))}
        </select>
        <input
          type="number"
          min="1"
          value={newIngredient.quantity}
          onChange={(e) => setNewIngredient({...newIngredient, quantity: parseInt(e.target.value) || 1})}
          className="quantity-input"
        />
        <select
          value={newIngredient.unit}
          onChange={(e) => setNewIngredient({...newIngredient, unit: e.target.value})}
          className="unit-select"
        >
          {units.map(unit => (
            <option key={unit} value={unit}>{unit}</option>
          ))}
        </select>
        <button type="submit" className="add-button">
          Add Ingredient
        </button>
      </form>
    </div>
  );
}