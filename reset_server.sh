#!/usr/bin/env bash
# Remove old database
# Then setup, populate db
# Then start the server
rm wildsight.db
python3 database_setup.py
python3 populate_db.py
python3 wildsight.py
