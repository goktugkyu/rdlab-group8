import csv
import json
from pathlib import Path

ROOT = Path("/data/leuven/380/vsc38053/RD_Project")
ANN_DIR = ROOT / "epic-kitchens-data" / "annotations"

TRAIN_CSV = ANN_DIR / "EPIC_100_train.csv"
# If your validation CSV is borked, we will just reuse train list for val later.
VAL_CSV = ANN_DIR / "EPIC_100_validation.csv"

OUT_TRAIN_LIST = ROOT / "epic-kitchens-data" / "epic100_train_action_list.txt"
OUT_VAL_LIST   = ROOT / "epic-kitchens-data" / "epic100_val_action_list.txt"
OUT_MAPPING    = ROOT / "epic-kitchens-data" / "epic100_action_mapping.json"


def build_action_lists():
    pair_to_id = {}
    id_to_pair = {}

    def process_csv(csv_path, out_txt_path, desc):
        print(f"Reading {desc} CSV:", csv_path)
        num_lines = 0
        missing = 0
    
        video_root = ROOT / "epic-kitchens-data" / "videos_640x360"
    
        with csv_path.open("r", newline="") as f_in, out_txt_path.open("w") as f_out:
            reader = csv.DictReader(f_in)
            required_cols = ["participant_id", "video_id", "verb_class", "noun_class"]
    
            for col in required_cols:
                if col not in reader.fieldnames:
                    raise KeyError(
                        f"Column '{col}' not found in {csv_path}. "
                        f"Available: {reader.fieldnames}"
                    )
    
            for row in reader:
                participant_id = row["participant_id"]     # e.g. "P01"
                video_id = row["video_id"]                 # e.g. "P01_01"
                verb = int(row["verb_class"])
                noun = int(row["noun_class"])
    
                # Relative video path and full path on disk
                video_rel_path = f"{participant_id}/{video_id}.MP4"
                full_path = video_root / video_rel_path
    
                # *** IMPORTANT: skip if video file is missing in the mini dataset ***
                if not full_path.is_file():
                    missing += 1
                    continue
    
                pair = (verb, noun)
                if pair not in pair_to_id:
                    action_id = len(pair_to_id)
                    pair_to_id[pair] = action_id
                    id_to_pair[action_id] = {"verb_class": verb, "noun_class": noun}
                else:
                    action_id = pair_to_id[pair]
    
                f_out.write(f"{video_rel_path} {action_id}\n")
                num_lines += 1
    
        print(f"  Wrote {num_lines} lines to {out_txt_path}")
        print(f"  Skipped {missing} segments (video file not found)")
        return num_lines


    # Process train first (builds the mapping)
    n_train = process_csv(TRAIN_CSV, OUT_TRAIN_LIST, "TRAIN")

    # Try to process validation; if it fails, we will reuse train file
    try:
        n_val = process_csv(VAL_CSV, OUT_VAL_LIST, "VAL")
    except Exception as e:
        print("\nWARNING: Could not process VAL CSV properly:", e)
        print("=> Reusing TRAIN action list as VAL for simplicity.")
        # Copy train list to val
        OUT_VAL_LIST.write_text(OUT_TRAIN_LIST.read_text())
        n_val = n_train

    num_actions = len(pair_to_id)
    print(f"\nTotal unique (verb, noun) pairs = {num_actions}")

    # Save mapping so we can decode predictions later
    mapping_obj = {
        "num_actions": num_actions,
        "pair_to_id": {f"{v}_{n}": aid for (v, n), aid in pair_to_id.items()},
        "id_to_pair": {str(aid): pair for aid, pair in id_to_pair.items()},
    }
    with OUT_MAPPING.open("w") as f_map:
        json.dump(mapping_obj, f_map, indent=2)

    print("Saved mapping to:", OUT_MAPPING)


if __name__ == "__main__":
    build_action_lists()
