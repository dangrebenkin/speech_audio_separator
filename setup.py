from setuptools import setup, find_packages

setup(
    name='audio_separator',
    version='0.2',
    description='a Python library for wav-files separation',
    url='https://github.com/dangrebenkin/audio_separator',
    author='Daniel Grebenkin',
    author_email='d.grebenkin@g.nsu.ru',
    license='Apache License Version 2.0',
    keywords=['wav', 'separator', 'audio', 'energy', 'local minimums', 'vad'],
    packages=find_packages(),
    python_requires=r'>=3.8.0',
)
