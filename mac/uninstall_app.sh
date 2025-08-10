#!/bin/sh
# POSIX-safe uninstaller (no bashisms)
set -eu

DRY_RUN=0
APP_NAME=""

# Parse args
for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=1 ;;
    *) if [ -z "$APP_NAME" ]; then APP_NAME="$arg"; fi ;;
  esac
done

if [ -z "${APP_NAME:-}" ]; then
  printf "Enter the Application name (as seen in /Applications): "
  IFS= read -r APP_NAME
fi

# trim trailing spaces
APP_NAME_TRIMMED=$(printf "%s" "$APP_NAME" | sed 's/[[:space:]]*$//')

[ -n "$APP_NAME_TRIMMED" ] || { echo "No application name provided."; exit 1; }

echo "Searching for \"$APP_NAME_TRIMMED\".app ..."

# Build candidate list into a temp file
TMP=$(mktemp)
trap 'rm -f "$TMP"' EXIT

# Try Spotlight via mdfind (exact then fuzzy)
mdfind "kMDItemKind == 'Application' && kMDItemDisplayName == '$APP_NAME_TRIMMED'" 2>/dev/null >>"$TMP" || true
mdfind "kMDItemKind == 'Application' && kMDItemDisplayName == '*$APP_NAME_TRIMMED*'" 2>/dev/null >>"$TMP" || true

# Also check standard folders
[ -d "/Applications/$APP_NAME_TRIMMED.app" ] && echo "/Applications/$APP_NAME_TRIMMED.app" >>"$TMP"
[ -d "$HOME/Applications/$APP_NAME_TRIMMED.app" ] && echo "$HOME/Applications/$APP_NAME_TRIMMED.app" >>"$TMP"

# Dedup
sort -u "$TMP" -o "$TMP"

# Count
COUNT=$(wc -l <"$TMP" | awk '{print $1}')
if [ "$COUNT" -eq 0 ]; then
  echo "No app bundle found for \"$APP_NAME_TRIMMED\"."
  exit 1
fi

if [ "$COUNT" -gt 1 ]; then
  echo "Multiple matches found:"
  i=1
  while IFS= read -r line; do
    echo "  [$i] $line"
    i=$((i+1))
  done <"$TMP"
  printf "Choose a number: "
  IFS= read -r choice
  case "$choice" in
    ''|*[!0-9]*) echo "Invalid choice."; exit 1 ;;
  esac
  if [ "$choice" -lt 1 ] || [ "$choice" -gt "$COUNT" ]; then
    echo "Invalid choice."; exit 1
  fi
  APP_PATH=$(sed -n "${choice}p" "$TMP")
else
  APP_PATH=$(sed -n '1p' "$TMP")
fi

echo "Selected: $APP_PATH"

# Bundle ID (may be empty)
BUNDLE_ID=$(mdls -name kMDItemCFBundleIdentifier -raw "$APP_PATH" 2>/dev/null || true)
[ "$BUNDLE_ID" = "(null)" ] && BUNDLE_ID=""
if [ -n "$BUNDLE_ID" ]; then
  echo "Bundle identifier: $BUNDLE_ID"
else
  echo "Bundle identifier: (not found; will match by name)"
fi

APP_BASENAME=$(basename "$APP_PATH" .app)

# Helper: iterate a glob pattern and remove matches
remove_glob() {
  pat="$1"
  # expand the glob; if it doesn't match, it stays as literal
  # so check existence before removing
  for f in $pat; do
    [ -e "$f" ] || continue
    if [ "$DRY_RUN" -eq 1 ]; then
      echo "[dry-run] rm -rf \"$f\""
    else
      rm -rf "$f" 2>/dev/null || true
    fi
  done
}

sudo_remove_glob() {
  pat="$1"
  for f in $pat; do
    [ -e "$f" ] || continue
    if [ "$DRY_RUN" -eq 1 ]; then
      echo "[dry-run] sudo rm -rf \"$f\""
    else
      sudo rm -rf "$f" 2>/dev/null || true
    fi
  done
}

