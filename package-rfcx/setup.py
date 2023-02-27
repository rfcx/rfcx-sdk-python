from setuptools import setup, find_packages

REQUIRED_PACKAGES = ['httplib2', 'six', 'requests']

setup(name='rfcx',
      version='0.2.6',
      url='https://github.com/rfcx/rfcx-sdk-python',
      license='None',
      author='Rainforest Connection',
      author_email='antony@rfcx.org',
      install_requires=REQUIRED_PACKAGES,
      description='Python client SDK for connecting to the Rainforest Connection platform',
      long_description="[See the documentation](https://rfcx.github.io/rfcx-sdk-python/) or [try an example](https://gist.github.com/antonyharfield/93231b3df86cd58fecee4f4d1ec9cc5b)",
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
