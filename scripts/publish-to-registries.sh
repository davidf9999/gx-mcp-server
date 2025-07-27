#!/usr/bin/env bash
set -euo pipefail

### usage:
# # 1) Install dependencies
# brew install gh yq jq     # macOS (or your distro’s package manager)
# gh auth login             # make sure GH CLI is auth’d

# # 2) Prepare your registry list (registries.yaml)

# # 3) Execute
# ./scripts/publish-to-registries.sh ./scripts/registries.yaml gx-mcp-server "docs: add gx-mcp-server to Community lists" "docs(registry): add gx-mcp-server"
### End: usage


REGFILE="$1"        # e.g. registries.yaml
PKG_NAME="$2"       # e.g. gx-mcp-server
COMMIT_MSG="$3"     # e.g. "docs: add gx-mcp-server to Community"
PR_TITLE="$4"       # optional; defaults to commit msg

# Default PR body
PR_BODY="${5:-Add ${PKG_NAME} to registry entry list.}"

# Loop through each registry
yq eval '.[]' -o=json "$REGFILE" | jq -c '. as $reg | $reg' | while read -r reg; do
  REPO=$(jq -r .repo <<<"$reg")
  FILE=$(jq -r .file <<<"$reg")
  MARKER=$(jq -r .marker <<<"$reg")
  ENTRY=$(jq -r .entry <<<"$reg")

  BRANCH="add-${PKG_NAME}-to-$(echo "$REPO" | tr / -)"
  echo "→ Publishing to $REPO ($FILE)..."

  # 1) Fork & clone (if not already forked)
  gh repo fork "$REPO" --clone=true --remote=true --force

  pushd "$(basename "$REPO")" >/dev/null

    # 2) Create new branch (force-delete if exists)
    git branch -D "$BRANCH" 2>/dev/null || true
    git checkout -b "$BRANCH"

    # 3) Insert entry
    # Use sed to insert ENTRY after the line matching MARKER
    sed -i "/$MARKER/a $ENTRY" "$FILE"

    # 4) Commit & push
    git add "$FILE"
    git commit -m "$COMMIT_MSG"
    git push --set-upstream origin "$BRANCH"

    # 5) Create PR
    gh pr create \
      --repo "$REPO" \
      --base main \
      --title "${PR_TITLE:-$COMMIT_MSG}" \
      --body "$PR_BODY" \
      --head "$(gh repo view --json owner -q .owner)/$BRANCH"

  popd >/dev/null
  echo "✓ PR opened for $REPO"
done

echo "All done."
