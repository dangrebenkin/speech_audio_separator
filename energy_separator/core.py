import wave, numpy, struct, temp, os, sys, logging, pandas, re, argparse, traceback
from scipy import signal
from pydub import AudioSegment

def separate(input_audio, sample_rate, max_time, min_time, output_path):
	nperseg=int(sample_rate/100)
	frame_duration = 0.01
	with wave.open(input_audio, 'r') as data:
		audiodata = data.readframes(data.getnframes())
	len_data = len(audiodata)
	sound_signal = numpy.empty((int(len_data / 2),))
	for position_index in range(sound_signal.shape[0]):
		sound_signal[position_index] = float(struct.unpack('<h', audiodata[(position_index * 2):(position_index * 2 + 2)])[0])
	frequencies_axis, time_axis, spectrogram = signal.spectrogram(
		sound_signal, fs=sample_rate, window='hamming', nperseg=nperseg, noverlap=0,
		scaling='spectrum', mode='psd'
		)
	frame_size = int(round(frame_duration * float(sample_rate)))
	spectrogram = spectrogram.transpose()
	sound_frames = numpy.reshape(sound_signal[0:(spectrogram.shape[0] * frame_size)], (spectrogram.shape[0], frame_size))
	energy_values = []
	for time_index in range(spectrogram.shape[0]):
		energy = numpy.square(sound_frames[time_index]).mean()
		energy_values.append(energy)
	minimums = []
	for i in range(len(energy_values)-1):
		if (energy_values[i] < energy_values[i-1]) and (energy_values[i] < energy_values[i+1]):
			minimums.append(i)
	sorted_minimums = sorted(set(minimums))
	boundaries = [0]
	for i in sorted_minimums:
		duration = i - boundaries[-1]
		if duration >= (min_time*100) and duration <= (max_time*100): 
			boundaries.append(i)
			sorted_minimums = sorted_minimums[sorted_minimums.index(i)::]
	boundaries.append(sorted_minimums[-1])
	timepoints=[0]
	for boundary in boundaries[1::]:
		timepoint = boundary*10 
		timepoints.append(timepoint)
	audio = AudioSegment.from_file(input_audio, format="wav", frame_rate=sample_rate) 
	result_paths = []
	for startpoint, finishpoint in zip(timepoints, timepoints[1:]):
		input_file_part = audio[startpoint : finishpoint]
		name = output_path+temp.tempfile()+'.wav' 
		final_name = re.sub('tmp/','',name)
		input_file_part.export(final_name,format='wav')
		result_paths.append(final_name)
	return result_paths

def main():
	
	logging.basicConfig(filename='energy_separator.log', level=logging.DEBUG)
	current_path = os.path.abspath(os.getcwd())
	
	parser = argparse.ArgumentParser()
	parser.add_argument('-f', '--input_wav_file', dest='input_audio', type=str,
						help='input wav file path', required=False)
	parser.add_argument('-fs', '--list_of_input_wavs', dest='input_audio_csv', type=str,
						help='input wavs csv-file', required=False)
	parser.add_argument('-s', '--sample_rate', dest='sample_rate', type=int,
						help='wav sample_rate in Hz', required=True)
	parser.add_argument('-max','--max_duration', dest='max_time', type=int,
						help='max duration for each of output audiofiles in seconds', required=True)
	parser.add_argument('-min','--min_duration', dest='min_time', type=int,
						help='min duration for each of output audiofiles in seconds', required=True)
	parser.add_argument('-o', '--output_path', dest='output_path', type=str, default=current_path, 
						help='path for output files', required=False)
	
	args = parser.parse_args()

	logging.info('Checking your output folder...')
	try:
		output_path = os.path.abspath(args.output_path)
	except Exception as e:
		logging.error(traceback.format_exc())
		logging.error("Check your output path, please, it seems like it does not exist.")
		sys.exit()  
	
	logging.info('Checking your input wav file(s) info...')
	
	if args.input_audio is not None:
		if args.input_audio.endswith('.wav'):
			try:
				audio = os.path.abspath(args.input_audio)
				result = separate(audio, args.sample_rate, args.max_time, args.min_time, output_path)
				logging.info('Your file was seprated to these ones:'+str(result))
				logging.info('End.')
			except Exception as e:
				logging.error(traceback.format_exc())
				sys.exit()
		else:
			logging.error("Check your audiofile format, it must be WAV PCM.")
			sys.exit()
			
	elif args.input_audio_csv is not None:
		try:
			audio_csv = os.path.abspath(args.input_audio_csv)
			csv_file = pandas.read_csv(audio_csv,header=None)
			csv_file.rename(columns={0:'path'}, inplace=True)
			df = pandas.DataFrame(csv_file)
			counter = 0
			for path in df['path']:
				path = str(path)
				if path.endswith('.wav'):
					try:
						audio = os.path.abspath(path)
						result = separate(audio, args.sample_rate, args.max_time, args.min_time, output_path)
						if len(result) >= 2:
							df.loc[counter, 'new files'] = str(', '.join(result))
							counter += 1
						else:
							df.loc[counter, 'new files'] = 'incorrect result'
							counter += 1
					except Exception as e:
						logging.error(traceback.format_exc())
						counter += 1
						continue
				else:
					logging.error("Check your audiofile format, it must be WAV PCM, file: "+path)
					counter += 1
					continue
			df.to_csv(audio_csv, mode='w',index=False)
			logging.info('End.')
		except Exception as e:
			logging.error(traceback.format_exc())
			sys.exit()
			
	else:
		logging.error('There is no your input wav file(s) info.')
		sys.exit()
