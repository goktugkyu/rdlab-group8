
import csv

import os



root = "epic-kitchens-data"

csv_path = os.path.join(root, "annotations", "EPIC_100_train.csv")

out_path = os.path.join(root, "epic100_train_verb_list.txt")



print("Reading:", csv_path)

print("Writing:", out_path)



with open(csv_path, newline="") as f, open(out_path, "w") as out:

    reader = csv.DictReader(f)

    print("CSV columns:", reader.fieldnames)



    # We know train CSV has `verb_class`

    if "verb_class" not in reader.fieldnames:

        raise KeyError(f"'verb_class' not in CSV columns: {reader.fieldnames}")



    for row in reader:

        pid = row["participant_id"]   # e.g. P01

        vid = row["video_id"]         # e.g. P01_01

        label = row["verb_class"]     # e.g. 3



        # Format: "P01/P01_01.MP4 3"

        out.write(f"{pid}/{vid}.MP4 {label}\n")



print("Done.")


