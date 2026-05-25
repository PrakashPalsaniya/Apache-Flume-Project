#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════
#  verify-ingestion.sh
#  Run INSIDE the namenode container to verify Flume ingestion.
#
#  Usage (from project directory):
#    docker exec namenode bash /opt/verify-ingestion.sh
#
#  Or copy it first:
#    docker cp verify-ingestion.sh namenode:/opt/
#    docker exec namenode bash /opt/verify-ingestion.sh
# ═══════════════════════════════════════════════════════════════════
set -euo pipefail

HDFS_PATH="/flume/logs"
EXPECTED_LINES=10000

# ── Colour helpers ─────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; BOLD='\033[1m'; RESET='\033[0m'

header() { echo -e "\n${BOLD}${CYAN}══════════════════════════════════════════════${RESET}"; \
           echo -e "${BOLD}${CYAN}  $1${RESET}"; \
           echo -e "${BOLD}${CYAN}══════════════════════════════════════════════${RESET}"; }

ok()   { echo -e "${GREEN}  ✔  $*${RESET}"; }
warn() { echo -e "${YELLOW}  ⚠  $*${RESET}"; }
err()  { echo -e "${RED}  ✗  $*${RESET}"; }

# ── Task 119a: List HDFS directory ────────────────────────────────
header "Task 119a — hdfs dfs -ls ${HDFS_PATH}"
echo ""
if hdfs dfs -ls -R "${HDFS_PATH}" 2>/dev/null; then
  ok "Listing succeeded."
else
  warn "Directory may not exist yet — waiting for Flume to start ingestion …"
fi

# ── Task 119b: Preview first file ────────────────────────────────
header "Task 119b — Preview first ingested file (first 10 lines)"
echo ""
FIRST_FILE=$(hdfs dfs -ls -R "${HDFS_PATH}" 2>/dev/null \
  | awk '/^-/{print $NF}' | head -1 || true)

if [ -n "${FIRST_FILE}" ]; then
  echo -e "${YELLOW}File: ${FIRST_FILE}${RESET}"
  hdfs dfs -cat "${FIRST_FILE}" | head -10
  ok "File preview complete."
else
  warn "No ingested files found yet. Wait for Flume to finish and re-run."
fi

# ── Task 120: Line count verification ────────────────────────────
header "Task 120 — Line count: hdfs dfs -cat ${HDFS_PATH}/*/* | wc -l"
echo ""
ACTUAL_LINES=$(hdfs dfs -cat "${HDFS_PATH}/"*/* 2>/dev/null | wc -l || echo 0)
echo -e "${BOLD}  Expected lines : ${EXPECTED_LINES}${RESET}"
echo -e "${BOLD}  Actual lines   : ${ACTUAL_LINES}${RESET}"

if [ "${ACTUAL_LINES}" -eq "${EXPECTED_LINES}" ]; then
  ok "✅  LINE COUNT MATCHES — Ingestion 100% successful!"
elif [ "${ACTUAL_LINES}" -gt 0 ]; then
  warn "Ingestion in progress. (${ACTUAL_LINES} / ${EXPECTED_LINES} lines so far)"
else
  err "No lines found. Check: docker logs flume-agent"
fi

# ── Summary ───────────────────────────────────────────────────────
header "Summary"
echo ""
echo -e "  HDFS Path          : ${CYAN}${HDFS_PATH}${RESET}"
echo -e "  Files ingested     : ${CYAN}$(hdfs dfs -ls -R ${HDFS_PATH} 2>/dev/null | grep '^-' | wc -l || echo 0)${RESET}"
echo -e "  Total HDFS lines   : ${CYAN}${ACTUAL_LINES}${RESET}"
echo -e "  Source log lines   : ${CYAN}${EXPECTED_LINES}${RESET}"
echo ""
echo -e "  Web UI  → ${CYAN}http://localhost:9870${RESET}  (NameNode)"
echo -e "  Web UI  → ${CYAN}http://localhost:9864${RESET}  (DataNode)"
echo ""
