.PHONY: install nodes masters workers

install: | nodes masters workers

nodes:
	cd infrastructure/terraform && terraform init
	cd infrastructure/terraform && terraform apply -auto-approve

masters:
	ansible-playbook ansible/install-k3s-masters.yaml
	kubectl apply -f https://docs.projectcalico.org/manifests/tigera-operator.yaml
	kubectl apply -f infrastructure/manifests/install-calico.yaml

workers:
	ansible-playbook infrastructure/ansible/install-k3s-workers.yaml

flux:
	kubectl create namespace flux-system
	kubectl apply -f operations/flux-system/extras/cluster-config.yaml
	kubectl create secret generic cluster-secret-vars -n flux-system
	gpg --export-secret-keys --armor $(SOPS_KEY_FINGERPRINT) | \
		kubectl create secret generic sops-gpg \
		--namespace=flux-system
		--from-file=sops.asc=/dev/stdin
	kubectl create secret generic slack-url \
		--from-literal=address=$(SLACK_WEBHOOK_URL)
	flux bootstrap github \
        --owner=buvis-net \
        --repository=clusters \
        --path=staging/operations \
        --branch=main \
        --personal
