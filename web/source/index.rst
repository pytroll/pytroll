.. pytroll documentation master file, created by
   sphinx-quickstart on Mon Apr  4 15:14:52 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. meta::
   :description: Weather satellite data reading and processing with python
   :keywords: Meteosat, SEVIRI, AVHRR, Metop, NOAA, MODIS, Terra, Aqua, VIIRS, NPP, SDR, AAPP, HRPT, read, reading, reader, process, processing, python, pytroll, weather, satellite, data


Welcome to pytroll!
===================

This is the home of the pytroll project.  The pytroll project is a
collaboration on weather satellite data processing between DMI_ and SMHI_.

Its objective is provide different free and open source python modules for the
reading, interpretation, and writing of weather satellite data.

The provided python packages are designed to be used both in R&D environments
and in 24/7 operational production.

If you want to contact us, you can use the following mailing list:
https://groups.google.com/group/pytroll

.. note::
   A two day Pytroll workshop will be held in Norrköping, Sweden end of
   November (25-26). Please send a message on the pytroll mailing list
   (pytroll@googlegroups.com) if you are interested.


The available pytroll python packages at the moment are:

* pyresample_ for resampling satellite data
* mipp_ for reading weather satellite data
* mpop_ for processing weather satellite data
* python-bufr_ for reading bufr files
* pycoast_ for putting coastlines, borders and rivers on an image 
* pyorbital_ for computing satellite orbital parameters and reading TLE's

Some more packages are in the process of being developed (you're very welcome
to have a look and give us a hand):

* python-geotiepoints_ for interpolating (and extrapolation) geographic tiepoints
* posttroll_ for a higher-level messaging library for pytroll
* pykdtree_ for really fast nearest neighbour search
* trollcast_ for realtime sharing of weather satellite data

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
.. _pykdtree: https://github.com/storpipfugl/pykdtree
.. _trollcast: http://github.com/mraspaud/trollcast

Satellites supported (imager instruments) at the moment by the reader/processor
modules include: 

 - Meteosat series (tested with 7, 8, 9, 10)
 - GOES series, in HRIT/LRIT format (tested with 11, 12, 13, 15)
 - MTSAT series, in HRIT/LRIT format (tested with 1R, 2)
 - Electro L, in HRIT/LRIT format (tested with N1)
 - NOAA series, in AAPP format (tested with 15, 16, 17, 18, 19)
 - Metop-A/B, in EPS 1a and 1b format
 - Aqua and Terra, in hdf-eos format
 - Suomi NPP, in SDR hdf5 format

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
   workshop2012

Contact us: https://groups.google.com/group/pytroll

