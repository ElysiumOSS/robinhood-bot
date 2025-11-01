#!/bin/sh
# initialize.sh

# --- Virtual Environment and Dependency Installation (No Changes Here) ---
if [ ! -d "env" ]; then
    echo "Creating virtual environment: env"
    python3 -m venv env
    source env/bin/activate
    echo "Upgrading pip..."
    python3 -m pip install --upgrade pip
    echo "Installing dependencies..."
    pip install -r requirements.txt
    echo "Installing pre-commit hooks..."
    pre-commit install
    echo "Done!"
fi

# --- Secure .env File Creation ---
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    # Copy the template to a new .env file for the user to fill out.
    cp .env.example .env
    echo "Done! Please edit the .env file with your credentials."
else
    echo ".env file already exists. Skipping creation."
fi