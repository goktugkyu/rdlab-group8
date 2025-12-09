EPIC-KITCHENS-100 Action Recognition (RD Lab Project)

This repository contains our full pipeline for training an EPIC-KITCHENS-100 action recognition model using MMAction2, based on an X3D-S backbone, trained on time-bounded segments extracted from the original full videos (not sliced video files).

The project includes:

dataset reconstruction from full-frame EPIC videos

corrupted-video detection & cleaning

custom dataloader for segment-based video sampling

training configuration (X3D-S, segment sampling, verb–noun pair model)

slurm job scripts for VSC Tier-2 HPC

notes on producing Codabench submissions (for EPIC validation leaderboard)

This README explains how everything fits together and which files newcomers should study first.

🚀 Project Overview

EPIC-KITCHENS-100 provides:

full videos per participant (P01/P01_01.MP4, etc.)

annotations containing start_frame, stop_frame, verb_class, noun_class

MMAction2 normally requires pre-sliced videos (per segment), but we implemented a custom approach:

✔ We train directly from full videos

Instead of slicing tens of thousands of videos:

we load the original full videos

we use frame-level start and stop indices

our custom dataset (EpicSegmentVideoDataset) ensures MMAction2 decodes only frames inside the annotation segment.

This avoids:

errors from corrupted sliced videos

massive storage usage

redundant preprocessing

📂 Repository Structure (Important Files)

Here are the key files your collaborators must read:

1. epic_segment_dataset.py

➡️ This is the custom MMAction2 dataset class we built.

It:

reads annotation lines like:

epic-kitchens-data/videos_640x360/P01/P01_01.MP4 12345 12495 12 87


loads only the [start_frame : stop_frame] frames

provides filename, start_index, end_index, label, etc., to the pipeline

supports our “segment-based” training strategy

This file is the heart of the project.

2. make_epic_segment_ann.py

➡️ Script that reconstructs EPIC annotation text files from the raw CSV:

reads the full EPIC_100_train.csv

builds one line per segment

outputs:

epic_rgb_train_segments_train.txt

epic_rgb_train_segments_val.txt

each line includes video path + frame boundaries

3. clean_segments_bytesio.py (or similar)

➡️ Removes all segments referencing corrupted videos via Decord and BytesIO.

This was necessary because ~20 videos in the VSC archive were corrupted.

Outputs:

epic_rgb_train_segments_train_bytesio_clean.txt (used for training)

4. Config file

mmaction2/configs/recognition/x3d/x3d_s_epic_rgb_segments.py

➡️ This is the training configuration you run via Slurm.

It contains:

custom dataset import

data_root settings

cleaned annotation file

training pipeline

X3D-S model definition

optimizer / LR schedule

work_dir

disabled validation/test (for now)

Your teammates must inspect this file because it defines the full model.

5. train_x3d_wice.job / train_x3d_genius.job

➡️ Slurm scripts for launching training on VSC HPC.

They include:

module load

conda environment

PYTHONPATH fix

GPU/partition configs

training command

6. Output and Logs

Inside:

work_dirs/x3d_s_epic100_13x6x1_rgb_pairs/


Includes:

training logs

checkpoints

model metadata

🧠 How the Model Works
Model: X3D-S

lightweight 3D ConvNet

efficient for long activity videos

trained on RGB frames

uses 13 frames × 6-frame interval (≈78 input frames per clip)

Task: Verb–Noun Pair Classification

We combine:

97 verbs

300 nouns
→ 3477 unique pairs

Model predicts pair logits (not separate heads).

🎬 Data Loading & Training Strategy
Segment-based training

Our dataloader samples clips by:

Reading 'start_frame' and 'stop_frame'

Selecting frames only inside that interval

Applying MMAction2 augmentations

Feeding them to X3D

This avoids pre-slicing but does slow down I/O.
(We later optimized by reducing num_workers and memory load on HPC.)

🧪 Validation (Codabench Pipeline — Future Step)

Codabench expects a file:

submission.pt


containing:

[
   {
      'narration_id': 'P01_101_0',
      'verb_output': <tensor shape [97]>,
      'noun_output': <tensor shape [300]>,
   },
   ...
]


To achieve this later, we'll:

Load model checkpoint

Run inference on EPIC_100_validation.csv segments

Gather logits per narration_id

Save using torch.save()

This is easy to add once the training stabilizes.

🛠 Setup Instructions (For New Collaborators)
1. Clone this repo on VSC:
git clone git@github.com:<your_repo>.git
cd epic-kitchens-rdlab

2. Activate environment:
conda activate mmaction_clean

3. Ensure EPIC dataset folders exist:
epic-kitchens-data/annotations/
epic-kitchens-data/videos_640x360/

4. Ensure annotation files are present:
epic_rgb_train_segments_train_bytesio_clean.txt

5. Run training:
sbatch train_x3d_wice.job

🧹 Notes on Known Issues
⚠ Slow data loading (Decord)

Full-video loading is expensive → CPU/GPU idle time increases.

Possible improvements:

reduce clip_len

reduce frame_interval

convert videos to a faster codec

pre-slice segments into short clips (if storage permits)

⚠ Corrupted videos

Detected via Decord:

mostly in P22, P25, P28

removed automatically via cleaning script

🤝 Contributors

Göktuğ Kuyumcuoğlu
(and friends in the RD Lab group)

Project supervised under KU Leuven Research & Development Lab.

📌 Summary

This repository contains the full working pipeline for training segment-based action recognition on EPIC-KITCHENS-100 using MMAction2, including:

downloading & organizing raw data

generating annotations

cleaning corrupted entries

building a custom dataset class

configuring X3D-S

launching jobs on VSC HPC

preparing for Codabench submissions

Everything necessary to reproduce or extend the work is documented here.