#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════
#  flume-entrypoint.sh
#  Runs inside the apache/flume container:
#    1. Waits for HDFS NameNode to leave safe-mode
#    2. Creates the /flume/logs directory in HDFS
#    3. Runs generate_logs.py to fill the spooling directory
#    4. Starts the Flume agent
# ═══════════════════════════════════════════════════════════════════
set -euo pipefail

NAMENODE="namenode"
HDFS_URI="hdfs://${NAMENODE}:9000"
MAX_WAIT=180   # seconds to wait for NameNode

echo "╔══════════════════════════════════════════════════════╗"
echo "║          Apache Flume — Log Ingestion Agent          ║"
echo "║               GROUP 20 — Big Data                    ║"
echo "╚══════════════════════════════════════════════════════╝"

# ── 1. Wait for NameNode TCP ───────────────────────────────────────
echo ""
echo "▶  [1/4] Waiting for NameNode TCP at ${NAMENODE}:9000 …"
elapsed=0
until nc -z "${NAMENODE}" 9000 2>/dev/null; do
  if [ $elapsed -ge $MAX_WAIT ]; then
    echo "✗  NameNode TCP not reachable after ${MAX_WAIT}s — aborting."
    exit 1
  fi
  echo "   … still waiting (${elapsed}s)"
  sleep 5
  elapsed=$((elapsed + 5))
done
echo "✔  NameNode TCP is UP."

# ── 2. Wait for safe-mode to clear ────────────────────────────────
echo ""
echo "▶  [2/4] Waiting for NameNode to leave safe-mode …"
elapsed=0
until hdfs dfsadmin -fs "${HDFS_URI}" -safemode get 2>&1 | grep -q "Safe mode is OFF"; do
  if [ $elapsed -ge $MAX_WAIT ]; then
    echo "✗  Safe-mode not cleared after ${MAX_WAIT}s — forcing leave."
    hdfs dfsadmin -fs "${HDFS_URI}" -safemode leave 2>/dev/null || true
    break
  fi
  echo "   … safe-mode still ON (${elapsed}s)"
  sleep 5
  elapsed=$((elapsed + 5))
done
echo "✔  Safe-mode is OFF."

# ── 3. Create HDFS directories ─────────────────────────────────────
echo ""
echo "▶  [3/4] Creating HDFS directory /flume/logs …"
hdfs dfs -fs "${HDFS_URI}" -mkdir -p /flume/logs 2>/dev/null || true
hdfs dfs -fs "${HDFS_URI}" -chmod -R 777 /flume      2>/dev/null || true
echo "  HDFS directory listing:"
hdfs dfs -fs "${HDFS_URI}" -ls / || true
echo "✔  HDFS directories ready."

# ── 4. Generate synthetic log file ────────────────────────────────
echo ""
echo "▶  [4/4] Generating 10,000 synthetic Apache log lines …"
mkdir -p /opt/spooling_dir
python3 /opt/generate_logs.py
echo "  Files in spooling directory:"
ls -lh /opt/spooling_dir/
echo "✔  Log file ready."

# ── 5. Start Flume agent ───────────────────────────────────────────
echo ""
echo "══════════════════════════════════════════════════════"
echo "  Starting Flume agent 'agent' …"
echo "  Source  : /opt/spooling_dir  (SpoolDir)"
echo "  Channel : Memory (100,000 capacity)"
echo "  Sink    : ${HDFS_URI}/flume/logs/%Y-%m-%d"
echo "══════════════════════════════════════════════════════"
echo ""

exec /opt/flume/bin/flume-ng agent \
  --name agent \
  --conf /opt/flume/conf \
  --conf-file /opt/flume/conf/flume.conf \
  -Dflume.root.logger=INFO,console \
  -Dorg.apache.flume.log.rawdata=true
