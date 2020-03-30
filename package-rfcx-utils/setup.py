from setuptools import setup, find_packages

REQUIRED_PACKAGES = ['httplib2', 'six', 'pydub', 'pandas']

setup(name='rfcx-utils',
      version='0.0.7',
      url='https://github.com/rfcx/rfcx-sdk-python',
      license='None',
      author='Rainforest Connection',
      author_email='antony@rfcx.org',
      install_requires=REQUIRED_PACKAGES,
      description='Collection of utils for use with Rainforest Connection platform',
      packages=find_packages(exclude=['tests']),
      classifiers=[
          'Development Status :: 1 - Planning',
          'Intended Audience :: Science/Research',
          'Programming Language :: Python :: 3',
          'Operating System :: OS Independent',
      ],
      test_suite='nose.collector',
      tests_require=['nose'])
