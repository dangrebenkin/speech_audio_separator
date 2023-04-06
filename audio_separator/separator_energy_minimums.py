import struct
import numpy as np
from scipy import signal


class SeparatorSignalEnergy:

    def __init__(self,
                 sample_rate: int = 16000,
                 max_duration_s: float = 0.4,
                 min_duration_s: float = 0.3,
                 frame_duration: float = 0.001):

        self.frame_duration = frame_duration
        self.sample_rate = sample_rate
        self.max_duration_s = int(max_duration_s * self.sample_rate)
        self.min_duration_s = int(min_duration_s * self.sample_rate)
        self.result_container = []
        self.nperseg = int(self.sample_rate / 100)

    def separate_function(self,
                          input_audio: np.array,
                          audio_duration: float) -> list:

        # обработка сигнала
        audio_duration = int(audio_duration * self.sample_rate)
        input_audio_bytes = np.asarray(input_audio * 32768.0, dtype=np.int16).tobytes()
        n_data = len(input_audio_bytes)
        sound_signal = np.empty((int(n_data / 2),))
        for ind in range(sound_signal.shape[0]):
            sound_signal[ind] = float(struct.unpack('<h', input_audio_bytes[(ind * 2):(ind * 2 + 2)])[0])
        frequencies_axis, time_axis, spectrogram = signal.spectrogram(
            sound_signal, fs=self.sample_rate, window='hamming', nperseg=self.nperseg, noverlap=0,
            scaling='spectrum', mode='psd'
        )
        frame_size = int(round(self.frame_duration * float(self.sample_rate)))
        spectrogram = spectrogram.transpose()
        sound_frames = np.reshape(sound_signal[0:(spectrogram.shape[0] * frame_size)],
                                  (spectrogram.shape[0], frame_size))
        # энергия для каждого окна
        energy_values = []
        for time_ind in range(spectrogram.shape[0]):
            energy = np.square(sound_frames[time_ind]).mean()
            energy_values.append(energy)
        # поиск локальных минимумов
        energy_minimums = []
        for i in range(len(energy_values) - 1):
            if (energy_values[i] < energy_values[i - 1]) and (energy_values[i] < energy_values[i + 1]):
                energy_minimums.append(i)

        if len(energy_minimums) == 0:  # при отсутствии лок. минимумов в контейнер добавляется весь файл целиком
            self.result_container.append(input_audio)
        else:
            minimums = [i * self.nperseg for i in energy_minimums]
            boundaries = [0]
            current_part = self.max_duration_s  # временная точка конца текущего фрагмента сигнала, в котором
            # проверяется наличие minimums[0]
            while current_part <= audio_duration:
                if len(minimums) != 0:
                    if minimums[0] <= current_part:  # если minimums[0] лежит
                        # в данном отрезке
                        min_time_check = minimums[0] - boundaries[-1]
                        if min_time_check < self.min_duration_s:  # и если minimums[0] лежит ближе к точке начала фрагмента
                            # чем минимально допустимое значение
                            boundaries.append(current_part + self.min_duration_s)  # то мы считаем
                            # след. точку прибавлением мин. длительности к предыдущей
                        else:
                            boundaries.append(minimums[0])  # в противном случае просто доабвляем ее в boundaries

                        if len(minimums) > 1:
                            minimums = minimums[1::]
                        else:
                            minimums = []
                    else:  # если minimums[0] не лежит в данном отрезке,
                        boundaries.append(current_part)  # то в boundaries добавляется точка сигнала, таким образом
                        # фрагмент будет иметь макс. допустимую длительность
                else:
                    boundaries.append(current_part)
                current_part = boundaries[-1] + self.max_duration_s  # вычисляем макс. допустимое значение конца
                # след. фрагмента сигнала

            # добавление последней точки (конца сигнала)
            rest_time = audio_duration - boundaries[-1]
            if rest_time > self.min_duration_s:
                boundaries.append(audio_duration)
            else:
                boundaries[-1] = boundaries[-1] + rest_time

            for startpoint, finishpoint in zip(boundaries, boundaries[1:]):
                self.result_container.append(input_audio[startpoint:finishpoint])

        return self.result_container
