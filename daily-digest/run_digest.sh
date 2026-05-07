#!/bin/bash
# OptimAI Daily Digest Runner — scheduled via cron at 6am
#
# Usage:
#   run_digest.sh              # generate only
#   run_digest.sh --email      # generate + email to EMAIL_TO
#
# Cron entry (generate + email at 6am daily):
#   0 6 * * * /home/user/OptimAI/daily-digest/run_digest.sh --email

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$SCRIPT_DIR/.."
LOG_DIR="$SCRIPT_DIR/logs"
ENV_FILE="$REPO_DIR/.env"

mkdir -p "$LOG_DIR"

# Load .env for cron (cron doesn't inherit shell env)
if [ -f "$ENV_FILE" ]; then
  set -a
  # shellcheck disable=SC1090
  source "$ENV_FILE"
  set +a
fi

if [ -z "$ANTHROPIC_API_KEY" ]; then
  echo "[$(date)] ERROR: ANTHROPIC_API_KEY not set. Check $ENV_FILE" | tee -a "$LOG_DIR/digest.log"
  exit 1
fi

echo "[$(date)] Starting OptimAI Daily Digest..." | tee -a "$LOG_DIR/digest.log"

cd "$REPO_DIR"
python3 daily-digest/digest_generator.py "$@" 2>&1 | tee -a "$LOG_DIR/digest.log"

echo "[$(date)] Digest complete." | tee -a "$LOG_DIR/digest.log"
