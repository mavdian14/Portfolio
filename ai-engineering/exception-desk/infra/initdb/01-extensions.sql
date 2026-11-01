-- Runs once, on first initialisation of the database volume.
--
-- pgvector is installed here rather than in an Alembic migration: extension
-- provisioning is an infrastructure concern and migrations describe application
-- schema. Keeping them apart means the app migrates cleanly against any Postgres,
-- and the M2 RAG project finds the extension already present.
--
-- Nothing in this project queries a vector column yet. The extension is installed
-- and left alone — an unused dependency is a smell, an unprovisioned one is a bug.

CREATE EXTENSION IF NOT EXISTS vector;

-- Useful for the queue's ORDER BY available_at once it has real volume.
-- gen_random_uuid() is built into PostgreSQL 13+, so no pgcrypto needed.
