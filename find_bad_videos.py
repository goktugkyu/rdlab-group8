
from decord import VideoReader

import sys



ANN_FILE = "epic_rgb_train_segments_train.txt"



bad = []

total = 0



with open(ANN_FILE, "r") as f:

    for i, line in enumerate(f):

        line = line.strip()

        if not line:

            continue

        parts = line.split()

        path = parts[0]  # absolute video path

        total += 1

        try:

            vr = VideoReader(path)

            _ = len(vr)  # force reading header

        except Exception as e:

            msg = f"BAD #{len(bad)} @ line {i}: {path}  |  {repr(e)}"

            print(msg)

            bad.append((i, path, repr(e)))



print(f"\nChecked {total} samples.")

print(f"Total bad videos: {len(bad)}")

if bad:

    print("List of bad videos:")

    for i, path, err in bad:

        print(f"- line {i}: {path}")


