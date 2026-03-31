#!/usr/bin/env bash
set -euo pipefail

CONTAINER_IMAGES_DIR="${CONTAINER_IMAGES_DIR:-$HOME/git/src/github.com/buvis/container-images}"
OPERATOR_DIR="$CONTAINER_IMAGES_DIR/apps/koolna-operator"
WEBUI_DIR="$CONTAINER_IMAGES_DIR/apps/koolna-webui"
CACHE_DIR="$CONTAINER_IMAGES_DIR/apps/koolna-cache"

# ── Interactive configuration ─────────────────────────────────────────────────

prompt() {
  local var="$1" label="$2" default="${3:-}"
  local value
  if [ -n "$default" ]; then
    read -rp "$label [$default]: " value
    printf '%s' "${value:-$default}"
  else
    read -rp "$label: " value
    printf '%s' "$value"
  fi
}

echo "── Koolna deployment configuration ──"
echo ""

KOOLNA_HOST=$(prompt KOOLNA_HOST "Ingress hostname" "koolna.local")
KOOLNA_USER=$(prompt KOOLNA_USER "WebUI username" "bob")
read -rsp "WebUI password: " KOOLNA_PASS
echo ""
KOOLNA_BRANCH=$(prompt KOOLNA_BRANCH "Default branch" "main")

echo ""
echo "Dotfiles (leave empty to skip):"
DOTFILES_METHOD=$(prompt DOTFILES_METHOD "  Method (none/bare-git/clone/command)" "none")

DOTFILES_REPO=""
DOTFILES_BARE_DIR=""
DOTFILES_COMMAND=""
DOTFILES_INIT=""

if [ "$DOTFILES_METHOD" = "bare-git" ] || [ "$DOTFILES_METHOD" = "clone" ]; then
  DOTFILES_REPO=$(prompt DOTFILES_REPO "  Repository URL" "")
  if [ "$DOTFILES_METHOD" = "bare-git" ]; then
    DOTFILES_BARE_DIR=$(prompt DOTFILES_BARE_DIR "  Bare repo dir" ".cfg")
  fi
fi

if [ "$DOTFILES_METHOD" = "command" ]; then
  DOTFILES_COMMAND=$(prompt DOTFILES_COMMAND "  Command" "")
fi

if [ "$DOTFILES_METHOD" != "none" ] && [ "$DOTFILES_METHOD" != "" ]; then
  DOTFILES_INIT=$(prompt DOTFILES_INIT "  Init command (optional)" "")
fi

echo ""
echo "── Deploying ──"

# ── Namespaces ────────────────────────────────────────────────────────────────

echo "==> Creating namespace..."
kubectl create namespace koolna --dry-run=client -o yaml | kubectl apply -f -

# ── Operator ──────────────────────────────────────────────────────────────────

echo "==> Deploying operator via kustomize..."
kubectl apply -k "$OPERATOR_DIR/config/default"

echo "==> Waiting for operator..."
kubectl rollout status deployment -n koolna -l app.kubernetes.io/name=koolna-operator --timeout=300s

# ── Cache proxy ──────────────────────────────────────────────────────────────

echo "==> Deploying cache proxy via kustomize..."
kubectl apply -k "$CACHE_DIR/deploy"

echo "==> Waiting for cache proxy..."
kubectl rollout status deployment koolna-cache -n koolna --timeout=120s

# ── WebUI ─────────────────────────────────────────────────────────────────────

echo "==> Deploying webui via kustomize..."
kubectl apply -k "$WEBUI_DIR/deploy"

# ── Ingress host patch ────────────────────────────────────────────────────────

if [ "$KOOLNA_HOST" != "koolna.local" ]; then
  echo "==> Patching ingress host to $KOOLNA_HOST..."
  kubectl patch ingress koolna-webui -n koolna --type=json \
    -p "[{\"op\":\"replace\",\"path\":\"/spec/rules/0/host\",\"value\":\"$KOOLNA_HOST\"}]"
fi

# ── Basic auth secret ────────────────────────────────────────────────────────

echo "==> Creating basic auth secret..."
HASH=$(htpasswd -nbB "$KOOLNA_USER" "$KOOLNA_PASS")
kubectl delete secret koolna-webui-auth -n koolna --ignore-not-found
kubectl create secret generic koolna-webui-auth \
  --from-literal=auth="$HASH" \
  -n koolna

# ── Defaults ConfigMap ────────────────────────────────────────────────────────

echo "==> Configuring defaults..."
kubectl patch configmap koolna-defaults -n koolna --type=merge -p "{
  \"data\": {
    \"defaultBranch\": \"$KOOLNA_BRANCH\",
    \"dotfilesMethod\": \"$DOTFILES_METHOD\",
    \"dotfilesRepo\": \"$DOTFILES_REPO\",
    \"dotfilesBareDir\": \"$DOTFILES_BARE_DIR\",
    \"dotfilesCommand\": \"$DOTFILES_COMMAND\",
    \"dotfilesInit\": \"$DOTFILES_INIT\"
  }
}"

# ── Wait ──────────────────────────────────────────────────────────────────────

echo "==> Waiting for webui..."
kubectl rollout status deployment koolna-webui -n koolna --timeout=60s

echo "==> Done. Koolna available at http://$KOOLNA_HOST"
