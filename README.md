# Apache Flume Log Ingestion to HDFS
## GROUP 20 — Big Data Pipeline Project

A fully Dockerized pipeline that continuously ingests Apache web server access
logs from a **Spooling Directory** source through a **Memory Channel** into
**HDFS**, using Apache Flume 1.11 and Hadoop 3.3.

---

## Architecture

```
╔══════════════════╗   ╔═══════════════════╗   ╔══════════════════════════════╗
║  generate_logs.py║──▶║  Spooling Dir     ║──▶║  Flume Memory Channel        ║
║  (10,000 lines)  ║   ║  /opt/spooling_dir║   ║  capacity: 100,000 events    ║
╚══════════════════╝   ╚═══════════════════╝   ╚══════════════════════════════╝
                                                              │
                                                              ▼
                                              ╔══════════════════════════════╗
                                              ║  HDFS Sink                   ║
                                              ║  hdfs://namenode:9000        ║
                                              ║  /flume/logs/%Y-%m-%d/       ║
                                              ║  FileType: DataStream        ║
                                              ╚══════════════════════════════╝
```

---

## Project Structure

```
apache-flume-project/
├── Dockerfile              # Flume 1.11 + Hadoop 3.3 client image
├── docker-compose.yml      # NameNode + DataNode + Flume agent
├── flume.conf              # Flume pipeline configuration
├── core-site.xml           # Hadoop core config (NameNode URI)
├── hdfs-site.xml           # HDFS storage config (replication=1)
├── generate_logs.py        # Synthetic log generator (10,000 lines)
├── flume-entrypoint.sh     # Container startup script
├── verify-ingestion.sh     # HDFS verification script
├── spooling_dir/           # Host-mounted spooling directory
└── README.md               # This file
```

---

## Prerequisites

| Requirement   | Version  |
|---------------|----------|
| Docker        | 20.10+   |
| Docker Compose| 2.x      |
| RAM           | ≥ 4 GB   |
| Disk          | ≥ 5 GB   |

---

## Quick Start

### Step 1 — Clone / Enter the project directory
```bash
cd apache-flume-project
```

### Step 2 — Build and start all containers
```bash
docker compose up -d --build
```

> ⏳ First build downloads Flume + Hadoop (~600 MB). Allow 5–10 minutes.

### Step 3 — Watch Flume agent logs
```bash
docker logs -f flume-agent
```

You should see:
```
▶  [1/4] Waiting for HDFS NameNode …
✔  NameNode is UP.
▶  [2/4] Waiting for safe-mode to clear …
✔  Safe-mode is OFF.
▶  [3/4] Creating HDFS directory /flume/logs …
▶  [4/4] Generating 10,000 synthetic Apache log lines …
✔  Log file placed in /opt/spooling_dir/
Starting Flume agent 'agent' …
```

### Step 4 — Add more log files (optional, Task 118)
```bash
# Drop any new log file into the host-mounted spooling directory
cp my-extra-logs.log spooling_dir/
# Flume automatically picks it up within seconds
```

---

## Verification (Tasks 119 & 120)

### Option A — Using the verify script
```bash
# Copy and run verification script on the namenode container
docker cp verify-ingestion.sh namenode:/opt/
docker exec namenode bash /opt/verify-ingestion.sh
```

### Option B — Manual commands

#### Task 119 — List HDFS ingested files
```bash
docker exec namenode hdfs dfs -ls -R /flume/logs
```

Expected output:
```
drwxr-xr-x   - root supergroup          0 2025-01-15 10:30 /flume/logs/2025-01-15
-rw-r--r--   1 root supergroup     892341 2025-01-15 10:31 /flume/logs/2025-01-15/access-log-.log
```

#### Task 119 — Preview an ingested file
```bash
docker exec namenode hdfs dfs -cat /flume/logs/$(date +%Y-%m-%d)/access-log-.log | head -5
```

PowerShell:
```powershell
$today = Get-Date -Format 'yyyy-MM-dd'
docker exec namenode hdfs dfs -cat /flume/logs/$today/access-log-.log | Select-Object -First 5
```

Sample output:
```
10.0.0.12 - - [09/Jan/2025:03:27:15 +0530] "GET /api/v1/products HTTP/1.1" 200 14822 "-" "Mozilla/5.0 ..."
172.16.2.3 - - [09/Jan/2025:07:41:52 +0530] "POST /login HTTP/1.1" 201 512 "-" "curl/8.4.0"
...
```

#### Task 120 — Count total ingested lines
```bash
docker exec namenode bash -c "hdfs dfs -cat '/flume/logs/*/*' | wc -l"
```

PowerShell:
```powershell
docker exec namenode bash -c "hdfs dfs -cat '/flume/logs/*/*' | wc -l"
```

Expected:
```
10000
```

---

## Web UIs

| Service   | URL                      |
|-----------|--------------------------|
| NameNode  | http://localhost:9870    |
| DataNode  | http://localhost:9864    |

Navigate to **Utilities → Browse the file system** on the NameNode UI and
browse to `/flume/logs/` to see ingested files.

---

## Flume Pipeline Details

### Source — SpoolingDirectorySource
| Property        | Value                  |
|-----------------|------------------------|
| type            | `spooldir`             |
| spoolDir        | `/opt/spooling_dir`    |
| fileSuffix      | `.COMPLETED`           |
| deletePolicy    | `never`                |
| deserializer    | `LINE`                 |

### Channel — MemoryChannel
| Property             | Value    |
|----------------------|----------|
| type                 | `memory` |
| capacity             | 100,000  |
| transactionCapacity  | 10,000   |

### Sink — HDFSSink
| Property           | Value                              |
|--------------------|------------------------------------|
| type               | `hdfs`                             |
| hdfs.path          | `hdfs://namenode:9000/flume/logs/%Y-%m-%d` |
| hdfs.fileType      | `DataStream`                       |
| hdfs.writeFormat   | `Text`                             |
| hdfs.rollSize      | 128 MB                             |
| hdfs.rollInterval  | 600 seconds                        |
| hdfs.batchSize     | 10,000                             |

---

## Stopping the Pipeline

```bash
# Stop all containers
docker compose down

# Stop and remove all data volumes (full reset)
docker compose down -v
```

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| NameNode not ready | Wait 2–3 min; check `docker logs namenode` |
| Safe-mode ON | Run `docker exec namenode hdfs dfsadmin -safemode leave` |
| No files in HDFS | Check `docker logs flume-agent` for errors |
| Port conflict | Change host ports in `docker-compose.yml` |
| Build fails (download) | Check internet; retry `docker compose build` |

---

*Group 20 — Apache Flume Log Ingestion to HDFS | Big Data Systems*
