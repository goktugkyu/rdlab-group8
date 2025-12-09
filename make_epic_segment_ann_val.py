
import os

import pandas as pd



CSV_PATH = "epic-kitchens-data/annotations/EPIC_100_validation.csv"

VIDEO_ROOT = "epic-kitchens-data/videos_640x360"

OUT_TXT = "epic_rgb_val_segments_full.txt"



PART_COL = "participant_id"

VID_COL = "video_id"

VERB_CLASS_COL = "verb_class"

NOUN_CLASS_COL = "noun_class"

START_FRAME_COL = "start_frame"

STOP_FRAME_COL = "stop_frame"



def main():

    print(f"Reading CSV: {CSV_PATH}")

    df = pd.read_csv(CSV_PATH)

    print(f"Total rows in CSV: {len(df)}")



    used_rows = 0

    missing_files = 0



    with open(OUT_TXT, "w") as f:

        for _, row in df.iterrows():

            pid = row[PART_COL]

            vid = row[VID_COL]

            verb = int(row[VERB_CLASS_COL])

            noun = int(row[NOUN_CLASS_COL])

            start_f = int(row[START_FRAME_COL])

            stop_f = int(row[STOP_FRAME_COL])



            video_path = os.path.join(VIDEO_ROOT, pid, f"{vid}.MP4")



            if not os.path.exists(video_path):

                missing_files += 1

                continue



            used_rows += 1

            line = f"{video_path} {start_f} {stop_f} {verb} {noun}\n"

            f.write(line)



    print("Done.")

    print("  Used rows (video exists):", used_rows)

    print("  Skipped (video missing):", missing_files)

    print("  Wrote annotation file:", OUT_TXT)



if __name__ == "__main__":

    main()


