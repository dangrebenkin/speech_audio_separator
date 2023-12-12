# Speech audio separator

A useful tool to split speech WAV PCM files to fragments, **splitting bounds are located in speech pauses**.
For example, if you need audiofiles with duration less than 2 minutes and more than 70 seconds but there is only 
one 2-minutes WAV-file, you can use this tool with max and min time parameters and there will be the intended result.

#### Installation:

```
git clone https://github.com/dangrebenkin/audio_separator.git
cd audio_separator
pip install -r requirements.txt
python setup.py install
```

#### Two ways of ~~life~~ audiofile separation:

1) Local minimums of signal energy function [1] ("energy_minimums" or "em");
2) Local minimums of Voice active detection (VAD) speech probabilities values sequence by Silero [2] ("vad"). More
preferred to use with **_speech audiofiles_**.

#### Common algorithm steps:

1. computing signal energy values sequence / calculating speech probabilities sequence for each frame;
2. finding local minimums of values in sequence from step 1;
3. searching for the temporal distance between the values from step 2 which are more (or is equal) 
than user's min time parameter and less (or is equal) than user's max time parameter, saving good 
boundaries to the list;
4. audiofile splitting into several fragments with the boundaries from step 3.

#### Usage:

1. Create *Separator* object with your settings:

    ```
    from audio_separator.separator import Separator 
    
    separator_object = Separator()
    ```

    **_Separator()_** parameters list (all optional):
    
   - `separator_type`: ways to find local minimums ('energy_minimums' or 'em'; 'vad'), default = 'energy_minimums';
   - `sample_rate`: sampling rate (Hz) of audio signal, default = 16000;
   - `max_duration_s`: max duration (seconds) of possible separated audio fragment, default = 0.4;
   - `min_duration_s`: min duration (seconds) of possible separated audio fragment, default = 0.3;
   - `frame_duration`: a frame duration (seconds) parameter for 'energy_minimums' audio processing, default = 0.001;
   - `stream_enabled`: if True you can use a `separate_stream()` function (see **_Stream mode_**), default = False;
   - `max_container_duration_s`: a time bound (seconds) of audio container (stream mode), default = 1.0.
   
2. Separate audiofiles with `separate()` function:
    
    ```
   separated_files_dict = separator_object.separate()
    ```
   **_separate()_** function arguments (all optional) :
   
    - `input_audio_csv`: you can give a csv-file (path) with several audiofiles paths in the first column (with no headers) 
   as an input, for example:
   
   |                          |
   |------------------------------------|
   | /home/user/Documents/example_1.wav |
   | /home/user/Documents/example_2.wav |
   | /home/user/Documents/example_3.wav |

   default = None;
    - `single_audiofile`: audiofile to separate path, default = None.

   The output of **_separate()_** function is a dict:

   ```
   {'<original wav-file name>':[<fragment 1 np.array>, <fragment 2 np.array>, ... , <fragment n np.array>]}
   ```

3. Stream mode (`Separator(stream_mode=True)`)

   Stream mode can be used to separate the fragments of audiodata: container of a stream mode accumulates the 
   results of separator until the total duration of processed audiofiles goes beyond `max_container_duration_s`
   value. For example:
   
   ```
   separator_object = Separator(stream_mode=True, max_container_duration_s=20)
   results = separator_object.separate_stream('10_sec_wav_file_name.wav')
   results  # None, because total duration of processed audiofiles is 10 seconds now
   results = separator_object.separate_stream('40_sec_wav_file_name.wav')
   results  # [list of np.arrays], because total duration of processed audiofiles is 50 seconds now
   ```
   
#### Links

1. Рабинер Л.Р., Шафер Р.В. Цифровая обработка речевых сигналов — М.: Радио и связь, 1981. — 593 c., c. 114.
2. Silero VAD: pre-trained enterprise-grade Voice Activity Detector (VAD), Number Detector and Language Classifier.
URL: https://github.com/snakers4/silero-vad.
