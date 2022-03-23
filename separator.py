import wave, numpy, struct, temp
from scipy import signal
from pydub import AudioSegment

def separate(input_audio):	
	FRAME_DURATION = 0.01
	# обработка сигнала
	with wave.open(input_audio, 'r') as fp:
		sound_data = fp.readframes(fp.getnframes())
	n_data = len(sound_data)
	sound_signal = numpy.empty((int(n_data / 2),))
	for ind in range(sound_signal.shape[0]):
		sound_signal[ind] = float(struct.unpack('<h', sound_data[(ind * 2):(ind * 2 + 2)])[0])
	frequencies_axis, time_axis, spectrogram = signal.spectrogram(
		sound_signal, fs=16000, window='hamming', nperseg=160, noverlap=0,
		scaling='spectrum', mode='psd'
		)
	frame_size = int(round(FRAME_DURATION * float(16000)))
	spectrogram = spectrogram.transpose()
	sound_frames = numpy.reshape(sound_signal[0:(spectrogram.shape[0] * frame_size)], (spectrogram.shape[0], frame_size))
	# энергия для каждого окна
	energy_values = []
	for time_ind in range(spectrogram.shape[0]):
		energy = numpy.square(sound_frames[time_ind]).mean()
		energy_values.append(energy)
	# локальные минимумы
	minimums2 = []
	for i in range(len(energy_values)-1):
		if (energy_values[i] < energy_values[i-1]) and (energy_values[i] < energy_values[i+1]):
			minimums2.append(i)
	minimums = sorted(set(minimums2))
	# расстояние между минимумами
	max_time = 12000 # 2 мин.
	min_time = 7000 # 70 сек.
	moments = [0]
	for i in minimums:
		duration = i - moments[-1]
		if duration >= min_time and duration <= max_time:
			moments.append(i)
			minimums = minimums[minimums.index(i)::]
	moments.append(minimums[-1])
	# создание кусочков исходного аудиофайла
	timepoints_milliseconds=[0]
	for moment in moments[1::]:
		timepoint = moment*10
		timepoints_milliseconds.append(timepoint)
	audio = AudioSegment.from_file(input_audio, format="wav", frame_rate=16000)	
	pieces_names = []
	for startpoint, finishpoint in zip(timepoints_milliseconds, timepoints_milliseconds[1:]):
		new_file = audio[startpoint : finishpoint]
		new_file_name = temp.tempfile()+'.wav'
		new_file.export(new_file_name,format='wav')
		pieces_names.append(new_file_name)
	return pieces_names
