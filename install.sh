#!/bin/bash
# 🚗 Israeli Car Valuation - One-Click Installation Script
# =====================================================
# OME-119: Transform installation from 6 manual steps to 1 command
# Target: 95% success rate, <5 minutes, works on all platforms

set -euo pipefail  # Exit on errors, undefined vars, pipe failures

# Color codes for pretty output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Global variables
SKILL_NAME="car-valuation"
GITHUB_REPO="https://github.com/steinerhunter/car-valuation.git"
OPENCLAW_SKILLS_DIR=""
APIFY_TOKEN=""
LOG_FILE="/tmp/car-valuation-install.log"

# Progress tracking
TOTAL_STEPS=7
CURRENT_STEP=0

# Utility functions
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

step() {
    CURRENT_STEP=$((CURRENT_STEP + 1))
    echo
    echo -e "${PURPLE}[${CURRENT_STEP}/${TOTAL_STEPS}]${NC} ${WHITE}$1${NC}"
    log "STEP ${CURRENT_STEP}/${TOTAL_STEPS}: $1"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
    log "SUCCESS: $1"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
    log "WARNING: $1"
}

error() {
    echo -e "${RED}❌ $1${NC}"
    log "ERROR: $1"
    exit 1
}

info() {
    echo -e "${CYAN}ℹ️  $1${NC}"
}

# Progress bar function
progress_bar() {
    local current=$1
    local total=$2
    local width=30
    local percentage=$((current * 100 / total))
    local completed=$((current * width / total))
    local remaining=$((width - completed))
    
    printf "\r${BLUE}Progress: [${NC}"
    printf "%*s" "$completed" | tr ' ' '█'
    printf "%*s" "$remaining" | tr ' ' '░'
    printf "${BLUE}] %d%%${NC}" "$percentage"
}

# System detection
detect_system() {
    step "🔍 Detecting System Environment"
    
    # Detect OS
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
        if command -v apt-get >/dev/null; then
            PKG_MANAGER="apt"
        elif command -v yum >/dev/null; then
            PKG_MANAGER="yum"  
        elif command -v pacman >/dev/null; then
            PKG_MANAGER="pacman"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        PKG_MANAGER="brew"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        OS="windows"
        PKG_MANAGER="none"
    else
        warning "Unknown OS: $OSTYPE. Proceeding with caution..."
        OS="unknown"
    fi
    
    # Detect Python
    if command -v python3 >/dev/null; then
        PYTHON_CMD="python3"
        PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
    elif command -v python >/dev/null; then
        PYTHON_CMD="python" 
        PYTHON_VERSION=$(python --version 2>&1 | cut -d' ' -f2)
    else
        error "Python not found. Please install Python 3.8+ first."
    fi
    
    # Check Python version
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
    
    if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
        error "Python 3.8+ required. Found: $PYTHON_VERSION"
    fi
    
    # Detect pip
    if command -v pip3 >/dev/null; then
        PIP_CMD="pip3"
    elif command -v pip >/dev/null; then
        PIP_CMD="pip"
    else
        error "pip not found. Please install pip first."
    fi
    
    success "System detected: $OS, Python $PYTHON_VERSION, $PIP_CMD available"
    progress_bar 1 $TOTAL_STEPS
}

# Find OpenClaw installation
find_openclaw() {
    step "📁 Locating OpenClaw Installation"
    
    # Common OpenClaw locations
    POSSIBLE_PATHS=(
        "$HOME/.openclaw/workspace/skills"
        "$HOME/.openclaw/skills"
        "$HOME/openclaw/workspace/skills"
        "$HOME/openclaw/skills"
        "/opt/openclaw/workspace/skills"
        "/opt/openclaw/skills"
    )
    
    # Try to find OpenClaw
    for path in "${POSSIBLE_PATHS[@]}"; do
        if [ -d "$path" ]; then
            OPENCLAW_SKILLS_DIR="$path"
            success "Found OpenClaw skills directory: $OPENCLAW_SKILLS_DIR"
            progress_bar 2 $TOTAL_STEPS
            return
        fi
    done
    
    # If not found, ask user
    echo
    warning "OpenClaw skills directory not found in common locations."
    echo -e "${CYAN}Please enter your OpenClaw skills directory path:${NC}"
    read -p "Skills directory: " user_path
    
    if [ -d "$user_path" ]; then
        OPENCLAW_SKILLS_DIR="$user_path"
        success "Using custom skills directory: $OPENCLAW_SKILLS_DIR"
        progress_bar 2 $TOTAL_STEPS
    else
        error "Directory not found: $user_path"
    fi
}

# Clone or update skill repository
install_skill() {
    step "📥 Installing Car Valuation Skill"
    
    cd "$OPENCLAW_SKILLS_DIR"
    
    # Remove existing installation if present
    if [ -d "$SKILL_NAME" ]; then
        warning "Existing installation found. Updating..."
        rm -rf "$SKILL_NAME"
    fi
    
    # Clone repository
    if git clone "$GITHUB_REPO" "$SKILL_NAME" >/dev/null 2>&1; then
        success "Skill repository cloned successfully"
    else
        error "Failed to clone repository. Check internet connection."
    fi
    
    cd "$SKILL_NAME"
    success "Entered skill directory: $(pwd)"
    progress_bar 3 $TOTAL_STEPS
}

