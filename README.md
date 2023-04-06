# audio separator

#### Description

A useful tool to split WAV PCM files to fragments.
For example, if you need audiofiles with duration less then 2 minutes and more then 70 seconds but there is only 
one 2-minutes WAV-file, you can use this tool with max and min time parameters and there will be the intended result.

#### Installation

```
git clone https://github.com/dangrebenkin/audio_separator.git
cd audio_separator
pip install -r requirements.txt
python setup.py install
```

#### Two ways of ~~life~~ separation

1) Local minimums of signal energy function [1];
2) Voice active detection by Silero [2].

#### Usage

Create *Separator* object with your settings:
```
from audio_separator.separator import Separator 

separator_object = Separator()
```

#### Links

1. Рабинер Л.Р., Шафер Р.В. Цифровая обработка речевых сигналов — М.: Радио и связь, 1981. — 593 c., c. 114.
2. Silero VAD: pre-trained enterprise-grade Voice Activity Detector (VAD), Number Detector and Language Classifier.
URL: https://github.com/snakers4/silero-vad.