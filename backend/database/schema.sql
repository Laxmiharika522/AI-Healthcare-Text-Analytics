-- AI Healthcare Text Analytics Platform - MySQL Schema
-- Run this in MySQL before starting the app, OR let seed_data.py auto-create it.

CREATE TABLE IF NOT EXISTS Patients (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(255) NOT NULL,
    age         INT,
    gender      VARCHAR(20),
    blood_type  VARCHAR(10),
    admission_date VARCHAR(20),
    discharge_date VARCHAR(20),
    contact     VARCHAR(50),
    insurance_id VARCHAR(50)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS Clinical_Notes (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    patient_id  INT,
    note_text   TEXT NOT NULL,
    created_at  DATETIME DEFAULT NOW(),
    doctor_name VARCHAR(100),
    department  VARCHAR(100),
    diagnosis   VARCHAR(200),
    severity    VARCHAR(20),
    note_type   VARCHAR(50),
    FOREIGN KEY (patient_id) REFERENCES Patients(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS Diseases (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    disease_name VARCHAR(200) NOT NULL,
    symptoms     TEXT,
    severity     VARCHAR(20),
    category     VARCHAR(100),
    icd_code     VARCHAR(20),
    description  TEXT,
    treatment    TEXT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS Research_Papers (
    id             INT AUTO_INCREMENT PRIMARY KEY,
    title          TEXT NOT NULL,
    abstract       TEXT,
    authors        TEXT,
    journal        VARCHAR(255),
    year           INT,
    keywords       TEXT,
    doi            VARCHAR(100),
    citation_count INT DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
