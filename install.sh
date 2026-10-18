#!/usr/bin/env bash
# Kuromi dotfiles ♥ — CachyOS + Hyprland + Noctalia
#
#   ./install.sh            instala pacotes, faz backup e cria os symlinks
#   ./install.sh --no-pkgs  só os symlinks
#   ./install.sh --art      regenera wallpapers/logo na resolução do monitor
set -euo pipefail

DOT="$(cd "$(dirname "$0")" && pwd)"
CFG="${XDG_CONFIG_HOME:-$HOME/.config}"
BACKUP="$HOME/.config-backup-$(date +%Y%m%d-%H%M%S)"

PKGS=(mpvpaper rofi jq fuzzel python-cairo ffmpeg imagemagick fastfetch kitty ttf-meslo-nerd)
LINKS=(hypr kitty noctalia fastfetch fish rofi)

pink() { printf '\e[38;2;255;143;200m%s\e[0m\n' "$*"; }

if [[ "${1:-}" == "--art" ]]; then
    res="$(hyprctl monitors -j 2>/dev/null | python3 -c 'import json,sys; m=json.load(sys.stdin)[0]; print(f"{m[\"width\"]}x{m[\"height\"]}")' || echo 1920x1080)"
    python3 "$DOT/tools/kuromi_art.py" --size "$res"
    python3 "$DOT/tools/guts_art.py" --size "$res"
    exit
fi

if [[ "${1:-}" != "--no-pkgs" ]]; then
    pink "♥ instalando pacotes: ${PKGS[*]}"
    sudo pacman -S --needed --noconfirm "${PKGS[@]}"
fi

pink "♥ linkando configs (backup em $BACKUP)"
for name in "${LINKS[@]}"; do
    target="$CFG/$name"
    if [[ -L "$target" && "$(readlink -f "$target")" == "$DOT/config/$name" ]]; then
        echo "  = $name (já linkado)"; continue
    fi
    if [[ -e "$target" || -L "$target" ]]; then
        mkdir -p "$BACKUP"; mv "$target" "$BACKUP/"
    fi
    ln -s "$DOT/config/$name" "$target"
    echo "  → $target"
done

mkdir -p "$(xdg-user-dir PICTURES 2>/dev/null || echo "$HOME/Imagens")/Wallpapers"
# tema ativo (link local, fora do git); Kuromi na primeira instalação
[[ -L "$DOT/themes/current" ]] || ln -s Kuromi "$DOT/themes/current"

if pgrep -x noctalia >/dev/null; then
    pink "♥ aplicando tema Kuromi"
    noctalia msg color-scheme-set custom Kuromi || true
    noctalia msg config-reload || true
    "$DOT/scripts/kwall" fetch all || true                      # wallpapers animados de todos os temas
    "$DOT/scripts/ktheme" set "$(basename "$(readlink -f "$DOT/themes/current")")" || true
fi
pgrep -x Hyprland >/dev/null && hyprctl reload >/dev/null || true

pink "♥ pronto! abra um novo terminal para ver o fastfetch da Kuromi"
