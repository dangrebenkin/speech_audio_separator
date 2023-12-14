import logging
import os
import sys
import traceback
import wave
import numpy as np
import pandas
import torch
from .separator_vad import SeparatorVAD
from .separator_energy_minimums import SeparatorSignalEnergy

logging.basicConfig(filename='separator.log', level=logging.DEBUG)


class Separator:

    def __init__(self,
                 separator_type: str = 'energy_minimums',
                 sample_rate: int = 16000,
                 stream_enabled: bool = False,
                 max_container_duration_s: float = 1.0,
                 max_duration_s: float = 0.4,
                 min_duration_s: float = 0.3,
                 frame_duration: float = 0.001
                 ):

        self.sample_rate = sample_rate
        self.max_duration_s = int(max_duration_s * self.sample_rate)
        self.min_duration_s = int(min_duration_s * self.sample_rate)
        self.separator_type = separator_type
        if (separator_type == 'energy_minimums') or (separator_type == 'em'):
            self.separator_type = 'em'
            self.frame_duration = frame_duration
            self.separator_class = SeparatorSignalEnergy(sample_rate=self.sample_rate,
                                                         max_duration_s=self.max_duration_s,
                                                         min_duration_s=self.min_duration_s)
        elif separator_type == 'vad':
            model, utils = torch.hub.load(repo_or_dir='snakers4/silero-vad',
                                          model='silero_vad',
                                          force_reload=False,
                                          onnx=False)
            (get_speech_timestamps,
             save_audio,
             read_audio,
             VADIterator,
             collect_chunks) = utils
            self.separator_class = SeparatorVAD(sample_rate=self.sample_rate,
                                                window_size_samples=1024,
                                                vad_iterator=VADIterator(model,
                                                                         sampling_rate=self.sample_rate),
                                                model=model,
                                                max_duration_s=self.max_duration_s,
                                                min_duration_s=self.min_duration_s
                                                )
        else:
            logging.error('Wrong separator type was set, check "separator_type" parameter')
        if stream_enabled:
            self.max_container_duration_s = max_container_duration_s
            self.container = []
            self.duration = 0

    def audio_processing(self,
                         audio_path: str):
        audio = os.path.abspath(audio_path)
        with wave.open(audio, 'rb') as fp:
            sound_data = fp.readframes(fp.getnframes())
            n_channels = fp.getnchannels()
            if fp.getsampwidth() == 1:
                data = np.frombuffer(sound_data, dtype=np.uint8)
            else:
                data = np.frombuffer(sound_data, dtype=np.int16)
            if n_channels == 1:
                if fp.getsampwidth() == 1:
                    sound = (data.astype(np.float32) - 128.0) / 128.0
                else:
                    sound = data.astype(np.float32) / 32768.0
            else:
                sound = None
        if sound is not None:
            file_duration = len(sound) / float(self.sample_rate)
        return sound, file_duration

    def separate(self,
                 input_audio_csv: str = None,
                 single_audiofile: str = None) -> dict:
        result_dict = {}
        if input_audio_csv is not None:
            try:
                audio_csv = os.path.abspath(input_audio_csv)
                csv_file = pandas.read_csv(audio_csv, header=None)
                csv_file.rename(columns={0: 'path'}, inplace=True)
                df = pandas.DataFrame(csv_file)
                for path in df['path']:
                    path = str(path)
                    if path.endswith('.wav'):
                        audio_array, audio_duration = self.audio_processing(path)
                        result = self.separator_class.separate_function(input_audio=audio_array,
                                                                        audio_duration=audio_duration)
                        result_dict[path] = result
                        self.separator_class.result_container = []
                    else:
                        logging.error("Check your audiofile format, it must be WAV PCM, file: " + path)
                        continue
                logging.info('End.')
            except Exception as e:
                logging.error(traceback.format_exc())
                sys.exit()

        if single_audiofile is not None:
            try:
                if single_audiofile.endswith('.wav'):
                    audio_array, audio_duration = self.audio_processing(single_audiofile)
                    result = self.separator_class.separate_function(input_audio=audio_array,
                                                                    audio_duration=audio_duration)
                    result_dict[single_audiofile] = result
                    self.separator_class.result_container = []
                else:
                    logging.error("Check your audiofile format, it must be WAV PCM, file: " + single_audiofile)
            except Exception as e:
                logging.error(traceback.format_exc())
                sys.exit()

        return result_dict

    def separate_stream(self,
                        single_audiofile: str = None) -> list:
        if single_audiofile.endswith('.wav'):
            audio_array, audio_duration = self.audio_processing(single_audiofile)
        else:
            logging.error("Check your audiofile format, it must be WAV PCM, file: " + single_audiofile)
        output = None
        if audio_array is not None:
            new_file_duration = len(audio_array) / float(self.sample_rate)
            self.duration += new_file_duration
            piece_result = self.separator_class.separate_function(input_audio=audio_array,
                                                                  audio_duration=audio_duration)
            self.separator_class.result_container = []
            self.container.extend(piece_result)
            if self.duration >= self.max_container_duration_s:
                output = self.container
                self.container = []
                self.duration = 0
        return output
