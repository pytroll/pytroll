.. pytroll documentation master file, created by
   sphinx-quickstart on Mon Apr  4 15:14:52 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. meta::
   :description: Weather satellite data reading and processing with python
   :keywords: Meteosat, SEVIRI, AVHRR, METOP, NOAA, MODIS, TERRA, AQUA, VIIRS, NPP, SDR, AAPP, HRPT, read, reading, reader, process, processing, python, pytroll, weather, satellite, data


Welcome to pytroll!
===================

This is the home of the pytroll project.  The pytroll project is a
collaboration on weather satellite data processing between DMI_ and SMHI_.

Its objective is provide different free and open source python modules for the
reading, interpretation, and writing of weather satellite data.

The provided python packages are designed to be used both in R&D environments
and in 24/7 operational production.

.. note::
   mipp_ version 0.9 with support for Meteosat-10 is out now!

   Met-10 will take over from Met-9 as the prime satellite for the 0-degree service January 21.


The available python packages at the moment are:

* pyresample_ for resampling satellite data
* mipp_ for reading weather satellite data
* mpop_ for processing weather satellite data
* python-bufr_ for reading bufr files
* pycoast_ for putting coast lines on an image 

Some more packages are in the process of being developped (you're very welcome
to have a look and give us a hand):

* pyorbital_ for computing satellite orbital parameters and reading TLE's
* python-geotiepoints_ for interpolating (and extrapolation) geographic tiepoints
* posttroll_ for a higher-level messaging library for pytroll

.. _DMI: http://www.dmi.dk
.. _SMHI: http://www.smhi.se
.. _pyresample: http://pyresample.googlecode.com
.. _mipp: http://www.github.com/loerum/mipp
.. _mpop: http://www.github.com/mraspaud/mpop
.. _python-bufr: http://python-bufr.googlecode.com
.. _pyorbital: http://www.github.com/mraspaud/pyorbital
.. _pycoast: http://pycoast.googlecode.com
.. _python-geotiepoints: http://www.github.com/adybbroe/python-geotiepoints
.. _posttroll: http://github.com/mraspaud/posttroll


Satellites supported (imager instruments) at the moment by the reader/processor
modules include: 

 - Meteosat series (tested with 7, 8, 9)
 - GOES series, in HRIT/LRIT format (tested with 11, 12, 13, 15)
 - MTSAT series, in HRIT/LRIT format (tested with 1R, 2)
 - Electro L, in HRIT/LRIT format (tested with N1)
 - NOAA series, in AAPP format (tested with 15, 16, 17, 18, 19)
 - Metop-A, in EPS 1a and 1b format
 - Aqua and Terra, in hdf-eos format
 - NPP, in SDR hdf format

Contents:

.. toctree::
   :maxdepth: 2

   install
   quickstart_seviri
   quickstart_avhrr
   quickstart_viirs
   quickstart_custom
   quickstart_bufr
   recipes
   workshop2012

Contact us: https://groups.google.com/group/pytroll

