.PHONY: flux update-flux

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
        --owner=buvis-net \
        --repository=clusters \
        --path=./production/operations \
        --branch=main \
        --personal

update-flux:
	flux bootstrap github \
        --owner=buvis-net \
        --repository=clusters \
        --path=./production/operations \
        --branch=main \
        --personal
