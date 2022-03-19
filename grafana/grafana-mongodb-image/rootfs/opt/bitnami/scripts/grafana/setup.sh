#!/bin/bash

# shellcheck disable=SC1091

set -o errexit
set -o nounset
set -o pipefail
# set -o xtrace # Uncomment this line for debugging purpose

# Load Grafana environment
. /opt/bitnami/scripts/grafana-env.sh

# Load libraries
. /opt/bitnami/scripts/liblog.sh
. /opt/bitnami/scripts/libservice.sh
. /opt/bitnami/scripts/libgrafana.sh

# Ensure Grafana environment variables are valid
grafana_validate

# Ensure Grafana is initialized
grafana_initialize
