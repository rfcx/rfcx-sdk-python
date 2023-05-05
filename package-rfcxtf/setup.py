from setuptools import setup, find_packages

REQUIRED_PACKAGES = ['tensorflow', 'pysndfile', 'numpy']

setup(name='rfcxtf',
      version='0.0.2',
      url='https://github.com/rfcx/rfcx-sdk-python',
      license='None',
      author='Rainforest Connection',
      author_email='antony@rfcx.org',
      install_requires=REQUIRED_PACKAGES,
      description='Support for building TensorFlow classifiers on Arbimon and Guardian platforms',
      packages=find_packages(exclude=['tests']),
      classifiers=[
          'Development Status :: 1 - Planning',
          'Intended Audience :: Science/Research',
          'Programming Language :: Python :: 3',
          'Operating System :: OS Independent',
      ],
      test_suite='nose.collector',
      tests_require=['nose'])
