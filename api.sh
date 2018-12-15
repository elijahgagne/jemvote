#!/bin/bash

WORKERS=${WORKERS:-4}

gunicorn --access-logfile - --error-logfile - --log-level=info --workers $WORKERS -b 0.0.0.0:5000 api:api
