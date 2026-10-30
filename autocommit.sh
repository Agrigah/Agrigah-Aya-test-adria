#!/usr/bin/env bash
# Usage: ./autocommit.sh  (laisser tourner dans un terminal séparé)
while true; do
  git add -A
  git diff --cached --quiet || git commit -m "wip: $(date '+%Y-%m-%d %H:%M')"
  git push origin HEAD 2>/dev/null
  sleep 900
done
