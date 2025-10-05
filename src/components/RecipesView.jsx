import React, { useState, useEffect } from 'react';
import './RecipesView.css';

export default function RecipesView({ userId, refreshIngredients }) {
  const [recipes, setRecipes] = useState([]);

  useEffect(() => {
    // Fetch recipes from backend
    const fetchRecipes = async () => {
      try {
        const response = await fetch(`http://localhost:5000/api/recipes/${userId}`);
        const data = await response.json();
        setRecipes(data);
      } catch (error) {
        console.error('Error fetching recipes:', error);
        setRecipes([]);
      }
    };

    fetchRecipes();
  }, [userId]);

  return (
    <div className="recipes-container">
      <h2 className="recipes-header">Recommended Recipes</h2>
      <div className="recipes-list">
        {recipes.length > 0 ? (
          recipes.map((recipe, index) => (
            <div key={index} className="recipe-card">
              <h3>{recipe.name}</h3>
              <p>{recipe.description}</p>
            </div>
          ))
        ) : (
          <p>No recipes available yet. Add more ingredients to get recommendations!</p>
        )}
      </div>
    </div>
  );
}