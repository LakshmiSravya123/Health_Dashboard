#!/bin/bash
# Simple script to run the dashboard

cd "$(dirname "$0")"
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python src/dashboard/app.py
