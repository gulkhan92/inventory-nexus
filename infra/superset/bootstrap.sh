#!/usr/bin/env bash
set -euo pipefail

superset db upgrade

superset fab create-admin \
  --username "$SUPERSET_ADMIN_USERNAME" \
  --firstname Inventory \
  --lastname Nexus \
  --email "$SUPERSET_ADMIN_EMAIL" \
  --password "$SUPERSET_ADMIN_PASSWORD" || true

superset init
