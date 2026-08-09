#!/usr/bin/env bash
# Source this file to isolate Azure CLI and PAC CLI state per TACATDP environment.
#
# Usage:
#   source scripts/use-powerplatform-env.sh mshirika
#   source scripts/use-powerplatform-env.sh crdb
#
# The script intentionally changes HOME for the current shell so PAC keeps a
# separate token cache per target. Open a new terminal, or source this file
# again with a different target, when switching environments.

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  echo "This script must be sourced, not executed."
  echo "Usage: source scripts/use-powerplatform-env.sh mshirika"
  exit 2
fi

set_tacatdp_powerplatform_env() {
  local target="${1:-}"
  local original_home="${TACATDP_POWERPLATFORM_ORIGINAL_HOME:-$HOME}"
  local root="${TACATDP_POWERPLATFORM_STATE_ROOT:-$original_home/.tacatdp-powerplatform}"

  case "$target" in
    mshirika)
      export TACATDP_POWERPLATFORM_TARGET="mshirika"
      export TACATDP_POWERPLATFORM_TENANT_ID="365d788e-eb60-4c11-969b-403ea2bafb26"
      export POWER_PLATFORM_ENVIRONMENT_URL="https://orga3cf4b37.crm4.dynamics.com/"
      export POWER_PLATFORM_ENVIRONMENT_NAME="PowerPagesDeveloper-070926-125720"
      export PAC_AUTH_NAME="tacatdp-mshirika"
      ;;
    crdb)
      export TACATDP_POWERPLATFORM_TARGET="crdb"
      export TACATDP_POWERPLATFORM_TENANT_ID="4fc60296-e19d-4bd4-8ea8-96cbf963ed25"
      export POWER_PLATFORM_ENVIRONMENT_URL="https://org5eb0379b.crm4.dynamics.com/"
      export POWER_PLATFORM_ENVIRONMENT_NAME="TACATDP-CRDB-Dev"
      export PAC_AUTH_NAME="tacatdp-crdb"
      ;;
    *)
      echo "Unknown target: ${target:-<empty>}"
      echo "Usage: source scripts/use-powerplatform-env.sh mshirika"
      echo "   or: source scripts/use-powerplatform-env.sh crdb"
      return 2
      ;;
  esac

  export TACATDP_POWERPLATFORM_ORIGINAL_HOME="$original_home"
  export HOME="$root/$TACATDP_POWERPLATFORM_TARGET/home"
  export AZURE_CONFIG_DIR="$root/$TACATDP_POWERPLATFORM_TARGET/azure"
  export XDG_CONFIG_HOME="$root/$TACATDP_POWERPLATFORM_TARGET/xdg-config"
  export XDG_DATA_HOME="$root/$TACATDP_POWERPLATFORM_TARGET/xdg-data"
  export XDG_CACHE_HOME="$root/$TACATDP_POWERPLATFORM_TARGET/xdg-cache"
  export POWER_PLATFORM_TENANT_ID="$TACATDP_POWERPLATFORM_TENANT_ID"
  export POWER_PLATFORM_AUTH_MODE="${POWER_PLATFORM_AUTH_MODE:-azureCli}"
  export POWER_PLATFORM_CLOUD="${POWER_PLATFORM_CLOUD:-Public}"

  if ! mkdir -p "$HOME" "$AZURE_CONFIG_DIR" "$XDG_CONFIG_HOME" "$XDG_DATA_HOME" "$XDG_CACHE_HOME"; then
    echo "Failed to create isolated TACATDP Power Platform state directories under: $root"
    return 1
  fi
  if ! chmod 700 "$HOME" "$AZURE_CONFIG_DIR" "$XDG_CONFIG_HOME" "$XDG_DATA_HOME" "$XDG_CACHE_HOME"; then
    echo "Failed to secure isolated TACATDP Power Platform state directories under: $root"
    return 1
  fi

  echo "TACATDP Power Platform target: $TACATDP_POWERPLATFORM_TARGET"
  echo "Environment: $POWER_PLATFORM_ENVIRONMENT_NAME"
  echo "Environment URL: $POWER_PLATFORM_ENVIRONMENT_URL"
  echo "Tenant: $TACATDP_POWERPLATFORM_TENANT_ID"
  echo "Isolated HOME: $HOME"
  echo
  echo "Next checks:"
  echo "  az account show"
  echo "  pac auth who"
  echo "  pac pages list"
}

set_tacatdp_powerplatform_env "$@"
