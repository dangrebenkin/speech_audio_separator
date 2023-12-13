import numpy as np
import torch
import torchaudio

from speech_audio_separator import Separator

file_name = 'test.wav'
separator_tool = Separator(separator_type='vad',
                           max_duration_s=10.0,
                           min_duration_s=2.0)
separation_parts = separator_tool.separate(single_audiofile=file_name)[file_name]
audio_tensors = [torch.from_numpy(np.float32(i)) for i in separation_parts]
audio_tensors = [torch.unsqueeze(i, 0) for i in audio_tensors]
counter = 1
for i in audio_tensors:
    torchaudio.save(f'{counter}_{file_name}',
                    i,
                    sample_rate=16000)
    counter += 1
