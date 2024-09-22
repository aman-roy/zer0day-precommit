#!/bin/bash

# Check if the user is running in a Git repository
if [ ! -d .git ]; then
    echo "This is not a Git repository. Please run this script in the root of a Git repository."
    exit 1
fi

# Add the sbom-precommit repo as a submodule (this step assumes your repository is public)
if [ ! -d "sbom-precommit" ]; then
    echo "Adding sbom-precommit repository as a submodule..."
    git submodule add https://github.com/yourusername/sbom-precommit.git sbom-precommit
    git submodule init
    git submodule update
else
    echo "sbom-precommit already exists. Skipping submodule setup."
fi

# Copy the pre-commit hook from the submodule to the .git/hooks directory
HOOK_FILE=".git/hooks/pre-commit"
if [ -f "$HOOK_FILE" ]; then
    echo "A pre-commit hook already exists. Do you want to overwrite it? (y/n)"
    read answer
    if [ "$answer" != "${answer#[Yy]}" ]; then
        cp sbom-precommit/pre-commit.sample "$HOOK_FILE"
        chmod +x "$HOOK_FILE"
        echo "Pre-commit hook installed."
    else
        echo "Pre-commit hook not installed."
    fi
else
    cp sbom-precommit/pre-commit.sample "$HOOK_FILE"
    chmod +x "$HOOK_FILE"
    echo "Pre-commit hook installed."
fi

# Ensure Syft is installed
if ! command -v syft &> /dev/null
then
    echo "Syft could not be found. Installing Syft..."
    curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | sh
else
    echo "Syft is already installed."
fi

echo "Pre-commit hook setup is complete."