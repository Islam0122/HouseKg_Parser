#!/usr/bin/env bash
set -e
exec celery -A project beat -l info