#!/bin/bash
set -e

echo "Starting server initialization..."

# 1. Collectstatic using production settings
export DJANGO_SETTINGS_MODULE=oncoscience.settings.prod
python manage.py collectstatic --noinput

# 2. Check if the database needs migration from SQLite
# If PostgreSQL has 0 users, it means it's a fresh database!
echo "Running migrations for PostgreSQL..."
python manage.py migrate --noinput

USER_COUNT=$(python manage.py shell -c "from django.contrib.auth import get_user_model; print(get_user_model().objects.count())" 2>/dev/null || echo "0")

if [ "$USER_COUNT" -eq "0" ] && [ -f "/app/db.sqlite3" ]; then
    echo "================================================="
    echo "PostgreSQL is empty. Migrating data from SQLite..."
    echo "================================================="
    
    # Dumpdata from SQLite
    export DJANGO_SETTINGS_MODULE=oncoscience.settings.sqlite
    echo "Dumping SQLite data to /tmp/datadump.json..."
    python manage.py dumpdata --natural-foreign --natural-primary -e contenttypes -e auth.Permission -e admin.logentry --indent 4 > /tmp/datadump.json
    
    if [ -s "/tmp/datadump.json" ]; then
        # Loaddata into PostgreSQL
        export DJANGO_SETTINGS_MODULE=oncoscience.settings.prod
        echo "Loading JSON into PostgreSQL..."
        python manage.py loaddata /tmp/datadump.json
        echo "Data migration complete!"
    else
        echo "SQLite dump failed or was empty."
    fi
else
    echo "PostgreSQL already has data (Users: $USER_COUNT). Skipping migration."
fi

# Ensure production settings are active for Gunicorn
export DJANGO_SETTINGS_MODULE=oncoscience.settings.prod
exec gunicorn --bind 0.0.0.0:8000 --workers 3 --timeout 120 oncoscience.wsgi:application
