#!/bin/bash

# ==============================================================================
# Powerlevel10k Theme Setup Script for macOS
#
# This script automates the installation of the Powerlevel10k theme for Zsh,
# including all its dependencies like Oh My Zsh and the required fonts.
#
# What it does:
# 1. Checks and installs/updates Homebrew.
# 2. Installs Zsh.
# 3. Installs the recommended Meslo Nerd Font.
# 4. Installs Oh My Zsh (if not already present).
# 5. Clones the Powerlevel10k theme into the Oh My Zsh themes directory.
# 6. Sets Powerlevel10k as the default theme in your .zshrc file.
# 7. Provides clear instructions for the final manual configuration steps.
# ==============================================================================

# --- Helper Functions for Colored Output ---
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

echo_info "🚀 Starting the Powerlevel10k theme setup..."

# Step 1: Check, Install, or Update Homebrew
echo_info "Checking for Homebrew..."
if ! command -v brew &>/dev/null; then
    echo "Homebrew not found. Installing now..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    
    (echo; echo 'eval "$(/opt/homebrew/bin/brew shellenv)"') >> ~/.zprofile
    eval "$(/opt/homebrew/bin/brew shellenv)"

    echo_success "Homebrew installed successfully."
else
    echo "Homebrew is already installed. Updating..."
    brew update >/dev/null 2>&1
    echo_success "Homebrew updated."
fi

# Step 2: Install Dependencies (Zsh and Fonts)
echo_info "Installing dependencies..."

# Install Zsh
echo "Starting installing zsh..."
if brew install --quiet "zsh"; then
    echo_success "Successfully installed zsh."
else
    echo_error "Failed to install zsh."
fi

# Install recommended fonts
echo_info "Installing Powerlevel10k recommended fonts..."
echo "Tapping homebrew/cask-fonts..."
brew tap homebrew/cask-fonts >/dev/null 2>&1

echo "Starting installing font-meslo-lg-nerd-font..."
if brew install --cask --quiet "font-meslo-lg-nerd-font"; then
    echo_success "Successfully installed font-meslo-lg-nerd-font."
else
    echo_error "Failed to install font-meslo-lg-nerd-font."
fi


# Step 3: Install Powerlevel10k and its dependencies
echo_info "Setting up Powerlevel10k theme..."

# Install Oh My Zsh if not already installed
if [ ! -d "$HOME/.oh-my-zsh" ]; then
    echo "Starting installing Oh My Zsh..."
    # Using --unattended will not change the default shell or run zsh
    sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended >/dev/null 2>&1
    echo_success "Successfully installed Oh My Zsh."
else
    echo "Oh My Zsh is already installed."
fi

# Install Powerlevel10k theme if not already installed
P10K_DIR="${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/themes/powerlevel10k"
if [ ! -d "$P10K_DIR" ]; then
    echo "Starting installing Powerlevel10k theme..."
    git clone --depth=1 https://github.com/romkatv/powerlevel10k.git "$P10K_DIR" >/dev/null 2>&1
    echo_success "Successfully installed Powerlevel10k theme."
else
    echo "Powerlevel10k theme is already installed. Updating..."
    (cd "$P10K_DIR" && git pull) >/dev/null 2>&1
    echo_success "Powerlevel10k updated."
fi

# Step 4: Configure Zsh to use Powerlevel10k
# Set Zsh theme to Powerlevel10k in .zshrc
if [ -f "$HOME/.zshrc" ]; then
    echo "Setting ZSH_THEME to powerlevel10k/powerlevel10k in .zshrc..."
    # Use sed to replace the theme. Create a backup (.zshrc.bak)
    sed -i.bak 's/^ZSH_THEME=".*"/ZSH_THEME="powerlevel10k\/powerlevel10k"/' "$HOME/.zshrc"
    echo_success "ZSH_THEME has been set."
else
    echo_error ".zshrc not found. Cannot set ZSH_THEME. Please ensure Oh My Zsh is installed correctly."
fi

echo "-------------------------------------------------"
echo_info "🎉 Powerlevel10k setup script finished!"
echo_info "⚠️ IMPORTANT FINAL STEPS ⚠️"
echo "1. Open your terminal's preferences (e.g., Terminal > Settings or iTerm2 > Profiles > Text)."
echo "2. Change the font for your profile to 'MesloLGS NF'."
echo "3. Restart your terminal completely (Cmd+Q and reopen)."
echo "4. The first time you open the new terminal, the Powerlevel10k configuration wizard should start automatically."
echo "   If it doesn't, run 'p10k configure' to start it manually."
echo "-------------------------------------------------"
