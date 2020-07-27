import setuptools

setuptools.setup(
  name = 'experiment_tracker',
  version = '0.0.5',
  author = 'Markus Zopf',
  description = 'Simple tool to track experiments by writing parameters and corresponding results into an SQL database.',
  url = 'https://github.com/MarkusZopf/ExperimentTracker',
  packages = ['experiment_tracker'],
  install_requires=[
          'pymysql',
      ],
  classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
  ],
   python_requires='>=3.6.7',
)