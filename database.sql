/* =========================================
   1️⃣ CREATE DATABASE
========================================= */
IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'blood_bank')
BEGIN
    CREATE DATABASE blood_bank;
END

-- =========================
-- CREATE DATABASE
-- =========================
CREATE DATABASE blood_bank;
GO
USE blood_bank;
GO

-- =========================
-- DONORS TABLE
-- =========================
CREATE TABLE donors (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    age INT NOT NULL,
    blood_group VARCHAR(5) NOT NULL,
    contact VARCHAR(15) NOT NULL,
    created_at DATETIME DEFAULT GETDATE()
);

-- =========================
-- BLOOD STOCK TABLE
-- =========================
drop table blood_stock
CREATE TABLE blood_stock (
    blood_group VARCHAR(5) PRIMARY KEY,
    units INT NOT NULL CHECK (units >= 0),
    amount INT NOT NULL
);

-- =========================
-- MONTHLY DONATIONS TABLE
-- =========================
CREATE TABLE monthly_donations (
    id INT IDENTITY(1,1) PRIMARY KEY,
    blood_group VARCHAR(5) NOT NULL,
    units INT NOT NULL,
    donation_date DATETIME DEFAULT GETDATE()
);

-- =========================
-- MONTHLY ISSUED TABLE
-- =========================
CREATE TABLE monthly_issued (
    id INT IDENTITY(1,1) PRIMARY KEY,
    blood_group VARCHAR(5) NOT NULL,
    units INT NOT NULL,
    total_amount INT NOT NULL,
    issue_date DATETIME DEFAULT GETDATE()
);

-- =========================
-- DEFAULT BLOOD PRICES
-- =========================
INSERT INTO blood_stock (blood_group, units, amount) VALUES
('A+', 10, 1200),
('A-', 20, 1500),
('B+', 8, 1200),
('B-', 9, 1500),
('AB+', 12, 1800),
('AB-', 17, 2200),
('O+', 18, 1000),
('O-', 99, 2000);


USE blood_bank;
GO

SELECT * FROM donors;
GO

SELECT * FROM blood_stock;
GO


SELECT * FROM monthly_donations;
GO


SELECT * FROM monthly_issued;
GO
