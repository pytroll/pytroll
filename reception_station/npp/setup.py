#!/usr/bin/env python


from setuptools import setup, find_packages

long_description = """
Small package with scripts to process Direct Readout Suomi NPP/VIIRS data from
RDR (level-0) to SDR (level-1). Uses the CSPP package from SSEC, Wisconsin, and
expects messages in pytroll format from the reception station telling when a
file is being dispatched to the server.
""" 

setup(name='npp_sdr_proc',
      description="Run scripts for Suomi NPP RDR to SDR processing",
      author="Adam Dybbroe",
      author_email="adam.dybbroe@smhi.se",
      url='',
      long_description=long_description,
      license='GPLv3',
      version='0.11',
      #packages = find_packages(),
      scripts = ['npp_sdr_runner.sh', 
                 'sdr_runner/npp_sdr_runner.py'],
      packages=['sdr_runner'],
      
      # Project should use reStructuredText, so ensure that the docutils get
      # installed or upgraded on the target machine
      install_requires = ['docutils>=0.3', 
                          'posttroll',
                          'numpy',
                          'pyorbital'
                          ],

      data_files=[('etc', ['etc/npp_sdr_config.cfg'])],
      test_suite="nose.collector",
      tests_require=[],
      zip_safe=False
      )
