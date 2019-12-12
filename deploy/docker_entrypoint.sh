#!/usr/bin/env bash

service nginx start

gunicorn domain.app:api --name Reader --workers 3 --bind=unix:/var/www/reader/gunicorn.sock --log-level=debug --log-file=- --timeout $GUNICORN_TIMEOUT
