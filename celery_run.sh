#!/bin/bash

celery -A run.celery worker --loglevel=info
