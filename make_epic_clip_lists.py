import csv
import json
import os
from collections import defaultdict

# -----------------------------
# Paths
# -----------------------------
ROOT = "/data/leuven/380/vsc38053/RD_Project/epic-kitchens-data/annotations"
CSV_PATH = os.path.join(ROOT, "train_clips_all.csv")

OUT_DIR = os.path.join(ROOT, "epic-kitchens-data")
TRAIN_LIST = os.path.join(OUT_DIR, "epic100_train_action_list.txt")
VAL_LIST = os.path.join(OUT_DIR, "epic100_val_action_list.txt")
PAIR_MAP_JSON = os.path.join(OUT_DIR, "epic100_clip_pair_mapping.json")
STATS_JSON = os.path.join(OUT_DIR, "epic100_clip_action_stats.json")

# -----------------------------
# Read CSV
# -----------------------------
clips = []
with open(CSV_PATH, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        clips.append(row)

print(f"Total clips in CSV: {len(clips)}")

# -----------------------------
# Build pair mapping
# -----------------------------
pair2id = {}
id2pair = {}
pair_counts = defaultdict(int)
verbs = set()
nouns = set()

for row in clips:
    v = int(row["verb_class"])
    n = int(row["noun_class"])
    pair_key = (v, n)

    if pair_key not in pair2id:
        pair_id = len(pair2id)
        pair2id[pair_key] = pair_id
        id2pair[pair_id] = {"verb_class": v, "noun_class": n}

    pair_counts[pair_key] += 1
    verbs.add(v)
    nouns.add(n)

num_pairs = len(pair2id)
print(f"Unique verbs: {len(verbs)}")
print(f"Unique nouns: {len(nouns)}")
print(f"Unique (verb, noun) pairs: {num_pairs}")

os.makedirs(OUT_DIR, exist_ok=True)

# -----------------------------
# Deterministic train/val split
#   - split by video_id (so clips from a video
#     go all to train OR all to val)
#   - approx 80/20: every 5th video -> val
# -----------------------------
video_ids = sorted({row["video_id"] for row in clips})
train_videos = set()
val_videos = set()

for idx, vid in enumerate(video_ids):
    # 1 in 5 videos -> val
    if idx % 5 == 0:
        val_videos.add(vid)
    else:
        train_videos.add(vid)

print(f"Total unique videos: {len(video_ids)}")
print(f"  Train videos: {len(train_videos)}")
print(f"  Val videos:   {len(val_videos)}")

train_count = 0
val_count = 0

with open(TRAIN_LIST, "w", encoding="utf-8") as ft, \
     open(VAL_LIST, "w", encoding="utf-8") as fv:

    for row in clips:
        pid = row["participant_id"]
        vid = row["video_id"]      # e.g. P01_01_a0001
        v = int(row["verb_class"])
        n = int(row["noun_class"])
        pair_id = pair2id[(v, n)]

        rel_path = f"{pid}/{vid}.MP4"   # adjust extension if needed

        line = f"{rel_path} {pair_id}\n"

        if vid in val_videos:
            fv.write(line)
            val_count += 1
        else:
            ft.write(line)
            train_count += 1

print(f"Train clips written: {train_count}")
print(f"Val   clips written: {val_count}")

# -----------------------------
# Save mapping + stats
# -----------------------------
with open(PAIR_MAP_JSON, "w", encoding="utf-8") as f:
    json.dump(
        {
            "num_pairs": num_pairs,
            "id2pair": id2pair,
        },
        f,
        indent=2,
    )

with open(STATS_JSON, "w", encoding="utf-8") as f:
    json.dump(
        {
            "num_clips": len(clips),
            "num_verbs": len(verbs),
            "num_nouns": len(nouns),
            "num_pairs": num_pairs,
            "pair_counts": {
                f"{v}_{n}": c for (v, n), c in pair_counts.items()
            },
        },
        f,
        indent=2,
    )

print(f"Wrote train list to: {TRAIN_LIST}")
print(f"Wrote val   list to: {VAL_LIST}")
print(f"Wrote pair mapping to: {PAIR_MAP_JSON}")
print(f"Wrote stats to: {STATS_JSON}")
