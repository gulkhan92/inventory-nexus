# Inventory Nexus Analytics SQL

This folder is reserved for database-level analytics assets used by BI tools such as Apache Superset.

The current application creates the analytics schema and views through `backend/app/services/reporting.py` during seeding. Keeping this folder makes the intended production migration path explicit: move those view definitions into Alembic or SQL migration files once the schema is managed through migrations.