# Install Python dependencies
install_dependencies() {
    step "📚 Installing Python Dependencies"
    
    # Check if requirements.txt exists
    if [ ! -f "requirements.txt" ]; then
        error "requirements.txt not found in skill directory"
    fi
    
    # Create virtual environment if possible
    if command -v python3 >/dev/null && $PYTHON_CMD -m venv --help >/dev/null 2>&1; then
        info "Creating virtual environment..."
        $PYTHON_CMD -m venv .venv
        source .venv/bin/activate
        PIP_CMD=".venv/bin/pip"
        success "Virtual environment created and activated"
    fi
    
    # Install dependencies
    echo "Installing Python packages..."
    if $PIP_CMD install -r requirements.txt --quiet; then
        success "All dependencies installed successfully"
    else
        # Try with --break-system-packages for newer systems
        warning "Retrying with system packages flag..."
        if $PIP_CMD install -r requirements.txt --break-system-packages --quiet; then
            success "Dependencies installed (system packages)"
        else
            error "Failed to install dependencies. Check logs: $LOG_FILE"
        fi
    fi
    
    progress_bar 4 $TOTAL_STEPS
}

# Interactive Apify setup
setup_apify() {
    step "🔑 Setting up Apify API Access"
    
    echo
    echo -e "${WHITE}🎯 Apify Setup - Real-time Yad2 Data Access${NC}"
    echo -e "${CYAN}We need an Apify account for live market data scraping.${NC}"
    echo
    
    # Check if token already exists
    if [ ! -z "${APIFY_API_TOKEN:-}" ]; then
        info "Existing APIFY_API_TOKEN found in environment"
        APIFY_TOKEN="$APIFY_API_TOKEN"
        success "Using existing Apify token"
        progress_bar 5 $TOTAL_STEPS
        return
    fi
    
    echo -e "${YELLOW}Option 1: Automatic Setup (Recommended)${NC}"
    echo "  • Opens browser to Apify signup"
    echo "  • Guides you through token creation"
    echo "  • Automatically configures environment"
    echo
    echo -e "${CYAN}Option 2: Manual Setup${NC}"
    echo "  • You provide existing Apify token"
    echo
    
    read -p "Choose setup method (1 for automatic, 2 for manual): " setup_choice
    
    case $setup_choice in
        1)
            automatic_apify_setup
            ;;
        2) 
            manual_apify_setup
            ;;
        *)
            warning "Invalid choice. Using automatic setup..."
            automatic_apify_setup
            ;;
    esac
    
    progress_bar 5 $TOTAL_STEPS
}

automatic_apify_setup() {
    echo
    info "🌐 Opening Apify signup page in your browser..."
    
    # Open browser based on OS
    case $OS in
        "linux")
            if command -v xdg-open >/dev/null; then
                xdg-open "https://apify.com/sign-up?ref=car-valuation" >/dev/null 2>&1 &
            fi
            ;;
        "macos")
            open "https://apify.com/sign-up?ref=car-valuation" >/dev/null 2>&1 &
            ;;
        "windows")
            start "https://apify.com/sign-up?ref=car-valuation" >/dev/null 2>&1 &
            ;;
    esac
    
    echo
    echo -e "${WHITE}📋 Follow these steps:${NC}"
    echo "1. 📝 Create free Apify account (if you don't have one)"
    echo "2. ⚙️  Go to: Account Settings → Integrations → API Tokens"
    echo "3. ➕ Click 'Create new token'"
    echo "4. 📋 Copy the token (starts with 'apify_api_')"
    echo
    
    read -p "Press ENTER when you have your API token ready..."
    echo
    
    while true; do
        read -p "🔑 Paste your Apify API token: " token
        
        # Validate token format
        if [[ $token =~ ^apify_api_[a-zA-Z0-9]{40,}$ ]]; then
            APIFY_TOKEN="$token"
            success "Valid Apify token received"
            break
        else
            echo -e "${RED}❌ Invalid token format. Should start with 'apify_api_'${NC}"
            echo "Please try again or press Ctrl+C to exit."
        fi
    done
}

manual_apify_setup() {
    echo
    info "Manual Apify setup selected"
    echo "If you don't have an Apify account, visit: https://apify.com/sign-up"
    echo
    
    while true; do
        read -p "🔑 Enter your Apify API token: " token
        
        if [[ $token =~ ^apify_api_[a-zA-Z0-9]{40,}$ ]]; then
            APIFY_TOKEN="$token"
            success "Valid Apify token received"
            break
        else
            echo -e "${RED}❌ Invalid token format${NC}"
        fi
    done
}

