#!/bin/bash

# Ensures that the database is available & Initialize database
flask --app ping_init run

# Start SCISTagram
echo "Starting SCISTagram"
exec  gunicorn -b '0.0.0.0:8000' -w 3 --access-logfile=- 'app:app'