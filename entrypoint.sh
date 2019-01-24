#!/bin/bash

python /src/labman_ud/labman_ud/manage.py collectstatic --noinput --settings=labman_ud.settings.settings
./wait-for-it/wait-for-it.sh ${DATABASE_HOST}:${DATABASE_PORT} && python  /src/labman_ud/labman_ud/manage.py runserver --settings=labman_ud.settings.settings 0.0.0.0:8000