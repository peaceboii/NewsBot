#!/bin/bash
set -e

pip install --upgrade pip
pip install -r requirements.txt
python manage.py migrate --no-input
python manage.py collectstatic --no-input
