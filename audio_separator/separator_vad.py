import torch
import numpy as np


class SeparatorVAD:

    def __init__(self,
                 vad_iterator,
                 model,
                 sample_rate: int = 16000,
                 window_size_samples: int = 1024,
                 max_duration_s: float = 0.4,
                 min_duration_s: float = 0.3,
                 ):

        self.sample_rate = sample_rate
        self.window_size_samples = window_size_samples
        self.vad_iterator = vad_iterator
        self.result_container = []
        self.max_duration_s = max_duration_s
        self.min_duration_s = min_duration_s
        self.model = model

    def separate_function(self,
                          input_audio: np.array,
                          audio_duration: float) -> list:

        # получаем вероятности для каждого фрейма
        audio_duration = int(audio_duration * self.sample_rate)
        speech_probs = []
        input_audio = np.float32(input_audio)
        speech_tensor = torch.from_numpy(input_audio)
        for i in range(0, len(speech_tensor), self.window_size_samples):
            chunk = speech_tensor[i: i + self.window_size_samples]
            if len(chunk) < self.window_size_samples:
                break
            speech_prob = self.model(chunk, self.sample_rate).item()
            speech_probs.append(speech_prob)
        self.vad_iterator.reset_states()

        # вычисляем локальные минимумы вероятностей
        probs_minimums = []
        for i in range(len(speech_probs) - 1):
            if (speech_probs[i] < speech_probs[i - 1]) and \
                    (speech_probs[i] < speech_probs[i + 1]):
                probs_minimums.append(i)
        if len(probs_minimums) == 0:  # при отсутствии лок. минимумов вероятностей
            # в контейнер добавляется весь файл целиком
            self.result_container.append(input_audio)
        else:
            boundaries = [0]
            probs_minimums = [i * self.window_size_samples for i in probs_minimums]
            current_part = self.max_duration_s  # временная точка конца текущего фрагмента сигнала, в котором
            # проверяется наличие minimums[0]
            while current_part <= audio_duration:
                if len(probs_minimums) != 0:
                    if probs_minimums[0] <= current_part:  # если minimums[0] лежит
                        # в данном отрезке
                        min_time_check = probs_minimums[0] - boundaries[-1]
                        if min_time_check < self.min_duration_s:
                            # и если minimums[0] лежит ближе к точке начала фрагмента
                            # чем минимально допустимое значение
                            boundaries.append(current_part + self.min_duration_s)  # то мы считаем
                            # след. точку прибавлением мин. длительности к предыдущей
                        else:
                            boundaries.append(probs_minimums[0])  # в противном случае просто доабвляем ее в boundaries

                        if len(probs_minimums) > 1:
                            probs_minimums = probs_minimums[1::]
                        else:
                            probs_minimums = []
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
