import os

in_file = "/data/leuven/380/vsc38053/RD_Project/epic-kitchens-data/epic100_train_action_list.txt"
out_file = "/data/leuven/380/vsc38053/RD_Project/epic-kitchens-data/epic100_train_action_list_clean.txt"
video_root = "/data/leuven/380/vsc38053/RD_Project/epic-kitchens-data/videos_640x360"

kept = 0
skipped = 0

with open(in_file, "r") as f, open(out_file, "w") as out:
    for line in f:
        parts = line.strip().split()
        vid_path = parts[0]  # first column is path like P25/P25_09_a0075.mp4
        full_path = os.path.join(video_root, vid_path)

        if os.path.exists(full_path):
            out.write(line)
            kept += 1
        else:
            skipped += 1

print(f"Kept {kept} entries, skipped {skipped} missing videos.")
print(f"Clean list saved to {out_file}")
