import os
import ssl
import csv
from irods.session import iRODSSession

IRODS_BASE_PATH = "/set/home/ciis-lab/datasets/epic-kitchens/videos_640x360"
VAL_CSV = "/data/leuven/380/vsc38053/RD_Project/epic-kitchens-data/annotations/EPIC_100_validation.csv"

LOCAL_BASE_ROOT = os.path.join(os.environ["VSC_SCRATCH"], "EPIC-val/videos_640x360")
os.makedirs(LOCAL_BASE_ROOT, exist_ok=True)

videos = set()

with open(VAL_CSV, newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
        pid = row["participant_id"]   # e.g. "P01"
        vid = row["video_id"]         # e.g. "P01_101"
        videos.add((pid, vid))

print(f"Found {len(videos)} unique videos in validation CSV.")

try:
    env_file = os.environ["IRODS_ENVIRONMENT_FILE"]
except KeyError:
    env_file = os.path.expanduser("~/.irods/irods_environment.json")

ssl_context = ssl.create_default_context(
    purpose=ssl.Purpose.SERVER_AUTH,
    cafile=None,
    capath=None,
    cadata=None,
)
ssl_settings = {"ssl_context": ssl_context}

with iRODSSession(irods_env_file=env_file, **ssl_settings) as session:
    for idx, (pid, vid) in enumerate(sorted(videos), start=1):
        remote_dir = f"{IRODS_BASE_PATH}/{pid}"
        local_dir = os.path.join(LOCAL_BASE_ROOT, pid)
        os.makedirs(local_dir, exist_ok=True)

        candidates = [f"{vid}.MP4", f"{vid}.mp4"]

        downloaded = False
        for fname in candidates:
            local_path = os.path.join(local_dir, fname)
            if os.path.exists(local_path):
                print(f"[{idx}/{len(videos)}] Already have {local_path}, skipping.")
                downloaded = True
                break

            remote_path = f"{remote_dir}/{fname}"
            try:
                print(f"[{idx}/{len(videos)}] Downloading {remote_path} -> {local_path}")
                session.data_objects.get(remote_path, local_path)
                downloaded = True
                break
            except Exception as e:
                print(f"   Could not get {remote_path}: {e}")

        if not downloaded:
            print(f"!!! WARNING: Could not download any variant for {pid}, {vid}")
