
import os

import io

from collections import defaultdict



from decord import VideoReader

from mmengine.fileio import FileClient



ANN_IN = "epic_rgb_train_segments_train.txt"   # original segments file

ANN_OUT = "epic_rgb_train_segments_train_bytesio_clean.txt"



file_client = FileClient("disk")



# Cache results so each video is tested only once

video_ok = {}

video_bad = {}



def check_video(video_path):

    """Return True if Decord can open this video via BytesIO, False otherwise."""

    if video_path in video_ok:

        return True

    if video_path in video_bad:

        return False



    if not os.path.exists(video_path):

        print(f"[MISS] File not found: {video_path}")

        video_bad[video_path] = True

        return False



    try:

        data = file_client.get(video_path)  # read bytes like MMAction does

        bio = io.BytesIO(data)

        vr = VideoReader(bio, num_threads=1)

        _ = len(vr)  # force metadata read

    except Exception as e:

        print(f"[BAD]  {video_path}  |  {repr(e)}")

        video_bad[video_path] = True

        return False



    video_ok[video_path] = True

    return True





def main():

    total_lines = 0

    kept = 0

    skipped = 0



    print(f"Input ann file: {ANN_IN}")

    print(f"Output ann file: {ANN_OUT}")



    with open(ANN_IN, "r") as fin, open(ANN_OUT, "w") as fout:

        for line in fin:

            line = line.strip()

            if not line:

                continue



            total_lines += 1

            parts = line.split()

            if len(parts) < 5:

                print(f"[SKIP] malformed line #{total_lines}: {line}")

                skipped += 1

                continue



            video_path = parts[0]



            # Full path should already be in the line (as we wrote it before),

            # e.g. /data/leuven/.../videos_640x360/P01/P01_01.MP4

            if not check_video(video_path):

                skipped += 1

                continue



            fout.write(line + "\n")

            kept += 1



    print("Done strict cleaning.")

    print(f"  Total lines seen: {total_lines}")

    print(f"  Kept segments:    {kept}")

    print(f"  Skipped segments: {skipped}")

    print(f"  Unique good videos: {len(video_ok)}")

    print(f"  Unique bad videos:  {len(video_bad)}")



    if video_bad:

        print("\nList of bad videos (BytesIO+Decord):")

        for vp in sorted(video_bad.keys()):

            print("  ", vp)





if __name__ == "__main__":

    main()


