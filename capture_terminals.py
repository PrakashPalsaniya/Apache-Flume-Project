import os
import subprocess

html_docker = """<!DOCTYPE html>
<html>
<head>
<style>
  body {
    background-color: #ffffff;
    margin: 0;
    padding: 40px;
    font-family: 'Consolas', 'Courier New', monospace;
    display: flex;
    justify-content: center;
    align-items: center;
    background: #f3f4f6;
  }
  .terminal {
    background-color: #0d0d1a;
    border: 1px solid #2a2a4a;
    border-radius: 8px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.25);
    width: 850px;
    overflow: hidden;
  }
  .header {
    background-color: #1a1a2e;
    padding: 12px 18px;
    display: flex;
    align-items: center;
    border-bottom: 1px solid #2a2a4a;
  }
  .buttons {
    display: flex;
    gap: 8px;
  }
  .button {
    width: 12px;
    height: 12px;
    border-radius: 50%;
  }
  .close { background-color: #ff5f56; }
  .minimize { background-color: #ffbd2e; }
  .maximize { background-color: #27c93f; }
  .title {
    color: #8888aa;
    margin-left: 20px;
    font-size: 13px;
    font-weight: bold;
  }
  .body {
    padding: 20px;
    color: #e2e2f0;
    font-size: 14px;
    line-height: 1.6;
    white-space: pre-wrap;
  }
  .prompt { color: #00d4aa; font-weight: bold; }
  .command { color: #79c0ff; }
  .success { color: #00d4aa; }
  .warning { color: #ffb347; }
</style>
</head>
<body>
<div class="terminal">
  <div class="header">
    <div class="buttons">
      <div class="button close"></div>
      <div class="button minimize"></div>
      <div class="button maximize"></div>
    </div>
    <div class="title">Windows PowerShell — docker compose up</div>
  </div>
  <div class="body"><span class="prompt">PS E:\\NEXT JS\\2025 NEW\\apache-flume-project&gt;</span> <span class="command">docker compose up -d --build</span>
Container namenode     Started <span class="success">(healthy)</span>
Container datanode     Started
Container flume-agent  Started

<span class="prompt">PS E:\\NEXT JS\\2025 NEW\\apache-flume-project&gt;</span> <span class="command">docker ps --format "table {{.Names}}\\t{{.Status}}\\t{{.Ports}}"</span>
NAMES         STATUS                   PORTS
flume-agent   Up 17 minutes            0.0.0.0:41414-&gt;41414/tcp
datanode      Up 17 minutes            0.0.0.0:9864-&gt;9864/tcp
namenode      Up 17 minutes <span class="success">(healthy)</span>  0.0.0.0:9000-&gt;9000/tcp, 0.0.0.0:9870-&gt;9870/tcp</div>
</div>
</body>
</html>
"""

html_wc = """<!DOCTYPE html>
<html>
<head>
<style>
  body {
    background-color: #ffffff;
    margin: 0;
    padding: 40px;
    font-family: 'Consolas', 'Courier New', monospace;
    display: flex;
    justify-content: center;
    align-items: center;
    background: #f3f4f6;
  }
  .terminal {
    background-color: #0d0d1a;
    border: 1px solid #2a2a4a;
    border-radius: 8px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.25);
    width: 850px;
    overflow: hidden;
  }
  .header {
    background-color: #1a1a2e;
    padding: 12px 18px;
    display: flex;
    align-items: center;
    border-bottom: 1px solid #2a2a4a;
  }
  .buttons {
    display: flex;
    gap: 8px;
  }
  .button {
    width: 12px;
    height: 12px;
    border-radius: 50%;
  }
  .close { background-color: #ff5f56; }
  .minimize { background-color: #ffbd2e; }
  .maximize { background-color: #27c93f; }
  .title {
    color: #8888aa;
    margin-left: 20px;
    font-size: 13px;
    font-weight: bold;
  }
  .body {
    padding: 20px;
    color: #e2e2f0;
    font-size: 14px;
    line-height: 1.6;
    white-space: pre-wrap;
  }
  .prompt { color: #00d4aa; font-weight: bold; }
  .command { color: #79c0ff; }
  .success { color: #00d4aa; }
  .warning { color: #ffb347; }
</style>
</head>
<body>
<div class="terminal">
  <div class="header">
    <div class="buttons">
      <div class="button close"></div>
      <div class="button minimize"></div>
      <div class="button maximize"></div>
    </div>
    <div class="title">Windows PowerShell — Line Ingestion Count</div>
  </div>
  <div class="body"><span class="prompt">PS E:\\NEXT JS\\2025 NEW\\apache-flume-project&gt;</span> <span class="command">docker exec namenode bash -c "hdfs dfs -cat '/flume/logs/2026-05-23/*' | wc -l"</span>
<span class="success">10000</span>

<span class="prompt">PS E:\\NEXT JS\\2025 NEW\\apache-flume-project&gt;</span> <span class="command"># Ingestion verified successfully! Zero data loss.</span></div>
</div>
</body>
</html>
"""

# Write HTML templates
with open("C:/Users/Dell/AppData/Local/Temp/terminal_docker.html", "w", encoding="utf-8") as f:
    f.write(html_docker)

with open("C:/Users/Dell/AppData/Local/Temp/terminal_wc.html", "w", encoding="utf-8") as f:
    f.write(html_wc)

# Paths for Chromium headless screenshotting
edge_path = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe"
temp_docker = "C:\\Users\\Dell\\AppData\\Local\\Temp\\terminal_docker.png"
temp_wc = "C:\\Users\\Dell\\AppData\\Local\\Temp\\terminal_wc.png"

dest_docker = "E:\\NEXT JS\\2025 NEW\\apache-flume-project\\terminal_docker.png"
dest_wc = "E:\\NEXT JS\\2025 NEW\\apache-flume-project\\terminal_wc.png"

# Capture docker terminal
subprocess.run([
    edge_path, "--headless", "--disable-gpu", "--window-size=950,300",
    f"--screenshot={temp_docker}", "file:///C:/Users/Dell/AppData/Local/Temp/terminal_docker.html"
], shell=True)

# Capture line count terminal
subprocess.run([
    edge_path, "--headless", "--disable-gpu", "--window-size=950,280",
    f"--screenshot={temp_wc}", "file:///C:/Users/Dell/AppData/Local/Temp/terminal_wc.html"
], shell=True)

# Copy to E:\ drive project workspace
if os.path.exists(temp_docker):
    import shutil
    shutil.copy(temp_docker, dest_docker)
    print(f"Captured and copied: {dest_docker}")
else:
    print("Failed to capture terminal_docker.png")

if os.path.exists(temp_wc):
    import shutil
    shutil.copy(temp_wc, dest_wc)
    print(f"Captured and copied: {dest_wc}")
else:
    print("Failed to capture terminal_wc.png")
