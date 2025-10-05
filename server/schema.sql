-- USERS
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    email TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- GLOBAL INGREDIENTS
CREATE TABLE ingredients (
    ingredient_id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    category TEXT
);

-- USER INVENTORY
CREATE TABLE user_inventory (
    inventory_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id) ON DELETE CASCADE,
    ingredient_id INT REFERENCES ingredients(ingredient_id),
    quantity REAL DEFAULT 1.0,
    unit TEXT DEFAULT 'kg',
    expiration_date DATE,
    used BOOLEAN DEFAULT FALSE,
    wasted BOOLEAN DEFAULT FALSE,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- RECIPES
CREATE TABLE recipes (
    recipe_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    instructions TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- RECIPE INGREDIENTS
CREATE TABLE recipe_ingredients (
    recipe_ingredient_id SERIAL PRIMARY KEY,
    recipe_id INT REFERENCES recipes(recipe_id) ON DELETE CASCADE,
    ingredient_id INT REFERENCES ingredients(ingredient_id),
    quantity REAL DEFAULT 1.0,
    unit TEXT DEFAULT 'kg'
);

-- Add user preferences
ALTER TABLE users ADD COLUMN dietary_preferences TEXT;
ALTER TABLE user_inventory ADD COLUMN expiration_date DATE;

-- Track recipe history
CREATE TABLE user_recipe_history (
    user_id INT REFERENCES users(user_id),
    recipe_id INT REFERENCES recipes(recipe_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);