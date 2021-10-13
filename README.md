# energy_separator

## What is it for?

This separator was created to split WAV PCM file(s) into several parts with less duration. It can be useful if you have some time or memory constraints: for example, if you need audiofiles with duration less then 2 minutes and more then 70 seconds but there is only one 2-minutes WAV-file, you can use this tool with max and min time parameters and there will be the intended result.

## How does a separation works?

This method is based on the definition of signal energy from work[1] and it contains three steps:
1. computing signal energy;
2. finding some signal energy local minimums, which have a minimal sum but the temporal distance between these points is more (or is equal) than user's min time parameter and less (or is equal) than user's max time parameter;
3. audiofile splitting into several new ones by the boundaries from step 2.

## Requirements & installation

### Requirements

Python 3.6+

### Installation

You can install it with pip:
```
pip install energy_separator
```

## Input/output data & example

### Input data

This command-line program has two modes: one-file splitting and several files splitting. 

1. In the first case you can split just one audiofile with using -f flag, for example:
```
egsr -f /home/user/Documents/example.wav -s 16000 -max 120 -min 70
```
2. Several files splitting means that you can give a csv-file with several audiofiles' paths in the first column (with no headers) as an input, like this one:

| | |
| ------------- | ------------- |
| /home/user/Documents/example_1.wav | |
| /home/user/Documents/example_2.wav | |
| /home/user/Documents/example_2.wav | |

And in this case you should use -fs flag, for example:
```
egsr -fs example.csv -s 16000 -max 120 -min 70
```
In both cases you also have to specify your file(s) sample rate (-s flag) in Hz, min (-min flag) and max (-max flag) time boundaries in seconds. In several files mode all of the files have to have a similar sample rate. All traceback and exceptions you can find in 'energy_separator.log'.

### Output data

The program output is several files with random names. These files path you can find in:

1. if you use the first mode, the path of new files will be in 'energy_separator.log', for example:
```
INFO:root:Checking your input wav file(s) info...
INFO:root:Your file was seprated to these ones:['/home/user/Documents/tmp9zf04xbb.wav', '/home/user/Documents/tmphdcpa_bt.wav']
```
2. if you use several files mode, the paths of new files will be in the second column of your csv-file, for example:

| path | new files |
| ------------- | ------------- |
| /home/user/Documents/example_1.wav | '/home/user/Documents/tmp9zf04xbb.wav', '/home/user/Documents/tmphdcpa_bt.wav' |
| /home/user/Documents/example_2.wav | '/home/user/Documents/tmp9zf04xbj.wav', '/home/user/Documents/tmpfdcpa_bt.wav'|
| /home/user/Documents/example_2.wav | '/home/user/Documents/tmp9zf04dbb.wav', '/home/user/Documents/tmpqdcpa_bt.wav'|

## Options
```
egsr [-h] [-f INPUT_AUDIO] [-fs INPUT_AUDIO_CSV] -s SAMPLE_RATE -max MAX_TIME -min MIN_TIME [-o OUTPUT_PATH]
```
1. -f INPUT_AUDIO, --input_wav_file INPUT_AUDIO (input wav file path, optional);
2. -fs INPUT_AUDIO_CSV, --list_of_input_wavs INPUT_AUDIO_CSV (input wavs csv-file, optional);
3. -s SAMPLE_RATE, --sample_rate SAMPLE_RATE (wav sample_rate in Hz, always required);
4. -max MAX_TIME, --max_duration MAX_TIME (max duration for each of output audiofiles in seconds, always required);
5. -min MIN_TIME, --min_duration MIN_TIME (min duration for each of output audiofiles in seconds, always required);
6. -o OUTPUT_PATH, --output_path OUTPUT_PATH (path for output files, optional), for example:
```
egsr -fs example.csv -s 16000 -max 120 -min 70 -o results
```

## Links
1. Рабинер Л.Р., Шафер Р.В. Цифровая обработка речевых сигналов — М.: Радио и связь, 1981. — 593 c., c. 114.
