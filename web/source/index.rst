.. pytroll documentation master file, created by
   sphinx-quickstart on Mon Apr  4 15:14:52 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. meta::
   :description: Weather satellite data reading and processing with python
   :keywords: Meteosat, SEVIRI, AVHRR, Metop, NOAA, MODIS, Terra, Aqua, VIIRS,
   NPP, SDR, AAPP, HRPT, TerraSAR-X, COSMO-SkyMed, Radarsat-2, Himawari, Sentinel,
   read, reading, reader, process, processing, python, pytroll, 
   weather, satellite, data


Welcome to pytroll!
===================

This is the home of the pytroll project. The pytroll project started out in
2009 as a collaboration on weather satellite data processing between DMI_ and
SMHI_. Pytroll now has a growing international user base and is used
operationally at several National Met Services.

Its objective is provide different free and open source python modules for the
reading, interpretation, and writing of weather satellite data.

The provided python packages are designed to be used both in R&D environments
and in 24/7 operational production.

If you want to contact us, you can use the following mailing list:
https://groups.google.com/group/pytroll or chat with us on the pytroll slack: https://pytrollslackin.herokuapp.com/ or on the pytroll IRC channel on 
freenode: irc://irc.freenode.net/pytroll


.. note:: Pytroll workshop Offenbach 2016

          +--------------+
          |   |pict1|    |
          +--------------+
          | |figuretext| |
          +--------------+

.. |pict1| image:: _static/Group2_small.JPG
    :width: 800px

.. |figuretext| replace:: 

   A pytroll developers workshop was held at the Head Quarters of Deutscher
   Wetterdienst (DWD) in Offenbach between June 13 and 17, 2016. With the
   paticipation of 18 developers from the national Met Services of Switzerland,
   Norway, Denmark, Sweden, Finland and Germany, as well as EUMETSAT it was the
   largest to date.

   

The available pytroll python packages at the moment are:

* pyresample_ for resampling satellite data
* mipp_ for reading (mostly HRIT/LRIT formated) weather satellite data
* mpop_ for reading and processing weather satellite data
* python-bufr_ for reading bufr files
* pycoast_ for putting coastlines, borders and rivers on an image 
* pyorbital_ for computing satellite orbital parameters and reading TLE's
* posttroll_ a higher-level messaging library for pytroll
* pykdtree_ for really fast nearest neighbour search
* python-geotiepoints_ for interpolating (and extrapolation) geographic tiepoints
* trollimage_ the new image packagse for pytroll (replaces and enhances the image.py module in mpop)
* trollsift_ for the formatting, parsing and filtering of satellite granule file names
* pyspectral_ to read and manipulate satellite sensor spectral responses and solar irradiance spectra
* pydecorate_ to simplify the drawing of logos, text labels, color scales and legends onto images
* trollduction_ a framework for satellite batch processing
* pytroll-schedule_ to generate optimized satellite schedules for polar reception stations
* trollcast_ for realtime sharing of weather satellite data

Some more packages are in the process of being developed (you're very welcome
to have a look and give us a hand):

* satpy_ A refactored mpop_ (for reading and processing weather satellite data)
* pygranules_ for validating, fetching and scheduling satellite data granules


.. _DMI: http://www.dmi.dk
.. _SMHI: http://www.smhi.se
.. _pyresample: http://github.com/pytroll/pyresample
.. _mipp: http://github.com/pytroll/mipp
.. _mpop: http://github.com/pytroll/mpop
.. _satpy: https://github.com/pytroll/satpy
.. _python-bufr: http://github.com/pytroll/python-bufr
.. _pyorbital: http://github.com/pytroll/pyorbital
.. _pycoast: http://github.com/pytroll/pycoast
.. _python-geotiepoints: http://github.com/pytroll/python-geotiepoints
.. _posttroll: http://github.com/pytroll/posttroll
.. _pykdtree: https://github.com/storpipfugl/pykdtree
.. _trollcast: http://github.com/pytroll/trollcast
.. _pyspectral: https://github.com/pytroll/pyspectral
.. _pydecorate: http://code.google.com/p/pydecorate
.. _trollimage: https://github.com/pytroll/trollimage
.. _trollsift: https://github.com/pytroll/trollsift
.. _pygranules: http://pygranule.readthedocs.org/en/latest
.. _trollduction: https://github.com/pytroll/trollduction
.. _pytroll-schedule: https://github.com/pytroll/pytroll-schedule
.. _pytroll5years: https://www.youtube.com/watch?v=Sxphky9vwGc

Satellites supported (imager instruments) at the moment by the reader/processor
modules include: 

 - Meteosat series (tested with 7, 8, 9, 10)
 - GOES series, in HRIT/LRIT format (tested with 11, 12, 13, 15)
 - MTSAT series, in HRIT/LRIT format (tested with 1R, 2)
 - Himawari 8, in HRIT/LRIT format
 - Himawari 8, standard format (satpy_ only)
 - Electro L, in HRIT/LRIT format (tested with N1)
 - NOAA series, in AAPP, GAC and LAC format (tested with 15, 16, 17, 18, 19)
 - Metop-A/B, in EPS 1a and 1b format
 - Aqua and Terra, in hdf-eos format
 - Suomi NPP, in SDR hdf5 format
 - TerraSAR-X
 - Radarsat-2 SAR
 - COSMO-SkyMed SAR
 - Sentinel-1 SAR
 - Sentinel-2 MSI
 - FY-3 viir

Contents:

.. toctree::
   :maxdepth: 2

   install
   quickstart_seviri
   quickstart_avhrr
   quickstart_viirs
   quickstart_custom
   quickstart_bufr
   quickstart_earsnwc
   recipes
   past_workshops
   manifest
   guidelines
   five_year_anniversary
   shop

Contact us: https://groups.google.com/group/pytroll

