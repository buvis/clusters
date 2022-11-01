.PHONY: install vms cluster flux update-flux 

install: | vms cluster flux

vms:
	cd infrastructure/terraform && terraform init
	cd infrastructure/terraform && terraform apply -auto-approve

cluster:
	talosctl gen config buvis https://$$MASTER1_IP:6443 --output-dir infrastructure/talos/generated-config --config-patch @infrastructure/talos/patch-all.yaml --config-patch-control-plane @infrastructure/talos/patch-controlplane.yaml
	timeout 600 bash -c 'while [[ "$$(curl --insecure https://$$MASTER1_IP:50000 -s; echo $$?)" != "35" ]]; do sleep 5; done'
	talosctl apply-config --insecure --nodes $$MASTER1_IP --file infrastructure/talos/generated-config/controlplane.yaml
	timeout 600 bash -c 'while [[ "$$(curl --insecure https://$$WORKER2_IP:50000 -s; echo $$?)" != "35" ]]; do sleep 5; done'
	talosctl apply-config --insecure --nodes $$WORKER2_IP --file infrastructure/talos/generated-config/worker.yaml
	timeout 600 bash -c 'while [[ "$$(curl --insecure https://$$WORKER3_IP:50000 -s; echo $$?)" != "35" ]]; do sleep 5; done'
	talosctl apply-config --insecure --nodes $$WORKER3_IP --file infrastructure/talos/generated-config/worker.yaml
	timeout 600 bash -c 'while [[ "$$(curl --insecure https://$$WORKER4_IP:50000 -s; echo $$?)" != "35" ]]; do sleep 5; done'
	talosctl apply-config --insecure --nodes $$WORKER4_IP --file infrastructure/talos/generated-config/worker.yaml
	timeout 600 bash -c 'while [[ "$$(curl --insecure https://$$MASTER1_IP:50001 -s; echo $$?)" != "35" ]]; do sleep 5; done'
	talosctl config endpoint $$MASTER1_IP
	talosctl config node $$MASTER1_IP
	talosctl bootstrap
	timeout 300 bash -c 'while [[ "$$(curl --insecure https://$$MASTER1_IP:6443 -s -o /dev/null; echo $$?)" != "0" ]]; do sleep 5; done'
	talosctl kubeconfig infrastructure/.kube --force
	timeout 300 bash -c 'while [[ "$$(kubectl get namespace tigera-operator -o json 2>/dev/null | jq .status.phase -r)" != "Active" ]]; do sleep 5; done'
	timeout 300 bash -c 'while [[ "$$(kubectl get namespace calico-system -o json 2>/dev/null | jq .status.phase -r)" != "Active" ]]; do sleep 5; done'

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
        --path=./cluster-home/operations \
        --branch=main \
        --personal

update-flux:
	flux bootstrap github \
        --owner=buvis \
        --repository=clusters \
        --path=./cluster-home/operations \
        --branch=main \
        --personal
