#!/usr/bin/env bash
# Exit on error
set -o errexit

echo "Installing dependencies using python3..."
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
