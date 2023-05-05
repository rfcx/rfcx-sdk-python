from setuptools import setup, find_packages

REQUIRED_PACKAGES = ['httplib2', 'six', 'requests', 'requests-toolbelt']

setup(name='rfcx',
      version='0.3.1',
      url='https://github.com/rfcx/rfcx-sdk-python',
      license='None',
      author='Rainforest Connection',
      author_email='antony@rfcx.org',
      install_requires=REQUIRED_PACKAGES,
      description='Client SDK for the Rainforest Connection and Arbimon platforms',
      long_description="[See the documentation](https://rfcx.github.io/rfcx-sdk-python/) and [try the examples](https://github.com/rfcx/rfcx-sdk-python/tree/master/package-rfcx)",
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
