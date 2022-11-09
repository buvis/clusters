.PHONY: install nodes cluster cni flux update-flux

install: | nodes cluster cni flux

nodes:
	talosctl gen config buvis-office https://$$MASTER_IP:6443 --output-dir infrastructure/talos/generated-config --config-patch @infrastructure/talos/patch-all.yaml --config-patch-control-plane @infrastructure/talos/patch-controlplane.yaml
	talosctl apply-config --insecure --nodes $$MASTER_IP --file infrastructure/talos/generated-config/controlplane.yaml
	talosctl apply-config --insecure --nodes $$WORKER1_IP --file infrastructure/talos/generated-config/worker.yaml
	talosctl apply-config --insecure --nodes $$WORKER2_IP --file infrastructure/talos/generated-config/worker.yaml

cluster:
	timeout 900 bash -c 'while [[ "$$(curl --insecure https://$$MASTER_IP:50001 -s; echo $$?)" != "35" ]]; do sleep 5; done'
	talosctl config endpoint $$MASTER_IP
	talosctl config node $$MASTER_IP
	talosctl bootstrap

cni:
	timeout 900 bash -c 'while [[ "$$(curl --insecure https://$$MASTER_IP:6443 -s -o /dev/null; echo $$?)" != "0" ]]; do sleep 5; done'
	talosctl kubeconfig infrastructure/.kube --force
	timeout 900 bash -c 'while [[ "$$(kubectl get namespace tigera-operator -o json 2>/dev/null | jq .status.phase -r)" != "Active" ]]; do sleep 5; done'
	timeout 900 bash -c 'while [[ "$$(kubectl get namespace calico-system -o json 2>/dev/null | jq .status.phase -r)" != "Active" ]]; do sleep 5; done'

flux:
	kubectl create namespace flux-system --dry-run=client -o yaml | kubectl apply -f -
	kubectl apply -f operations/flux-system/extras/cluster-config.yaml
	kubectl create secret generic cluster-secret-vars -n flux-system
	gpg --export-secret-keys --armor $(SOPS_KEY_FINGERPRINT) | \
		kubectl create secret generic sops-gpg \
		--namespace=flux-system \
		--from-file=sops.asc=/dev/stdin
	kubectl create secret generic slack-url \
		--namespace=flux-system \
		--from-literal=address=$(SLACK_WEBHOOK_URL)
	flux bootstrap github \
        --owner=buvis \
        --repository=clusters \
        --path=./cluster-office/operations \
        --branch=main \
        --personal

update-flux:
	flux bootstrap github \
        --owner=buvis \
        --repository=clusters \
        --path=./cluster-office/operations \
        --branch=main \
        --personal
