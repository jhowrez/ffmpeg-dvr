ffmpeg-dvr — Timed RTSP Recorder

Overview
--------
ffmpeg-dvr.py is a Python utility that automatically records an RTSP stream between two scheduled timestamps. It launches ffmpeg, writes recordings with timestamped filenames, and stops once the period finishes.

Features
--------
- Schedule recording start/end times
- Auto-generates timestamped output filenames
- Uses ffmpeg via a subprocess (zero re-encode overhead)
- Automatically stops when the period ends
- Works on Linux/Mac/Windows
- Simple CLI interface

Requirements
-----------
- Python 3.8+
- ffmpeg installed and accessible in PATH
- Accessible RTSP stream URL

Running Online
--------------
You can run the script directly from a URL:

python3 <(wget -qO- https://raw.githubusercontent.com/jhowrez/ffmpeg-dvr/refs/heads/main/ffmpeg-dvr.py) --help

Usage
-----
usage: ffmpeg-dvr.py [-h] [-ts START] [-te END] [-c CMD] [-o OUTPUT]
                     -i URL -n PREFIX [-d | --exit | --no-exit]

Examples
--------
python3 ffmpeg-dvr.py \\
    -i rtsp://192.168.1.15/live \\
    -n driveway \\
    -ts "25/01/2025 14:00:00 +0000" \\
    -te "25/01/2025 14:30:00 +0000"

This produces:
recs/driveway.25-01-2025.14-00-00.mp4
