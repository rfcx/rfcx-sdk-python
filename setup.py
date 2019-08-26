from setuptools import setup, find_packages

REQUIRED_PACKAGES = ['pydub', 'librosa']

setup(name='rfcx',
      version='0.0.3',
      url='https://github.com/rfcx/rfcx-sdk-python',
      license='None',
      author='Antony Harfield',
      author_email='antony@rfcx.org',
      install_requires=REQUIRED_PACKAGES,
      description='Python client SDK for connecting to the Rainforest Connection platform',
      long_description=open('README.md').read(),
      long_description_content_type="text/markdown",
      packages=find_packages(exclude=['tests']),
      classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
      ],
      test_suite='nose.collector',
      tests_require=['nose'])