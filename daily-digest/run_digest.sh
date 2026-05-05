#!/bin/bash
# OptimAI Daily Digest Runner — scheduled via cron at 6am
# Cron entry: 0 6 * * * /home/user/OptimAI/daily-digest/run_digest.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$SCRIPT_DIR/.."
LOG_DIR="$SCRIPT_DIR/logs"
ENV_FILE="$REPO_DIR/.env"

mkdir -p "$LOG_DIR"

# Load API key from .env
if [ -f "$ENV_FILE" ]; then
  export $(grep -v '^#' "$ENV_FILE" | xargs)
fi

if [ -z "$ANTHROPIC_API_KEY" ]; then
  echo "[$(date)] ERROR: ANTHROPIC_API_KEY not set. Check $ENV_FILE" | tee -a "$LOG_DIR/digest.log"
  exit 1
fi

echo "[$(date)] Starting OptimAI Daily Digest..." | tee -a "$LOG_DIR/digest.log"

cd "$REPO_DIR"
python3 daily-digest/digest_generator.py 2>&1 | tee -a "$LOG_DIR/digest.log"

echo "[$(date)] Digest complete." | tee -a "$LOG_DIR/digest.log"
