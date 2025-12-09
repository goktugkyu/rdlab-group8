
import os



ANN_IN = "epic_rgb_train_segments_train.txt"

ANN_OUT = "epic_rgb_train_segments_train_clean.txt"

BAD_LIST = "bad_rel_videos.txt"



# Load bad video relative paths into a set

with open(BAD_LIST, "r") as f:

    bad_rel = {line.strip() for line in f if line.strip()}



print("Loaded", len(bad_rel), "bad videos")



def rel_from_full(path: str) -> str:

    """

    Convert e.g.

      epic-kitchens-data/videos_640x360/P22/P22_103.MP4

    -> P22/P22_103.MP4

    """

    marker = "epic-kitchens-data/videos_640x360/"

    if marker in path:

        return path.split(marker, 1)[1]

    # fallback: just take last two components (Pxx / Pxx_yyy.MP4)

    parts = path.split("/")

    if len(parts) >= 2:

        return "/".join(parts[-2:])

    return path



kept = 0

skipped = 0



with open(ANN_IN, "r") as fin, open(ANN_OUT, "w") as fout:

    for line in fin:

        line = line.strip()

        if not line:

            continue

        parts = line.split()

        video_path = parts[0]



        rel = rel_from_full(video_path)



        if rel in bad_rel:

            skipped += 1

            continue



        kept += 1

        fout.write(line + "\n")



print("Done.")

print("  Kept segments:   ", kept)

print("  Skipped segments:", skipped)

print("  Output written to:", ANN_OUT)


