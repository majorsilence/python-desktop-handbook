#!/usr/bin/env sh
#
# Install the example's desktop file and icon for the current user.
#
# Everything below lives under ~/.local/share, which is the per-user half of the
# XDG data directories. Installing system-wide is the same paths under /usr/share
# and needs root.
#
set -eu

app_id="com.example.Settings"
here="$(cd "$(dirname "$0")" && pwd)"
data="${XDG_DATA_HOME:-$HOME/.local/share}"

mkdir -p "$data/applications" "$data/icons/hicolor/scalable/apps" "$HOME/.local/bin"

# The Exec line must name something on PATH, or give an absolute path.
cat > "$HOME/.local/bin/settings-example" <<SCRIPT
#!/usr/bin/env sh
exec python3 "$here/settings.py" "\$@"
SCRIPT
chmod +x "$HOME/.local/bin/settings-example"

# The icon's basename must match the Icon= line, which should match the app id.
cat > "$data/icons/hicolor/scalable/apps/$app_id.svg" <<'SVG'
<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64">
  <rect width="64" height="64" rx="14" fill="#3584e4"/>
  <circle cx="32" cy="32" r="13" fill="none" stroke="#fff" stroke-width="5"/>
  <circle cx="32" cy="32" r="4" fill="#fff"/>
</svg>
SVG

install -m 644 "$here/$app_id.desktop" "$data/applications/$app_id.desktop"

# The caches are what the shell actually reads; without these the entry may not
# appear until the next login.
update-desktop-database "$data/applications" 2>/dev/null || true
gtk-update-icon-cache -f -t "$data/icons/hicolor" 2>/dev/null || true

echo "installed $app_id"
echo "check it with: desktop-file-validate $data/applications/$app_id.desktop"
