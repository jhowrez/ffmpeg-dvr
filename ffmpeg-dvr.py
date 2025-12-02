import argparse
import pathlib
import shlex
import time
from datetime import datetime, timedelta
from subprocess import PIPE, Popen, TimeoutExpired

# Constants
TIME_FORMAT = "%d/%m/%Y %H:%M:%S %z"
FILENAME_FORMAT = "%d-%m-%Y.%H-%M-%S"

# Default values
now = datetime.now().astimezone()
DEFAULT_START_TIME_STR = now.strftime(TIME_FORMAT)
DEFAULT_END_TIME_STR = (now + timedelta(hours=1)).strftime(TIME_FORMAT)


def parse_args():
    parser = argparse.ArgumentParser(description="Timed RTSP recorder using ffmpeg.")
    parser.add_argument("-ts", "--start", default=DEFAULT_START_TIME_STR,
                        help="Start time (format: dd/mm/yyyy hh:mm:ss ±zzzz)")
    parser.add_argument("-te", "--end", default=DEFAULT_END_TIME_STR,
                        help="End time (format: dd/mm/yyyy hh:mm:ss ±zzzz)")
    parser.add_argument("-c", "--cmd", default="ffmpeg", help="ffmpeg command")
    parser.add_argument("-o", "--output", default="recs", help="Output directory")
    parser.add_argument("-i", "--url", required=True, help="RTSP stream URL")
    parser.add_argument("-n", "--prefix", required=True, help="Output filename prefix")
    parser.add_argument("-d", "--exit", action=argparse.BooleanOptionalAction, default=True,
                        help="Exit when recording period ends (default: True)")
    return parser.parse_args()


def parse_datetime(ts_str: str) -> datetime:
    return datetime.strptime(ts_str, TIME_FORMAT)


def ensure_output_dir(path: str):
    try:
        pathlib.Path(path).mkdir(parents=True, exist_ok=True)
    except Exception as e:
        raise RuntimeError(f"Failed to create output directory '{path}': {e}")


def should_record(ts_start: datetime, ts_end: datetime) -> bool:
    now = datetime.now().astimezone()
    return ts_start <= now <= ts_end


def generate_filename(prefix: str, output_dir: str) -> str:
    timestamp = datetime.now().astimezone().strftime(FILENAME_FORMAT)
    filename = f"{prefix}.{timestamp}.mp4"
    return str(pathlib.Path(output_dir) / filename)


def ffmpeg_start(ffmpeg_cmd: str, url: str, filename: str) -> Popen:
    cmd_args = shlex.split(
        f"{ffmpeg_cmd} -hide_banner -loglevel error -y -timeout 5000000 "
        f"-rtsp_transport tcp -i {url} -c copy {filename}"
    )
    print(f"Starting ffmpeg: {' '.join(cmd_args)}")
    process = Popen(cmd_args, stdout=PIPE, stderr=PIPE, stdin=PIPE, text=True)
    print(f"Recording to {filename}")
    return process


def ffmpeg_stop(process: Popen):
    if process and process.poll() is None:
        try:
            process.communicate("q\n", timeout=3)
            process.wait(timeout=5)
        except TimeoutExpired:
            process.terminate()
            print("Process forcefully terminated after timeout.")


def main():
    args = parse_args()

    ts_start = parse_datetime(args.start)
    ts_end = parse_datetime(args.end)

    if ts_end <= ts_start:
        raise ValueError("End time must be after start time.")

    ensure_output_dir(args.output)

    while True:
        if not should_record(ts_start, ts_end):
            if datetime.now().astimezone() > ts_end and args.exit:
                print("Recording period finished. Exiting...")
                break
            print("Waiting for recording period...")
            time.sleep(5)
            continue

        filename = generate_filename(args.prefix, args.output)
        process = ffmpeg_start(args.cmd, args.url, filename)

        while True:
            time.sleep(1)
            if process.poll() is not None:
                print("ffmpeg process exited early.")
                break
            if not should_record(ts_start, ts_end):
                print("Recording period ended.")
                break

        ffmpeg_stop(process)


if __name__ == "__main__":
    main()