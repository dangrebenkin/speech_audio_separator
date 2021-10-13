from setuptools import setup, find_packages, Extension
from os.path import join, dirname

setup(
    name='energy_separator',              
    version='0.1',                         
    description='command-line package for wav-files separation with using local energy minimums method',
    url='https://github.com/dangrebenkin/energy_separator',
    author='Daniel Grebenkin',
    author_email = 'd.grebenkin@g.nsu.ru',
    license='Apache License Version 2.0',
    keywords=['wav','separator','audio','energy','local minimums'],     
    packages = find_packages(), 
    platforms = 'Linux',
    entry_points ={ 
        'console_scripts': [ 
            'egsr = energy_separator.core:main'
        ]
    },
    install_requires=[
		'argparse >= 1.4.0',
        'wave >= 0.0.2',
        'numpy >= 1.19.5',
        'temp >= 2020.7.2',
        'scipy >= 1.5.1',
        'pandas >= 1.1.1',
        'pydub >= 0.25.1'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',
        'Topic :: Software Development',
        'Topic :: Scientific/Engineering',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',  
        'Programming Language :: Python :: 3.8']            
) 

