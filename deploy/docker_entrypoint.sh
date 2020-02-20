#!/usr/bin/env bash

service nginx start

gunicorn wsgi:process_memory_app --name Memory --workers 1 --bind=unix:/var/www/memory/gunicorn.sock --log-level=debug --log-file=- --timeout $GUNICORN_TIMEOUT
