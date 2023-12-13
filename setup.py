from setuptools import setup, find_packages
from setuptools.command.install import install
import subprocess


class PostInstallCommand(install):
    def run(self):
        subprocess.call(['pip', 'install', 'torch==2.0.1', 'torchaudio==2.0.2',
                         '--index-url', 'https://download.pytorch.org/whl/cpu'])
        subprocess.call(['pip', 'install', '-r', 'requirements.txt'])
        install.run(self)


setup(
    name='speech_audio_separator',
    version='0.3',
    description='a Python library for wav-files separation',
    url='https://github.com/dangrebenkin/speech_audio_separator',
    author='Daniel Grebenkin',
    author_email='d.grebenkin@g.nsu.ru',
    license='Apache License Version 2.0',
    keywords=['wav', 'separator', 'audio', 'energy', 'local minimums', 'vad'],
    packages=find_packages(),
    python_requires=r'>=3.8.0',
    cmdclass={
        'install': PostInstallCommand,
    },
)
