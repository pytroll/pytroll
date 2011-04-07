================================
 Installation and configuration
================================

Installing the different packages
=================================

From the web pages of the different project you will find instructions on how
to install them. Here we will cover the configuration part of the process, so
that the packages work together.


Configuration
=============

Environment variables
---------------------

Environment variables which are needed for pytroll packages are the
`PYTHONPATH` of course, and the `PPP_CONFIG_DIR`, which is the directory where
the configuration files are to be found. If the latter is not defined, the
`etc` directory of the mpop_ installation is used.

Input data directories
----------------------

The input data directories are setup in the satellite configuration files,
which can be found in the `PPP_CONFIG_DIR` directory (some template files are
provided with mpop_ in the `etc` directory):

.. code-block:: ini

   [seviri-level1]
   format = 'xrit/MSG'
   dir='/data/geo_in'
   filename='H-000-MSG?__-MSG?________-%(channel)s-%(segment)s-%Y%m%d%H%M-__'
   filename_pro='H-000-MSG?__-MSG?________-_________-%(segment)s-%Y%m%d%H%M-__'
   filename_epi='H-000-MSG?__-MSG?________-_________-%(segment)s-%Y%m%d%H%M-__'
        

   [seviri-level2]
   format='mipp'


The different levels indicate different steps of the reading. The `level2`
section gives at least the mpop_ plugin to read the data with. In some cases,
the data is first read from another level, as is this case with HRIT/LRIT data
when we use mipp_: there we use the `level1` section.

The data location is generally dealt in to parts: the directory and the
filename. There can also be additional filenames depending on the reader
plugin: here, mipp needs also the filename for prologue and epilogue files.

Note that the section starts with the name of the instrument. This is important
in the case where several instruments are available for the same satellite.
Note also that the filename can contain wildcards (`*` and `?`) and optional
values (here channel, segment, and time markers). It is up to the input plugin
to handle these constructs if needed.


.. _mipp: http://www.github.com/loerum/mipp
.. _mpop: http://www.github.com/mraspaud/mpop
