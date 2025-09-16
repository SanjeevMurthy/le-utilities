#!/bin/bash

# ==============================================================================
# macOS Development Environment Setup Script
#
# This script automates the setup of a common development environment on macOS
# by installing and verifying essential tools using Homebrew.
#
# What it does:
# 1. Checks if Homebrew is installed. If not, it installs it. If it is,
#    it updates it.
# 2. Installs a list of essential command-line tools and applications quietly.
# 3. Runs everything in a non-interactive mode, showing progress.
# 4. At the end, it lists the versions of all installed packages to verify
#    the setup was successful.
# ==============================================================================

# --- Helper Functions for Colored Output ---
# Adds a bit of flair and makes the output easier to read.
echo_info() {
    # Blue color for informational messages
    printf "\n\033[1;34m%s\033[0m\n" "$1"
}

echo_success() {
    # Green color for success messages
    printf "\033[1;32m✅ %s\033[0m\n" "$1"
}

echo_error() {
    # Red color for error messages
    printf "\033[1;31m❌ ERROR: %s\033[0m\n" "$1" >&2
}

# --- Main Execution ---

echo_info "🚀 Starting the macOS development environment setup..."

# Step 1: Check, Install, or Update Homebrew
# Homebrew is the package manager we'll use for all installations.
echo_info "Checking for Homebrew..."
if ! command -v brew &>/dev/null; then
    echo "Homebrew not found. Installing now..."
    # Install Homebrew non-interactively
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    
    # Add Homebrew to the PATH for the current script session.
    # This is necessary because the installation script doesn't update the current shell's environment.
    (echo; echo 'eval "$(/opt/homebrew/bin/brew shellenv)"') >> ~/.zprofile
    eval "$(/opt/homebrew/bin/brew shellenv)"

    echo_success "Homebrew installed successfully."
else
    echo "Homebrew is already installed. Updating Homebrew..."
    brew update
    echo_success "Homebrew updated."
fi

# Step 2: Define the list of packages to install
# Formulae are command-line tools. Casks are GUI applications.
formulae=(
    "git"
    "minikube"
    "terraform"
    "azure-cli"
    "awscli"
    "python"
)

casks=(
    "docker" # Docker Desktop for Mac
)

# Step 3: Install all packages
echo_info "Installing packages. This might take a while..."

for formula in "${formulae[@]}"; do
    echo "Starting installing ${formula}..."
    if brew install --quiet "${formula}"; then
        echo_success "Successfully installed ${formula}."
    else
        echo_error "Failed to install ${formula}. Please run 'brew install ${formula}' manually to debug."
    fi
done

for cask in "${casks[@]}"; do
    echo "Starting installing ${cask}..."
    if brew install --cask --quiet "${cask}"; then
        echo_success "Successfully installed ${cask}."
    else
        echo_error "Failed to install ${cask}. Please run 'brew install --cask ${cask}' manually to debug."
    fi
done

echo_success "All packages have been processed."

# Step 4: List versions of installed packages to verify installation
echo_info "✅ Setup complete! Verifying installations..."
echo "-------------------------------------------------"
echo "Installed Package Versions:"
echo "-------------------------------------------------"

# A helper function to neatly print the name and version of a tool
print_version() {
    local tool_name=$1
    local version_command=$2
    local version_output

    if command -v "$tool_name" &>/dev/null; then
        # Execute the version command and capture the output
        version_output=$(eval "$version_command" 2>&1)
        # Print the tool name and its version output, formatted nicely
        printf "  %-12s %s\n" "$tool_name:" "$version_output"
    else
        printf "  %-12s Not found\n" "$tool_name:"
    fi
}

# Call the function for each tool
print_version "git" "git --version"
print_version "docker" "docker --version"
print_version "minikube" "minikube version --short"
print_version "terraform" "terraform -version | head -n 1"
print_version "az" "az --version | head -n 1"
print_version "aws" "aws --version | head -n 1"
print_version "python3" "python3 --version"

echo "-------------------------------------------------"
echo_info "🎉 Your development environment is ready!"
echo "NOTE: You may need to start Docker Desktop manually for the first time to accept the terms of service."