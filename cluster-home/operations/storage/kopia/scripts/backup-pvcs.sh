#!/bin/bash

# Define the label selector to find the target CronJobs
LABEL_SELECTOR="generate.kyverno.io/policy-name=snapshot-cronjob-controller"

echo "Finding CronJobs with label: $LABEL_SELECTOR"

# Get the namespace and name of all CronJobs matching the label
# The --no-headers flag prevents the header line from being processed by the loop
kubectl get cronjobs -A -l "$LABEL_SELECTOR" -o custom-columns=NAMESPACE:.metadata.namespace,NAME:.metadata.name --no-headers |
  while read -r namespace name; do
    if [[ -n "$name" ]]; then
      # Generate a unique name for the new Job based on the CronJob name and a timestamp
      JOB_NAME="${name}-manual-$(date +%s)"

      echo "Triggering CronJob '$name' in namespace '$namespace' by creating Job '$JOB_NAME'..."

      # Create a new Job from the CronJob template in the correct namespace
      kubectl create job "$JOB_NAME" --from="cronjob/$name" -n "$namespace"
    fi
  done

echo "All matching CronJobs have been triggered."
