import random

in_file = "epic_rgb_train_segments_train_bytesio_clean.txt"
out_file = "epic_rgb_train_segments_train_bytesio_clean_30p.txt"

keep_prob = 0.3  # keep 30% of lines
random.seed(0)

kept = 0
total = 0

with open(in_file, "r") as fin, open(out_file, "w") as fout:
    for line in fin:
        total += 1
        if random.random() < keep_prob:
            fout.write(line)
            kept += 1

print(f"Total lines: {total}")
print(f"Kept lines:  {kept}")
