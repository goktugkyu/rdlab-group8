
import random



IN_FILE = "epic_rgb_train_segments_full.txt"

TRAIN_OUT = "epic_rgb_train_segments_train.txt"

VAL_OUT = "epic_rgb_train_segments_val.txt"



VAL_RATIO = 0.1   # 10% for validation, change if you want



def main():

    with open(IN_FILE, "r") as f:

        lines = [ln for ln in f.readlines() if ln.strip()]



    print(f"Total segments in {IN_FILE}: {len(lines)}")



    # Shuffle with fixed seed for reproducibility

    random.seed(42)

    random.shuffle(lines)



    n_total = len(lines)

    n_val = int(n_total * VAL_RATIO)

    n_train = n_total - n_val



    val_lines = lines[:n_val]

    train_lines = lines[n_val:]



    with open(TRAIN_OUT, "w") as f:

        f.writelines(train_lines)

    with open(VAL_OUT, "w") as f:

        f.writelines(val_lines)



    print(f"Train segments: {n_train}  -> {TRAIN_OUT}")

    print(f"Val segments:   {n_val}    -> {VAL_OUT}")



if __name__ == "__main__":

    main()


