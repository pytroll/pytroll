#!/usr/bin/env python


from setuptools import setup

long_description = """
Small package with scripts to process Direct Readout MODIS from PDS level 0 to
level 1. Uses the NASA DRL Science Processing Algorithm (SPA) and expects
messages in pytroll format from the reception station telling when a file is
being dispatched to the server.
""" 

setup(name='modis_lvl1_proc',
      description="Run scripts for MODIS level 0 to level 1 processing",
      author="Adam Dybbroe",
      author_email="adam.dybbroe@smhi.se",
      url='',
      long_description=long_description,
      license='GPLv3',
      version='0.1',
      scripts = ['modis_dr_runner.sh', 
                 'modis_lvl1_check_runner_lib.sh',
                 'modis_lvl1_runner_status.sh',
                 'modis_lvl1_runner_start.sh',
                 'modis_lvl1_runner_stop.sh',
                 'modis_runner/modis_dr_runner.py'],
      packages=['modis_runner'],
      data_files = [('/etc/init.d', ['etc/init.d/SMHI-modis-lvl1-preproc'])],
      
      # Project should use reStructuredText, so ensure that the docutils get
      # installed or upgraded on the target machine
      install_requires = ['docutils>=0.3', 
                          'posttroll',
                          'numpy'
                         ],

      data_files=[('etc', ['etc/modis_dr_config.cfg'])],
      test_suite="nose.collector",
      tests_require=[],
      zip_safe=False
      )
