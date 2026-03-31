#!/usr/bin/env bash
set -euo pipefail

CONTAINER_IMAGES_DIR="${CONTAINER_IMAGES_DIR:-$HOME/git/src/github.com/buvis/container-images}"
OPERATOR_DIR="$CONTAINER_IMAGES_DIR/apps/koolna-operator"
WEBUI_DIR="$CONTAINER_IMAGES_DIR/apps/koolna-webui"
CACHE_DIR="$CONTAINER_IMAGES_DIR/apps/koolna-cache"

echo "==> Deleting Koolna CRs (finalizers need operator running)..."
kubectl delete koolnas --all -n koolna --ignore-not-found

echo "==> Deleting leftover PVCs and secrets..."
kubectl delete pvc --all -n koolna --ignore-not-found
kubectl delete secrets --all -n koolna --ignore-not-found

echo "==> Tearing down webui via kustomize..."
kubectl delete -k "$WEBUI_DIR/deploy" --ignore-not-found

echo "==> Tearing down cache proxy via kustomize..."
kubectl delete -k "$CACHE_DIR/deploy" --ignore-not-found

echo "==> Tearing down operator via kustomize..."
kubectl delete -k "$OPERATOR_DIR/config/default" --ignore-not-found

echo "==> Deleting namespace..."
kubectl delete namespace koolna --ignore-not-found

echo "==> Done"
