import React, { useEffect, useState } from "react";
import FridgeView from "./components/FridgeView";
import RecipesView from "./components/RecipesView";
import { getIngredients } from "./api";
import './App.css';

export default function App() {
  const userId = 1;
  const [ingredients, setIngredients] = useState([]);

  const refreshIngredients = async () => {
    setIngredients(await getIngredients(userId));
  };

  useEffect(() => {
    refreshIngredients();
  }, []);

  return (
    <div className="container">
      <h1 className="header">🍳 EcoChef</h1>
      <FridgeView userId={userId} ingredients={ingredients} refreshIngredients={refreshIngredients} />
      <RecipesView userId={userId} refreshIngredients={refreshIngredients} />
    </div>
  );
}