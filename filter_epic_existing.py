
import os



ROOT = "epic-kitchens-data/videos_640x360"

SPLITS = [

    ("epic100_train_verb_list.txt", "epic100_train_verb_list_exist.txt"),

    ("epic100_val_verb_list.txt", "epic100_val_verb_list_exist.txt"),

]



for in_name, out_name in SPLITS:

    in_path = os.path.join("epic-kitchens-data", in_name)

    out_path = os.path.join("epic-kitchens-data", out_name)



    kept = 0

    skipped = 0



    print(f"Processing {in_path} -> {out_path}")



    with open(in_path, "r") as fin, open(out_path, "w") as fout:

        for line in fin:

            line = line.strip()

            if not line:

                continue

            try:

                rel_path, label = line.split()

            except ValueError:

                print("Bad line (skipping):", line)

                skipped += 1

                continue



            full_path = os.path.join(ROOT, rel_path)

            if os.path.exists(full_path):

                fout.write(line + "\n")

                kept += 1

            else:

                # Uncomment the next line if you want to see which files are missing

                # print("Missing video:", full_path)

                skipped += 1



    print(f"  Kept {kept} lines, skipped {skipped} (missing videos)")


