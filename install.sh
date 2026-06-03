#!/bin/sh
# egw-tools installer — one command.
# curl -sSL https://raw.githubusercontent.com/gershomj/egw-tools/main/install.sh | bash

set -e

REPO="https://raw.githubusercontent.com/gershomj/egw-tools/main"
INSTALL_DIR="$HOME/.egw-tools"
BIN_DIR="$HOME/.local/bin"

echo "╔══════════════════════════════════════════╗"
echo "║       egw — EGW + KJV Bible Search      ║"
echo "╚══════════════════════════════════════════╝"
echo ""

# ── Find Python ──
PYTHON=""
for p in python3 python; do
    if command -v "$p" >/dev/null 2>&1; then
        PYTHON="$p"
        break
    fi
done

if [ -z "$PYTHON" ]; then
    echo "Python 3 is required but not found."
    echo ""
    # Detect package manager
    PKG_MGR=""
    if command -v apt >/dev/null 2>&1; then
        PKG_MGR="sudo apt install python3"
    elif command -v pacman >/dev/null 2>&1; then
        PKG_MGR="sudo pacman -S python"
    elif command -v dnf >/dev/null 2>&1; then
        PKG_MGR="sudo dnf install python3"
    elif command -v brew >/dev/null 2>&1; then
        PKG_MGR="brew install python3"
    elif command -v zypper >/dev/null 2>&1; then
        PKG_MGR="sudo zypper install python3"
    fi

    if [ -n "$PKG_MGR" ]; then
        printf "Install Python 3 now? [y/N] "
        read -r answer
        if [ "$answer" = "y" ] || [ "$answer" = "Y" ]; then
            echo "Running: $PKG_MGR"
            $PKG_MGR
            # Re-check
            for p in python3 python; do
                if command -v "$p" >/dev/null 2>&1; then
                    PYTHON="$p"
                    break
                fi
            done
        fi
    fi

    if [ -z "$PYTHON" ]; then
        echo "Python 3 not found. Install it from https://python.org/downloads/"
        echo "Make sure 'python3' is on your PATH, then re-run this installer."
        exit 1
    fi
fi

echo "Python: $($PYTHON --version)"
echo ""

# ── Create directories ──
mkdir -p "$INSTALL_DIR" "$BIN_DIR"

# ── Download egw ──
echo "Downloading egw (~27 KB)..."
curl -sSL "$REPO/egw" -o "$INSTALL_DIR/egw"
chmod +x "$INSTALL_DIR/egw"

# ── Download pre-built KJV ──
echo "Downloading KJV Bible database (~12 MB)..."
curl -sSL "$REPO/kjv.db" -o "$INSTALL_DIR/kjv.db"

# ── Link to PATH ──
ln -sf "$INSTALL_DIR/egw" "$BIN_DIR/egw"

# ── Ensure ~/.local/bin is in PATH ──
if ! echo "$PATH" | grep -q "$BIN_DIR"; then
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

echo ""
echo "Done! egw v$($PYTHON "$INSTALL_DIR/egw" --version 2>/dev/null || echo "?") is installed."
echo ""
echo "  KJV Bible:  ready (pre-built, 31,009 verses)"
echo "  EGW corpus: not downloaded yet (~1.3 GB, optional)"
echo ""
echo "  Quick start:"
echo "    egw --kjv \"John 3:16\"      KJV verse lookup"
echo "    egw --kjv-search \"faith\"   KJV keyword search"
echo "    egw --egw-download          Download EGW writings"
echo "    egw --search \"sabbath\"      Search EGW (after download)"
echo ""
echo "  Restart your terminal or run:  source $RC"
