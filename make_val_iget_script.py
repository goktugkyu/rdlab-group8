
import csv

import os



# Paths

csv_path = "/data/leuven/380/vsc38053/RD_Project/epic-kitchens-data/annotations/EPIC_100_validation.csv"

remote_base = "/set/home/ciis-lab/datasets/epic-kitchens/videos_640x360"

local_base = "/scratch/leuven/380/vsc38053/EPIC-val/videos_640x360"



out_script = "download_epic_val_with_iget.sh"



seen = set()

lines = ["#!/bin/bash\n\nset -e\n\n"]



with open(csv_path, newline="") as f:

    reader = csv.DictReader(f)

    for row in reader:

        pid = row["participant_id"]        # e.g. P01

        video_id = row["video_id"]         # e.g. P01_11, P01_101, ...



        base = video_id.split(".")[0]      # just in case there is an extension in CSV

        key = (pid, base)

        if key in seen:

            continue

        seen.add(key)



        remote = f'{remote_base}/{pid}/{base}.MP4'

        local_dir = f'{local_base}/{pid}'

        local_path = f'{local_dir}/{base}.MP4'



        lines.append(f'mkdir -p "{local_dir}"\n')

        lines.append(f'echo "Downloading {remote} -> {local_path}"\n')

        lines.append(f'iget "{remote}" "{local_path}" || echo "!! FAILED {remote}"\n')

        lines.append("\n")



with open(out_script, "w") as f:

    f.writelines(lines)



print(f"Wrote {out_script} with {len(seen)} unique videos.")


