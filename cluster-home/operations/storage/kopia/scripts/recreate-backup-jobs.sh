#!/usr/bin/env sh
kubectl get pvc -A -l snapshot.home.arpa/enabled=true -o custom-columns=NAMESPACE:.metadata.namespace,NAME:.metadata.name --no-headers |
  while read -r namespace name; do
    echo "Triggering update for PVC: $name in namespace: $namespace"
    kubectl label pvc "$name" -n "$namespace" --overwrite snapshot.home.arpa/enabled=false
    kubectl label pvc "$name" -n "$namespace" --overwrite snapshot.home.arpa/enabled=true
  done

echo "Update trigger complete for all matching PVCs."
