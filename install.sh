#!/usr/bin/env bash
set -euo pipefail

# Oracle installer — adds custom tools into hermes-agent
# Run from the oracle project root: ./install.sh

HERMES_TOOLS="${HOME}/.hermes/hermes-agent/tools"
ORACLE_DIR="$(cd "$(dirname "$0")" && pwd)"

if [ ! -d "$HERMES_TOOLS" ]; then
    echo "Error: hermes-agent not found at ~/.hermes/hermes-agent"
    echo "Install it first: curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash"
    exit 1
fi

echo "Installing Oracle tools into hermes-agent..."

# Symlink tool files
for tool_file in exodus_tools.py muse_tools.py sisyphus_tools.py progression_tools.py todoist_tools.py; do
    src="${ORACLE_DIR}/tools/${tool_file}"
    dst="${HERMES_TOOLS}/${tool_file}"
    if [ -L "$dst" ] || [ -f "$dst" ]; then
        rm "$dst"
    fi
    ln -s "$src" "$dst"
    echo "  Linked ${tool_file}"
done

# Patch __init__.py to import oracle tools (idempotent)
INIT_FILE="${HERMES_TOOLS}/__init__.py"
MARKER="# --- Oracle tools ---"

if ! grep -q "$MARKER" "$INIT_FILE" 2>/dev/null; then
    cat >> "$INIT_FILE" << 'EOF'

# --- Oracle tools ---
from tools.exodus_tools import *      # noqa: F401,F403
from tools.muse_tools import *        # noqa: F401,F403
from tools.sisyphus_tools import *    # noqa: F401,F403
from tools.progression_tools import * # noqa: F401,F403
from tools.todoist_tools import *     # noqa: F401,F403
EOF
    echo "  Patched __init__.py"
else
    echo "  __init__.py already patched"
fi

# Copy HERMES.md context file
if [ -f "${ORACLE_DIR}/HERMES.md" ]; then
    cp "${ORACLE_DIR}/HERMES.md" "${HOME}/.hermes/HERMES.md"
    echo "  Installed HERMES.md context file"
fi

# Remind about env vars
echo ""
echo "Done! Now add these to ~/.hermes/.env:"
echo ""
echo "  EXODUS_API_URL=http://localhost:3001/api"
echo "  MUSE_API_URL=http://localhost:3002/api"
echo "  SISYPHUS_API_URL=http://localhost:3003/api"
echo "  PROGRESSION_API_URL=http://localhost:8000/api/v1"
echo "  FIREBASE_ID_TOKEN=<your-token>"
echo "  TODOIST_API_TOKEN=<your-token>"
echo ""
echo "Then enable toolsets: hermes tools -> enable exodus, muse, sisyphus, progression, todoist"
echo "Or run: hermes chat --toolsets 'exodus,muse,sisyphus,progression,todoist,web,terminal,memory'"
