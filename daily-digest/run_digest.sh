#!/bin/bash
# OptimAI Daily Digest Runner
# Add to cron: 0 6 * * * /home/user/OptimAI/daily-digest/run_digest.sh
# Or: crontab -e  →  0 6 * * * cd /home/user/OptimAI && python3 daily-digest/digest_generator.py >> daily-digest/logs/digest.log 2>&1

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$SCRIPT_DIR/logs"
mkdir -p "$LOG_DIR"

echo "[$(date)] Starting OptimAI Daily Digest..." | tee -a "$LOG_DIR/digest.log"

cd "$SCRIPT_DIR/.."
python3 daily-digest/digest_generator.py 2>&1 | tee -a "$LOG_DIR/digest.log"

echo "[$(date)] Digest complete." | tee -a "$LOG_DIR/digest.log"
