import csv
from pathlib import Path

# Root of your EPIC data under RD_Project
ROOT = Path("epic-kitchens-data")
ANNO_DIR = ROOT / "annotations"

def make_list(csv_name: str, out_name: str):
    csv_path = ANNO_DIR / csv_name
    out_path = ROOT / out_name

    print(f"Reading: {csv_path}")
    print(f"Writing: {out_path}")

    with open(csv_path, "r") as f_in, open(out_path, "w") as f_out:
        reader = csv.DictReader(f_in)
        for row in reader:
            # EPIC columns
            pid = row["participant_id"]   # e.g. "P04"
            vid = row["video_id"]         # e.g. "P04_113"
            label = row["verb_class"]     # e.g. "3"

            # IMPORTANT: include participant folder
            filename = f"{pid}/{vid}.MP4"
            line = f"{filename} {label}\n"
            f_out.write(line)

    print("Done.")

if __name__ == "__main__":
    make_list("EPIC_100_train.csv",      "epic100_train_verb_list.txt")
    make_list("EPIC_100_validation.csv", "epic100_val_verb_list.txt")
