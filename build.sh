#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt

mkdir -p data
python manage.py collectstatic --noinput
python manage.py migrate --noinput