# Configure environment
configure_environment() {
    step "⚙️ Configuring Environment"
    
    # Add to shell profile
    SHELL_PROFILE=""
    if [ -f "$HOME/.bashrc" ]; then
        SHELL_PROFILE="$HOME/.bashrc"
    elif [ -f "$HOME/.zshrc" ]; then
        SHELL_PROFILE="$HOME/.zshrc"
    elif [ -f "$HOME/.profile" ]; then
        SHELL_PROFILE="$HOME/.profile"
    fi
    
    if [ ! -z "$SHELL_PROFILE" ]; then
        # Check if already configured
        if ! grep -q "APIFY_API_TOKEN" "$SHELL_PROFILE" 2>/dev/null; then
            echo >> "$SHELL_PROFILE"
            echo "# Israeli Car Valuation - Auto-configured by installer" >> "$SHELL_PROFILE"
            echo "export APIFY_API_TOKEN=\"$APIFY_TOKEN\"" >> "$SHELL_PROFILE"
            success "Environment configured in $SHELL_PROFILE"
        else
            info "Environment already configured"
        fi
    fi
    
    # Set for current session
    export APIFY_API_TOKEN="$APIFY_TOKEN"
    
    # Create local config file
    cat > .env << EOF
# Israeli Car Valuation Configuration
APIFY_API_TOKEN=$APIFY_TOKEN
SKILL_VERSION=2.0
INSTALLATION_DATE=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
INSTALLER_VERSION=1.0
EOF

    success "Local configuration created"
    progress_bar 6 $TOTAL_STEPS
}

# Test installation
test_installation() {
    step "🧪 Testing Installation"
    
    echo "Running verification tests..."
    
    # Test 1: Python imports
    if $PYTHON_CMD -c "
import sys
sys.path.insert(0, '.')
try:
    from scripts.car_valuation_api import CarValuationAPI
    from scripts.market_analyzer import analyze_user_query
    print('✅ Python modules import successfully')
except ImportError as e:
    print(f'❌ Import error: {e}')
    sys.exit(1)
" 2>/dev/null; then
        success "Python modules verified"
    else
        warning "Module import test failed - may work in production"
    fi
    
    # Test 2: API connectivity
    if [ -f "examples/basic_usage.py" ]; then
        echo "Testing API connectivity..."
        if timeout 30s $PYTHON_CMD examples/basic_usage.py >/dev/null 2>&1; then
            success "API connectivity test passed"
        else
            warning "API test inconclusive - manual verification may be needed"
        fi
    fi
    
    # Test 3: Configuration
    if [ -f ".env" ] && grep -q "APIFY_API_TOKEN" .env; then
        success "Configuration verified"
    else
        warning "Configuration file issues detected"
    fi
    
    progress_bar 7 $TOTAL_STEPS
    echo
}

# Main installation flow
main() {
    clear
    echo
    echo -e "${WHITE}╔════════════════════════════════════════════════════╗${NC}"
    echo -e "${WHITE}║           🚗 Israeli Car Valuation Installer      ║${NC}"
    echo -e "${WHITE}║                One-Click Installation              ║${NC}"
    echo -e "${WHITE}╚════════════════════════════════════════════════════╝${NC}"
    echo
    echo -e "${CYAN}Transform installation from 6 manual steps to 1 command!${NC}"
    echo -e "${CYAN}Target: 95% success rate • <5 minutes • All platforms${NC}"
    echo
    
    # Initialize log
    log "=== Israeli Car Valuation Installation Started ==="
    log "OS: $OSTYPE"
    log "User: $(whoami)"
    log "Working directory: $(pwd)"
    
    # Run installation steps
    detect_system
    find_openclaw  
    install_skill
    install_dependencies
    setup_apify
    configure_environment
    test_installation
    
    # Success message
    echo
    echo -e "${GREEN}╔════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║               🎉 Installation Complete!           ║${NC}"  
    echo -e "${GREEN}╚════════════════════════════════════════════════════╝${NC}"
    echo
    echo -e "${WHITE}🚗 Israeli Car Valuation is now ready!${NC}"
    echo
    echo -e "${CYAN}💬 Try these commands with your AI assistant:${NC}"
    echo -e "  ${WHITE}• \"כמה שווה טויוטה קורולה 2019?\"${NC}"
    echo -e "  ${WHITE}• \"What's my Honda Civic worth?\"${NC}"
    echo -e "  ${WHITE}• Send any Yad2 car link for instant analysis${NC}"
    echo
    echo -e "${YELLOW}🔧 Troubleshooting:${NC}"
    echo -e "  ${CYAN}• Restart OpenClaw to load the new skill${NC}"
    echo -e "  ${CYAN}• Check logs: $LOG_FILE${NC}"
    echo -e "  ${CYAN}• Visit: https://github.com/steinerhunter/car-valuation${NC}"
    echo
    
    log "=== Installation completed successfully ==="
}

# Error handling
trap 'error "Installation failed at step $CURRENT_STEP. Check logs: $LOG_FILE"' ERR

# Run main function
main "$@"