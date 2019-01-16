#!/bin/bash

cd labman_ud
python manage.py runserver --settings=labman_ud.settings.settings 0.0.0.0:8000
python manage.py collectstatic --settings=labman_ud.settings.settings