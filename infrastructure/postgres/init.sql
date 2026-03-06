-- ColdCase AI Database Initialization
-- Creates separate schemas for each service

CREATE SCHEMA IF NOT EXISTS gateway;
CREATE SCHEMA IF NOT EXISTS users;
CREATE SCHEMA IF NOT EXISTS ai_service;

-- Grant permissions
GRANT ALL PRIVILEGES ON SCHEMA gateway TO coldcase;
GRANT ALL PRIVILEGES ON SCHEMA users TO coldcase;
GRANT ALL PRIVILEGES ON SCHEMA ai_service TO coldcase;
