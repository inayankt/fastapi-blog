#!/bin/sh
set -e

psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB" <<EOSQL
DO \$\$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = '${BLOG_USER}') THEN
    CREATE ROLE ${BLOG_USER} WITH LOGIN PASSWORD '${BLOG_PASSWORD}';
  END IF;

  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'testuser') THEN
    CREATE ROLE testuser WITH LOGIN PASSWORD 'testpass';
  END IF;
END
\$\$;

SELECT 'CREATE DATABASE ${BLOG_DB} OWNER ${BLOG_USER}'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '${BLOG_DB}')\gexec

SELECT 'CREATE DATABASE blog_test OWNER testuser'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'blog_test')\gexec
EOSQL