================================
 Installation and configuration
================================

Installing the different packages
=================================

From the web pages of the different project you will find instructions on how
to install them. Here we will cover the configuration part of the process, so
that the packages work together.
These documentation pages focus on the usage of mpop for processing of satellite data. So as a minimum this package should be installed. 
mpop uses plugins for reading of satellite data. In order to read the MSG SEVERI data used in many of the document examples the mipp package should be installed.
In order to resample image data with mpop the package pyresample must be installed.

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
section gives at the mpop_ plugin to read the data with. In some cases,
the data is first read from another level, as is this case with HRIT/LRIT data
when we use mipp_: there we use the `level1` section.

The data location is generally dealt in two parts: the directory and the
filename. There can also be additional filenames depending on the reader
plugin: here, mipp needs also the filename for prologue and epilogue files.

Note that the section starts with the name of the instrument. This is important
in the case where several instruments are available for the same satellite.
Note also that the filename can contain wildcards (`*` and `?`). It is up to
the input plugin to handle these constructs if needed.


Some words on NPP VIIRS configuration
-------------------------------------

The configuration for reading npp data is provided in the template file
`npp.cfg.template` included in mpop_, just as in the case of MSG discussed
above and like many other satellites. So far mpop_ only reads VIIRS, but feel
free to write your own reader for ATMS or CrIS. For VIIRS the configuration may
look like this:

.. code-block:: ini

   [satellite]
   satname = npp
   variant = 
   number = 
   instruments = ('viirs',)

   [viirs-level2]
   filename = SV???_%(satellite)s_d*b%(orbit)s_c*.h5
   geo_filenames = G????_%(satellite)s_d*b%(orbit)s_c*.h5
   dir = /data/viirs/sdr
   format = viirs_sdr.ViirsSDRReader


Different from the SEVIRI example above here we see a `geo_filenames`
entry. This is not mandatory, however, as will be clear from the following.

For VIIRS data, where there (except for the DNB) are two possible and different
types of geolocation information (terrain corrected and geoid) and where each
band-type (I- and M-bands and the DNB) has its own geolocation it is common to
have the geolocation data in separate files, separate from the band-data. Thus,
the configuration file allows you to specify the naming of these files.

If the parameter `geo_filenames` is not set the geolocation file pointed to by
the value of `N_GEO_Ref` given in the SDR file will be used.
 
You can of course keep your archive of NPP VIIRS SDR scenes in separate
sub-directories, so that each scene or pass has its own directory. This might
e.g. look like this:

.. code-block:: ini

   [viirs-level2]
   filename = SV???_%(satellite)s_d????????_t???????_e???????_b%(orbit)s_*cspp_dev.h5
   dir = /data/proj/satval/data/npplvl1/%(satellite)s_%Y%m%d_*_%(orbit)s
   format = viirs_sdr.ViirsSDRReader

As you can see here we use the geolocation file specified in the header of the
SDR band data files.



.. _mipp: http://www.github.com/loerum/mipp
.. _mpop: http://www.github.com/mraspaud/mpop