echo
echo "=== PLAN ================================================"
echo "App bundle to remove:"
echo "  $APP_PATH"
echo
echo "User-level leftovers (patterns):"
cat <<EOF
  $HOME/Library/Application Support/$APP_BASENAME
  $HOME/Library/Application Support/$APP_NAME_TRIMMED
  $HOME/Library/Caches/$APP_BASENAME
  $HOME/Library/Logs/$APP_BASENAME
  $HOME/Library/Saved Application State/$BUNDLE_ID.savedState
  $HOME/Library/Saved Application State/$APP_BASENAME.savedState
  $HOME/Library/Preferences/$BUNDLE_ID.plist
  $HOME/Library/Preferences/*$APP_BASENAME*.plist
  $HOME/Library/HTTPStorages/$BUNDLE_ID
  $HOME/Library/WebKit/$BUNDLE_ID
  $HOME/Library/Containers/$BUNDLE_ID
  $HOME/Library/Group Containers/*$(printf "%s" "$BUNDLE_ID" | sed 's/^[^.]*\.//')*
EOF
if [ -n "$BUNDLE_ID" ]; then
  cat <<EOF
  $HOME/Library/Caches/$BUNDLE_ID
  $HOME/Library/Caches/*$BUNDLE_ID*
  $HOME/Library/Logs/$BUNDLE_ID
  $HOME/Library/Application\ Scripts/$BUNDLE_ID
EOF
fi
echo
echo "System-level leftovers (patterns; optional):"
cat <<EOF
  /Library/Application\ Support/$APP_BASENAME
  /Library/Caches/$BUNDLE_ID
  /Library/Logs/$BUNDLE_ID
  /Library/Preferences/$BUNDLE_ID.plist
  /Library/LaunchAgents/*$BUNDLE_ID*.plist
  /Library/LaunchDaemons/*$BUNDLE_ID*.plist
  /var/db/receipts/${BUNDLE_ID}*.bom
  /var/db/receipts/${BUNDLE_ID}*.plist
EOF
echo "========================================================="
echo

printf "Proceed with UNINSTALL? (y/N): "
IFS= read -r CONFIRM
case "$CONFIRM" in
  y|Y) : ;;
  *) echo "Aborted."; exit 0 ;;
esac

echo
echo "Removing application bundle..."
if [ "$DRY_RUN" -eq 1 ]; then
  echo "[dry-run] rm -rf \"$APP_PATH\""
else
  rm -rf "$APP_PATH"
fi

echo "Cleaning user-level files..."
remove_glob "$HOME/Library/Application Support/$APP_BASENAME"
remove_glob "$HOME/Library/Application Support/$APP_NAME_TRIMMED"
remove_glob "$HOME/Library/Caches/$APP_BASENAME"
remove_glob "$HOME/Library/Logs/$APP_BASENAME"
[ -n "$BUNDLE_ID" ] && remove_glob "$HOME/Library/Saved Application State/$BUNDLE_ID.savedState"
remove_glob "$HOME/Library/Saved Application State/$APP_BASENAME.savedState"
[ -n "$BUNDLE_ID" ] && remove_glob "$HOME/Library/Preferences/$BUNDLE_ID.plist"
remove_glob "$HOME/Library/Preferences/*$APP_BASENAME*.plist"
[ -n "$BUNDLE_ID" ] && remove_glob "$HOME/Library/HTTPStorages/$BUNDLE_ID"
[ -n "$BUNDLE_ID" ] && remove_glob "$HOME/Library/WebKit/$BUNDLE_ID"
[ -n "$BUNDLE_ID" ] && remove_glob "$HOME/Library/Containers/$BUNDLE_ID"
if [ -n "$BUNDLE_ID" ]; then
  # Group Containers suffix (org part)
  SUFFIX=$(printf "%s" "$BUNDLE_ID" | sed 's/^[^.]*\.//')
  remove_glob "$HOME/Library/Group Containers/*$SUFFIX*"
  remove_glob "$HOME/Library/Caches/$BUNDLE_ID"
  remove_glob "$HOME/Library/Caches/*$BUNDLE_ID*"
  remove_glob "$HOME/Library/Logs/$BUNDLE_ID"
  remove_glob "$HOME/Library/Application Scripts/$BUNDLE_ID"
fi

echo
printf "Also remove system-level files (requires sudo)? (y/N): "
IFS= read -r SYS_CONFIRM
case "$SYS_CONFIRM" in
  y|Y)
    sudo_remove_glob "/Library/Application Support/$APP_BASENAME"
    [ -n "$BUNDLE_ID" ] && sudo_remove_glob "/Library/Caches/$BUNDLE_ID"
    [ -n "$BUNDLE_ID" ] && sudo_remove_glob "/Library/Logs/$BUNDLE_ID"
    [ -n "$BUNDLE_ID" ] && sudo_remove_glob "/Library/Preferences/$BUNDLE_ID.plist"
    [ -n "$BUNDLE_ID" ] && sudo_remove_glob "/Library/LaunchAgents/*$BUNDLE_ID*.plist"
    [ -n "$BUNDLE_ID" ] && sudo_remove_glob "/Library/LaunchDaemons/*$BUNDLE_ID*.plist"
    [ -n "$BUNDLE_ID" ] && sudo_remove_glob "/var/db/receipts/${BUNDLE_ID}*.bom"
    [ -n "$BUNDLE_ID" ] && sudo_remove_glob "/var/db/receipts/${BUNDLE_ID}*.plist"
    ;;
  *) echo "Skipping system-level cleanup." ;;
esac

echo
if [ "$DRY_RUN" -eq 1 ]; then
  echo "✅ Dry run complete. No files were deleted."
else
  echo "✅ Uninstall complete for \"$APP_NAME_TRIMMED\"."
fi

