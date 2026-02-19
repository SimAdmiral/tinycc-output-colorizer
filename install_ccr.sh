#!/usr/bin/env bash
# author: Sim Admiral
# project: PB111 – Code Highlighter
set -euo pipefail

# ------------- Configuration -------------------------------------------------
DEFAULT_PREFIX="$HOME/bin"
PREFIX="$DEFAULT_PREFIX"
FILES=("ccr" "colorizer.py")

GREEN="\e[32m"; RED="\e[31m"; YELLOW="\e[33m"; RESET="\e[0m"

usage() {
    cat <<EOF
Usage: ./install_ccr.sh [--prefix DIR]

Options:
  --prefix DIR   Install scripts into DIR (default: $DEFAULT_PREFIX)
  -h, --help     Show this help and exit

This installer:
  • checks for run‑time requirements (bash, python3, tinycc)
  • installs ${FILES[*]} into the chosen directory
  • adds directory to PATH if needed
EOF
    exit 0
}

# ------------- Parse Arguments -----------------------------------------------
while [[ $# -gt 0 ]]; do
    case $1 in
        --prefix)
            PREFIX="$2"
            [[ "$PREFIX" == ~* ]] && PREFIX="${PREFIX/#\~/$HOME}"
            shift 2
            ;;
        -h|--help)
            usage
            ;;
        *)
            echo -e "${RED}Unknown option: $1${RESET}"
            usage
            ;;
    esac
done

# ------------- Banner --------------------------------------------------------
echo -e "${YELLOW}PB111 – Code‑Highlighter Installer${RESET}"
echo "Target directory: $PREFIX"
echo

# ------------- Check Requirements --------------------------------------------
declare -A REQUIREMENTS=(
  [bash]="bash"
  [python3]="python3"
  [tinycc]="tinycc"
)

MISSING=()
for key in "${!REQUIREMENTS[@]}"; do
    if ! command -v "${REQUIREMENTS[$key]}" >/dev/null; then
        echo -e " • ${key}: ${RED}missing ✘${RESET}"
        MISSING+=("$key")
    else
        echo -e " • ${key}: ${GREEN}found ✓${RESET}"
    fi
done

if (( ${#MISSING[@]} )); then
    echo -e "\n${RED}Missing requirement(s):${RESET} ${MISSING[*]}"
    echo "Install them using your system's package manager before continuing."
    exit 1
fi

# ------------- Install Files -------------------------------------------------
mkdir -p "$PREFIX"

for file in "${FILES[@]}"; do
    if [[ -f "$file" ]]; then
        install -m 755 "$file" "$PREFIX/$file"
        echo "Installed $file to $PREFIX/"
    else
        echo -e "${RED}Warning:${RESET} File not found: $file"
    fi
done

# ------------- PATH Runtime Check --------------------------------------------
if [[ ":$PATH:" != *":$PREFIX:"* ]]; then
    echo -e "\n${YELLOW}Note:${RESET} $PREFIX is not in your current session's PATH."
    
    read -rp "${YELLOW}Do you want to add $PREFIX to PATH for the current session now? [y/N]: ${RESET}" answer
    case "$answer" in
        y|Y|yes|YES|Yes )
            export PATH="$PREFIX:$PATH"
            echo -e "${GREEN}Added $PREFIX to PATH for this session.${RESET}"
            ;;
        * )
            echo "Skipped adding $PREFIX to PATH for current session."
            ;;
    esac
fi

# ------------- Ensure PATH is Persistently Set -------------------------------
SHELL_RC=""
if [[ "$SHELL" == */bash ]]; then
    SHELL_RC="$HOME/.bashrc"
elif [[ "$SHELL" == */zsh ]]; then
    SHELL_RC="$HOME/.zshrc"
fi

if [[ -n "$SHELL_RC" ]]; then
    if ! grep -q 'export PATH="$HOME/bin:$PATH"' "$SHELL_RC"; then
        echo -e "\n${YELLOW}Adding export to $SHELL_RC...${RESET}"
        echo 'export PATH="$HOME/bin:$PATH"' >> "$SHELL_RC"
        echo -e "${GREEN}✓ Done.${RESET} Now run: source $SHELL_RC"
    else
        echo -e "\n${GREEN}✓ PATH already set in $SHELL_RC.${RESET}"
    fi
else
    echo -e "\n${RED}Shell config not detected.${RESET} Add this to your shell config manually:"
    echo '  export PATH="$HOME/bin:$PATH"'
fi

# ------------- Done ----------------------------------------------------------
echo -e "\n${GREEN}✔ Installation complete!${RESET} You can now run: ccr --help"
