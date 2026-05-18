DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'smartforest') THEN
    CREATE ROLE smartforest WITH LOGIN PASSWORD 'SmartForest2026!';
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = 'fire_detection') THEN
    CREATE DATABASE fire_detection OWNER smartforest;
  END IF;
END
$$;
