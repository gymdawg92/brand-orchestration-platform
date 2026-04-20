#!/usr/bin/env bash
#
# Seed Auxo's project_refs + tech_stack into brand.config.
# Run post-deploy. PATCH /brands/auxo is unauthenticated.
#
# The claude_code ref is a placeholder until Auxo's iOS codebase is
# registered as its own Paperclip project; replace `id` and fill
# `repo_url` once that's done.
#
# Usage:
#   BASE_URL=https://gentle-peace-production-4b05.up.railway.app ./scripts/seed-auxo-tech-stack.sh
set -euo pipefail

BASE_URL="${BASE_URL:-https://gentle-peace-production-4b05.up.railway.app}"

existing=$(curl -sS "$BASE_URL/brands/auxo")
if ! echo "$existing" | grep -q '"slug":"auxo"'; then
  echo "Brand 'auxo' not found at $BASE_URL. Aborting." >&2
  exit 1
fi

# Merge new keys into existing config (preserves vertical, agent_model, etc.)
new_config=$(echo "$existing" | python3 -c '
import json, sys
brand = json.load(sys.stdin)
config = brand.get("config") or {}
config["project_refs"] = [
    {
        "type": "claude_code",
        "id": "auxo-ios-placeholder",
        "label": "Auxo iOS",
        "repo_url": None,
    }
]
config["tech_stack"] = {
    "languages": ["swift"],
    "frameworks": ["swiftui", "uikit"],
    "data": ["oracle"],
    "distribution": ["app_store"],
    "notes": "iOS-native app. Oracle backend (connection details TBD). Distribution via App Store. SwiftUI primary, some legacy UIKit surfaces likely.",
}
print(json.dumps({"config": config}))
')

curl -sS -X PATCH "$BASE_URL/brands/auxo" \
  -H "Content-Type: application/json" \
  -d "$new_config" | python3 -m json.tool

echo
echo "Verify:"
curl -sS "$BASE_URL/brands/auxo/tech-stack" | python3 -m json.tool
