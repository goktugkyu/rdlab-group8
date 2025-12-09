#!/usr/bin/env python
import os
import csv
import json
import numpy as np
import torch

# ---- Adjust root once and forget about paths ----
PROJECT_ROOT = "/data/leuven/380/vsc38053/RD_Project"
ANN_ROOT = os.path.join(PROJECT_ROOT, "epic-kitchens-data", "annotations")
VIDEO_ROOT = os.path.join(PROJECT_ROOT, "epic-kitchens-data", "videos_640x360")

TRAIN_CSV = os.path.join(ANN_ROOT, "EPIC_100_train.csv")
VAL_CSV = os.path.join(ANN_ROOT, "EPIC_100_validation.csv")

OUT_TRAIN = os.path.join(PROJECT_ROOT, "epic-kitchens-data", "epic100_train_action_list.txt")
OUT_VAL = os.path.join(PROJECT_ROOT, "epic-kitchens-data", "epic100_val_action_list.txt")
OUT_STATS = os.path.join(PROJECT_ROOT, "epic-kitchens-data", "epic100_action_stats.json")

MAPPING_PATH = os.path.join(PROJECT_ROOT, "epic-kitchens-data", "epic100_pair2verbnoun.pt")


def check_video_exists(participant_id: str, video_id: str) -> tuple[str, bool]:
    """Build relative path like 'P01/P01_01.MP4' and check if file exists."""
    rel_path = f"{participant_id}/{video_id}.MP4"
    full_path = os.path.join(VIDEO_ROOT, rel_path)
    return rel_path, os.path.exists(full_path)


def build_train_list():
    """
    Build TRAIN list and pair mapping.

    For each valid row:
      - assign a pair_id to (verb_id, noun_id)
      - write: <video_rel_path> <pair_id>
    """
    print(f"Reading TRAIN CSV: {TRAIN_CSV}")
    num_rows = 0
    num_used = 0
    num_missing_video = 0
    verbs = set()
    nouns = set()
    actions = set()

    # mapping (verb_id, noun_id) -> pair_id
    pair2id = {}

    with open(TRAIN_CSV, "r") as f_in, open(OUT_TRAIN, "w") as f_out:
        reader = csv.DictReader(f_in)
        required_cols = [
            "narration_id",
            "participant_id",
            "video_id",
            "verb_class",
            "noun_class",
        ]
        for c in required_cols:
            if c not in reader.fieldnames:
                raise RuntimeError(
                    f"Column '{c}' not found in TRAIN CSV. "
                    f"Available: {reader.fieldnames}"
                )

        for row in reader:
            num_rows += 1
            participant_id = row["participant_id"]
            video_id = row["video_id"]
            verb_str = row["verb_class"]
            noun_str = row["noun_class"]

            if verb_str == "" or noun_str == "":
                continue

            try:
                verb_id = int(verb_str)
                noun_id = int(noun_str)
            except ValueError:
                continue

            rel_path, exists = check_video_exists(participant_id, video_id)
            if not exists:
                num_missing_video += 1
                continue

            key = (verb_id, noun_id)
            if key not in pair2id:
                pair2id[key] = len(pair2id)
            pair_id = pair2id[key]

            # *** IMPORTANT: exactly 2 columns: <video_path> <pair_id> ***
            f_out.write(f"{rel_path} {pair_id}\n")

            num_used += 1
            verbs.add(verb_id)
            nouns.add(noun_id)
            actions.add((verb_id, noun_id))

    print(f"  Total rows in TRAIN CSV: {num_rows}")
    print(f"  Used rows (video exists): {num_used}")
    print(f"  Skipped because video missing: {num_missing_video}")
    print(f"  Unique verbs: {len(verbs)}")
    print(f"  Unique nouns: {len(nouns)}")
    print(f"  Unique (verb, noun) pairs: {len(actions)}")

    # save pair_id -> verb/noun mapping
    num_pairs = len(pair2id)
    pair2verb = np.zeros(num_pairs, dtype=np.int64)
    pair2noun = np.zeros(num_pairs, dtype=np.int64)

    for (verb_id, noun_id), pid in pair2id.items():
        pair2verb[pid] = verb_id
        pair2noun[pid] = noun_id

    os.makedirs(os.path.dirname(MAPPING_PATH), exist_ok=True)
    torch.save(
        {
            "pair2verb": torch.from_numpy(pair2verb),
            "pair2noun": torch.from_numpy(pair2noun),
        },
        MAPPING_PATH,
    )

    print(f"Saved pair->verb/noun mapping to: {MAPPING_PATH}")
    print(f"  num_pairs: {num_pairs}")
    print(f"  max verb id: {pair2verb.max()}")
    print(f"  max noun id: {pair2noun.max()}")

    return {
        "train_total_rows": num_rows,
        "train_used": num_used,
        "train_missing_video": num_missing_video,
        "num_verbs_in_train": len(verbs),
        "num_nouns_in_train": len(nouns),
        "num_actions_in_train": len(actions),
        "num_pairs": num_pairs,
    }


def build_val_list():
    """
    Build VAL list in VideoDataset format:
      <video_rel_path> <label>

    We don't have labels there, so we use -1 as dummy label.
    """
    print(f"Reading VAL CSV: {VAL_CSV}")
    num_rows = 0
    num_used = 0
    num_missing_video = 0

    with open(VAL_CSV, "r") as f_in, open(OUT_VAL, "w") as f_out:
        reader = csv.DictReader(f_in)

        required_cols = [
            "narration_id",
            "participant_id",
            "video_id",
        ]
        for c in required_cols:
            if c not in reader.fieldnames:
                raise RuntimeError(
                    f"Column '{c}' not found in VAL CSV. "
                    f"Available: {reader.fieldnames}"
                )

        for row in reader:
            num_rows += 1
            participant_id = row["participant_id"]
            video_id = row["video_id"]

            rel_path, exists = check_video_exists(participant_id, video_id)
            if not exists:
                num_missing_video += 1
                continue

            # exactly 2 columns: <video_path> <label>, label = -1 (dummy)
            f_out.write(f"{rel_path} -1\n")
            num_used += 1

    print(f"  Total rows in VAL CSV: {num_rows}")
    print(f"  Used rows (video exists): {num_used}")
    print(f"  Skipped because video missing: {num_missing_video}")

    return {
        "val_total_rows": num_rows,
        "val_used": num_used,
        "val_missing_video": num_missing_video,
    }


def main():
    os.makedirs(os.path.dirname(OUT_TRAIN), exist_ok=True)

    stats = {}
    stats.update(build_train_list())
    stats.update(build_val_list())

    print("\nSaving stats to:", OUT_STATS)
    with open(OUT_STATS, "w") as f:
        json.dump(stats, f, indent=2)


if __name__ == "__main__":
    main()
