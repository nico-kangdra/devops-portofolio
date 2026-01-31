-- THIS CODE FOR INITIALIZE
-- JUST COPY TO YOUR SQL AND RUN IT

CREATE DATABASE govote;
USE govote;
CREATE TABLE users (
    nik VARCHAR(255) PRIMARY KEY,
    nama_lengkap VARCHAR(100) NOT NULL,
    nama_ibu_kandung VARCHAR(100) NOT NULL,
    vote INT NULL
);
INSERT INTO users VALUES (123,'admin','Admin123',NULL);