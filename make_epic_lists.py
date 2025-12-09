import csv
import os

ROOT = "/data/leuven/380/vsc38053/RD_Project/epic-kitchens-data"
ANN_DIR = os.path.join(ROOT, "annotations")

def find_label_key(row, target="verb_class"):
    if target in row:
        return target
    candidates = [
        k for k in row.keys()
        if "verb" in k.lower() and "class" in k.lower()
    ]
    if not candidates:
        raise KeyError(
            f"Could not find a column for {target!r}. "
            f"Available keys: {list(row.keys())}"
        )
    return candidates[0]


def convert_labeled(csv_name, out_name):
    """Use when CSV has verb_class."""
    in_path = os.path.join(ANN_DIR, csv_name)
    out_path = os.path.join(ROOT, out_name)

    print(f"Reading (labeled): {in_path}")
    print(f"Writing:          {out_path}")

    with open(in_path, "r", newline="") as f_in, \
         open(out_path, "w", newline="") as f_out:

        reader = csv.DictReader(f_in)
        label_key = None

        for row in reader:
            if label_key is None:
                label_key = find_label_key(row, "verb_class")
                print(f"Using label column: {label_key}")

            video_id    = row["video_id"]
            start_frame = row["start_frame"]
            stop_frame  = row["stop_frame"]
            label       = row[label_key]

            video_path = f"{row['participant_id']}/{video_id}.MP4"
            line = f"{video_path} {label} {start_frame} {stop_frame}\n"
            f_out.write(line)


def convert_unlabeled(csv_name, out_name, dummy_label="0"):
    """Use when CSV has NO verb_class (validation set)."""
    in_path = os.path.join(ANN_DIR, csv_name)
    out_path = os.path.join(ROOT, out_name)

    print(f"Reading (UNlabeled): {in_path}")
    print(f"Writing:             {out_path}")
    print(f"Using dummy label:   {dummy_label}")

    with open(in_path, "r", newline="") as f_in, \
         open(out_path, "w", newline="") as f_out:

        reader = csv.DictReader(f_in)

        for row in reader:
            video_id    = row["video_id"]
            start_frame = row["start_frame"]
            stop_frame  = row["stop_frame"]
            label       = dummy_label  # fake label

            video_path = f"{row['participant_id']}/{video_id}.MP4"
            line = f"{video_path} {label} {start_frame} {stop_frame}\n"
            f_out.write(line)


if __name__ == "__main__":
    # Train: real labels
    convert_labeled("EPIC_100_train.csv", "epic100_train_verb_list.txt")

    # Val: no labels available → dummy 0
    convert_unlabeled("EPIC_100_validation.csv", "epic100_val_verb_list.txt", dummy_label="0")

    print("Done.")
