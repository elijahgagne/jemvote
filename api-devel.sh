#!/bin/bash

. ENV.sh

gunicorn --access-logfile - --error-logfile - --log-level=info --reload --workers $WORKERS -b 0.0.0.0:5000 api:api
