-- 1. Tabel pentru categoriile de decorațiuni
CREATE TABLE Categories (
    category_id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL
);

-- 2. Tabel pentru regiuni
CREATE TABLE Regions (
    region_id SERIAL PRIMARY KEY,
    name VARCHAR(50),
    country VARCHAR(50)
);

-- 3. Tabel pentru perioade de timp
CREATE TABLE TimePeriods (
    period_id SERIAL PRIMARY KEY,
    period_name VARCHAR(20),
    start_date DATE,
    end_date DATE
);

-- 4. Tabel pentru decorațiuni, legat de categorii
CREATE TABLE Decorations (
    decoration_id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    model VARCHAR(50),
    category_id INT REFERENCES Categories(category_id) ON DELETE CASCADE,
    price DECIMAL(10, 2)
);

-- 5. Tabel pentru profilul clienților, legat de regiuni
CREATE TABLE Customers (
    customer_id SERIAL PRIMARY KEY,
    occupation VARCHAR(50),
    income DECIMAL(10, 2),
    age INT,
    marital_status VARCHAR(20),
    region_id INT REFERENCES Regions(region_id) ON DELETE SET NULL
);

-- 6. Tabel pentru preferințele clienților, legat de clienți și categorii
CREATE TABLE CustomerPreferences (
    preference_id SERIAL PRIMARY KEY,
    customer_id INT REFERENCES Customers(customer_id) ON DELETE CASCADE,
    category_id INT REFERENCES Categories(category_id) ON DELETE CASCADE,
    preference_level INT CHECK (preference_level BETWEEN 1 AND 5)
);

-- 7. Tabel pentru vânzări, legat de decorațiuni, clienți și perioade de timp
CREATE TABLE Sales (
    sale_id SERIAL PRIMARY KEY,
    decoration_id INT REFERENCES Decorations(decoration_id) ON DELETE CASCADE,
    customer_id INT REFERENCES Customers(customer_id) ON DELETE SET NULL,
    sale_date DATE,
    quantity INT,
    time_period_id INT REFERENCES TimePeriods(period_id) ON DELETE SET NULL
);

-- 8. Tabel pentru modificările de preț, legat de decorațiuni
CREATE TABLE PriceChanges (
    price_change_id SERIAL PRIMARY KEY,
    decoration_id INT REFERENCES Decorations(decoration_id) ON DELETE CASCADE,
    date_of_change DATE,
    old_price DECIMAL(10, 2),
    new_price DECIMAL(10, 2),
    change_reason VARCHAR(100)
);
