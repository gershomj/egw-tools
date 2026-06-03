#!/bin/sh
# egw-tools installer — one command, everything automated.
# curl -sSL https://raw.githubusercontent.com/gershomj/egw-tools/main/install.sh | bash

set -e

REPO="https://raw.githubusercontent.com/gershomj/egw-tools/main"
INSTALL_DIR="$HOME/.egw-tools"
BIN_DIR="$HOME/.local/bin"

echo "egw-tools installer"
echo "==================="

# ── Find/create Python ──
PYTHON=""
for p in python3 python; do
    if command -v "$p" >/dev/null 2>&1; then
        PYTHON="$p"
        break
    fi
done

if [ -z "$PYTHON" ]; then
    echo "Python 3 not found. Install it first:"
    echo "  Ubuntu/Debian: sudo apt install python3"
    echo "  Arch:          sudo pacman -S python"
    echo "  Fedora:        sudo dnf install python3"
    echo "  macOS:         brew install python3"
    exit 1
fi

echo "Python: $($PYTHON --version)"

# ── Create directories ──
mkdir -p "$INSTALL_DIR" "$BIN_DIR"

# ── Download files ──
echo "Downloading egw..."
curl -sSL "$REPO/egw" -o "$INSTALL_DIR/egw"
chmod +x "$INSTALL_DIR/egw"

echo "Downloading build_kjv.py..."
curl -sSL "$REPO/build_kjv.py" -o "$INSTALL_DIR/build_kjv.py"

# ── Link to PATH ──
ln -sf "$INSTALL_DIR/egw" "$BIN_DIR/egw"

# ── Ensure ~/.local/bin is in PATH ──
if ! echo "$PATH" | grep -q "$BIN_DIR"; then
    # Detect shell and add to rc file
    case "$SHELL" in
        */zsh)   RC="$HOME/.zshrc" ;;
        */bash)  RC="$HOME/.bashrc" ;;
        */fish)  RC="$HOME/.config/fish/config.fish" ;;
        *)       RC="$HOME/.profile" ;;
    esac

    if ! grep -q "$BIN_DIR" "$RC" 2>/dev/null; then
        echo "export PATH=\"$BIN_DIR:\$PATH\"" >> "$RC"
        echo "Added $BIN_DIR to PATH in $RC"
    fi
fi

# ── Start KJV build automatically ──
echo ""
echo "Starting KJV Bible build in background..."
"$PYTHON" "$INSTALL_DIR/build_kjv.py" > "$INSTALL_DIR/kjv-build.log" 2>&1 &
BUILD_PID=$!
echo $BUILD_PID > "$INSTALL_DIR/kjv-build.pid"

echo ""
echo "Done! egw is installed."
echo ""
echo "  KJV Bible is building in the background (~40 min)."
echo "  Check progress:  egw --kjv-status"
echo ""
echo "  Try it now:"
echo "    egw --version"
echo "    egw --search \"sabbath\"        (needs EGW database)"
echo "    egw --kjv \"John 3:16\"         (works once build finishes)"
echo ""
echo "  To use EGW features, place egw-corpus.db in ~/.egw-tools/"
echo ""
echo "  Restart your terminal or run:  source $RC"
