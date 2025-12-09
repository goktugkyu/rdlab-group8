import os
from typing import List, Dict

import numpy as np

from mmaction.datasets.base import BaseActionDataset
from mmaction.registry import DATASETS, TRANSFORMS


@DATASETS.register_module()
class EpicSegmentVideoDataset(BaseActionDataset):
    """EPIC-KITCHENS segment dataset using full videos and frame ranges.

    Annotation line format (space-separated):

        video_path start_frame stop_frame verb_id noun_id

    Example:

        /data/.../videos_640x360/P01/P01_01.MP4 8 202 3 13
    """

    def __init__(self,
                 ann_file: str,
                 data_prefix: Dict = dict(video=''),
                 **kwargs) -> None:
        # data_prefix is a dict, typically {'video': data_root}
        self.data_prefix = data_prefix
        super().__init__(ann_file=ann_file, **kwargs)

    def load_data_list(self) -> List[Dict]:
        data_list: List[Dict] = []
        pair2id: Dict[tuple, int] = {}
        next_id = 0

        with open(self.ann_file, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                parts = line.split()
                if len(parts) != 5:
                    raise ValueError(
                        f'Expected 5 fields per line, got {len(parts)}: {line}'
                    )

                path, start_f, stop_f, verb, noun = parts
                start_f = int(start_f)
                stop_f = int(stop_f)
                verb = int(verb)
                noun = int(noun)

                # Map (verb, noun) pair to a single class index
                key = (verb, noun)
                if key not in pair2id:
                    pair2id[key] = next_id
                    next_id += 1
                label = pair2id[key]

                # Make path absolute if needed
                if not os.path.isabs(path):
                    full_path = os.path.join(self.data_prefix.get('video', ''), path)
                else:
                    full_path = path

                total_frames = max(stop_f - start_f + 1, 1)

                data_list.append(
                    dict(
                        filename=full_path,
                        label=label,
                        start_index=start_f,
                        total_frames=total_frames,
                    )
                )

        # Optional: keep mapping for analysis
        self.pair2id = pair2id
        print(
            f'[EpicSegmentVideoDataset] Loaded {len(data_list)} segments, '
            f'{len(pair2id)} unique (verb, noun) pairs.'
        )
        return data_list


@TRANSFORMS.register_module()
class SegmentSampleFrames:
    """Sample frames inside the segment [start_index, start_index + total_frames - 1].

    This is a segment-aware sampler that works with full videos and the
    `start_index` / `total_frames` fields provided by EpicSegmentVideoDataset.

    It fills:
        - results["frame_inds"]
        - results["clip_len"]
        - results["frame_interval"]
        - results["num_clips"]
    """

    def __init__(self,
                 clip_len: int,
                 frame_interval: int = 1,
                 num_clips: int = 1,
                 test_mode: bool = False) -> None:
        self.clip_len = clip_len
        self.frame_interval = frame_interval
        self.num_clips = num_clips
        self.test_mode = test_mode

    def __call__(self, results: Dict) -> Dict:
        start = int(results.get('start_index', 1))
        num_frames = int(results['total_frames'])

        clip_len = self.clip_len
        frame_interval = self.frame_interval
        ori_clip_len = clip_len * frame_interval

        if num_frames <= 0:
            # Fallback: degenerate segment
            frame_inds = np.zeros((clip_len,), dtype=np.int32)
        else:
            if not self.test_mode:
                # Random offset in the segment
                if num_frames > ori_clip_len:
                    offset = np.random.randint(0, num_frames - ori_clip_len + 1)
                else:
                    offset = 0
            else:
                # Centered clip for val/test
                if num_frames > ori_clip_len:
                    offset = (num_frames - ori_clip_len) // 2
                else:
                    offset = 0

            # indices are 0-based relative to the segment
            frame_inds = offset + np.arange(0, ori_clip_len, frame_interval)
            frame_inds = np.clip(frame_inds, 0, max(num_frames - 1, 0))

            # convert to *video* frame indices (EPIC frames are 1-based)
            frame_inds = frame_inds + (start - 1)

        results['frame_inds'] = frame_inds.astype(np.int32)
        results['clip_len'] = clip_len
        results['frame_interval'] = frame_interval
        results['num_clips'] = self.num_clips

        return results
