import os
import pandas as pd

# === CONFIG: adjust paths if needed ===
CSV_PATH = "epic-kitchens-data/annotations/EPIC_100_train.csv"
VIDEO_ROOT = "/data/leuven/380/vsc38053/RD_Project/epic-kitchens-data/videos_640x360"
OUT_TXT = "epic_rgb_train_segments_full.txt"


# Column names from your CSV
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

    missing_files = 0
    used_rows = 0

    with open(OUT_TXT, "w") as f:
        for _, row in df.iterrows():
            pid = row[PART_COL]          # e.g. 'P01'
            vid = row[VID_COL]           # e.g. 'P01_01'
            verb = int(row[VERB_CLASS_COL])
            noun = int(row[NOUN_CLASS_COL])
            start_f = int(row[START_FRAME_COL])
            stop_f = int(row[STOP_FRAME_COL])

            # Try .MP4 first, then .mp4
            video_path_mp4 = os.path.join(VIDEO_ROOT, pid, f"{vid}.MP4")
            video_path_mp4_lower = os.path.join(VIDEO_ROOT, pid, f"{vid}.mp4")

            if os.path.exists(video_path_mp4):
                video_path = video_path_mp4
            elif os.path.exists(video_path_mp4_lower):
                video_path = video_path_mp4_lower
            else:
                missing_files += 1
                # Uncomment to debug:
                # print("Missing video:", video_path_mp4, "and", video_path_mp4_lower)
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
