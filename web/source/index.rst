.. pytroll documentation master file, created by
   sphinx-quickstart on Mon Apr  4 15:14:52 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. meta::
   :description: Weather satellite data reading and processing with python
   :keywords: Meteosat, SEVIRI, AVHRR, Metop, NOAA, MODIS, Terra, Aqua, VIIRS,
   Suomi-NPP, NPP, JPSS, SDR, AAPP, CSPP, HRPT, TerraSAR-X, COSMO-SkyMed,
   Radarsat-2, Himawari, Sentinel, SLSTR, OLCI, Sentinel-1, Sentinel-2,
   Sentinel-3, GOES-R, ABI, GOES-16, read, reading, reader, process,
   processing, python, pytroll, weather, satellite, data



Welcome to pytroll!
===================

.. This is the home of the pytroll project. The pytroll project started out in
   2009 as a collaboration on weather satellite data processing between DMI_ and
   SMHI_. Pytroll now has a growing international user base and is used
   operationally at several National Met Services.

The objective of Pytroll is to provide an easy to use, modular, free and open
source python framework for the processing of earth observation satellite
data. The provided python packages are designed to be used both in R&D
environments and in 24/7 operational production.

The focus is on atmospheric applications and imaging sensors, but as seen from
the list of supported satellite sensors below the data that can be handled py
Pytroll allows the usage in a wide range of earth sciences.


.. note:: Pytroll at the 2017 Eumetsat Conference

      Dave and Adam gave a `Pytroll overview`_ at the 2017 Eumetsat conference
      in Rome Tuesday 3rd. Thanks for attending the few who found the way to
      the slightly remote small workshop room!

      .. image:: images/pytroll_light_big.png
       :width: 217px


.. For a quick and easy overview of what Pytroll can possibly offer for you have a
   look at the `Pytroll overview`_ which was given at the Eumetsat conference
   in Rome Tuesday October 3.

   
If you want to contact us, you can use the following mailing list:
https://groups.google.com/group/pytroll or chat with us on the pytroll slack: https://pytrollslackin.herokuapp.com/ or on the pytroll IRC channel on 
freenode: irc://irc.freenode.net/pytroll


.. note:: Centre Météorologie Spatiale, Météo-France, Lannion, September 2017

          +-------------+
          |   |pict|    |
          +-------------+
          | |figtxt|    |
          +-------------+

.. |pict| image:: _static/PytrollGroupLannion20170914_small.JPG
    :width: 770px

.. |figtxt| replace:: 

   A pytroll developers workshop took place at the Céntre Météorologie Spatiale
   in Lannion, Brittany, France, from 11-15 of September 2017. 15 participants
   from several national Meteorological Institutes in Europe, incldung
   Switzerland, Germany, Denmark, Iceland, Finland, Sweden, and France, worked
   concentrated during one week improving and enhancing the Pytroll software.



The available pytroll python packages at the moment are:

* pyresample_ for resampling satellite data
* pykdtree_ for really fast nearest neighbour search
* python-geotiepoints_ for interpolating (and extrapolation) geographic tiepoints
* mpop_ for reading and processing weather satellite data
* satpy_ A refactored mpop_ (for reading and processing weather satellite data)
* mipp_ for reading (mostly HRIT/LRIT formated) weather satellite data
* pycoast_ for putting coastlines, borders and rivers on an image 
* pyorbital_ for computing satellite orbital parameters and reading TLE's
* posttroll_ a higher-level messaging library for pytroll
* trollimage_ the new image packagse for pytroll (replaces and enhances the image.py module in mpop)
* trollsift_ for the formatting, parsing and filtering of satellite granule file names
* pyspectral_ to read and manipulate satellite sensor spectral responses and solar irradiance spectra
* pydecorate_ to simplify the drawing of logos, text labels, color scales and legends onto images
* trollduction_ a framework for satellite batch processing
* trollflow_ a small workflow execution framework (eventually replacing trollduction_)
* pytroll-schedule_ to generate optimized satellite schedules for polar reception stations
* trollcast_ for realtime sharing of weather satellite data
* pytroll-file-utils_ for moving files in real time between nodes using posttroll_ messaging
* pytroll-collectors_ e.g. to gather granules over an area interest for real time processing
* pygac_ to read NOAA AVHRR Global Area Coverage (GAC) data and apply state of the art calibration and navigation


Some more packages are in the process of being developed (you're very welcome
to have a look and give us a hand):

* pygranules_ for validating, fetching and scheduling satellite data granules
* trollbufr_ for reading BUFR files

Satellites supported (imager instruments) at the moment by the reader/processor
modules include: 

 - Meteosat series (tested with 7, 8, 9, 10, 11)
 - GOES series, in HRIT/LRIT format (tested with 11, 12, 13, 15, 16)
 - MTSAT series, in HRIT/LRIT format (tested with 1R, 2)
 - Himawari 8 & 9, in HRIT/LRIT format
 - Himawari 8 & 9, standard format (satpy_ only)
 - Electro L, in HRIT/LRIT format (tested with N1)
 - NOAA series, in AAPP, GAC and LAC format (tested with TIROS-N to NOAA-19)
 - Metop-A/B, in EPS 1a and 1b format
 - Aqua and Terra MODIS, in hdf-eos format
 - Suomi NPP, in SDR hdf5 format
 - TerraSAR-X
 - Radarsat-2 SAR
 - COSMO-SkyMed SAR
 - Sentinel-1 SAR
 - Sentinel-2 MSI
 - Sentinel-3 SLSTR & OLCI
 - FY-3 viir
 - GCOM-W1 AMSR2 in hdf5 format

See also `satpy documentation pages`_ for a list of file formats supported by satpy_.


  
.. _`Pytroll overview`: https://docs.google.com/presentation/d/10QSq6H0QL4WruEiY-1TU4Rk-f05QzZOZ1UoD9adx9ow/edit?usp=sharing
.. _DMI: http://www.dmi.dk
.. _SMHI: http://www.smhi.se
.. _pyresample: http://github.com/pytroll/pyresample
.. _mipp: http://github.com/pytroll/mipp
.. _mpop: http://github.com/pytroll/mpop
.. _satpy: https://github.com/pytroll/satpy
.. _satpy documentation pages: http://satpy.readthedocs.io/en/latest
.. _python-bufr: http://github.com/pytroll/python-bufr
.. _pyorbital: http://github.com/pytroll/pyorbital
.. _pycoast: http://github.com/pytroll/pycoast
.. _python-geotiepoints: http://github.com/pytroll/python-geotiepoints
.. _posttroll: http://github.com/pytroll/posttroll
.. _pykdtree: https://github.com/storpipfugl/pykdtree
.. _trollcast: http://github.com/pytroll/trollcast
.. _pytroll-file-utils: http://github.com/pytroll/pytroll-file-utils
.. _pyspectral: https://github.com/pytroll/pyspectral
.. _pydecorate: http://code.google.com/p/pydecorate
.. _trollimage: https://github.com/pytroll/trollimage
.. _trollsift: https://github.com/pytroll/trollsift
.. _pytroll-collectors: https://github.com/pytroll/pytroll-collectors
.. _pygranules: http://pygranule.readthedocs.org/en/latest
.. _trollduction: https://github.com/pytroll/trollduction
.. _trollflow: https://github.com/pytroll/trollflow
.. _pygac: https://github.com/pytroll/pygac
.. _trollbufr: https://github.com/alexmaul/trollbufr
.. _pytroll-schedule: https://github.com/pytroll/pytroll-schedule
.. _pytroll5years: https://www.youtube.com/watch?v=Sxphky9vwGc




Contents:

.. toctree::
   :maxdepth: 2

   gallery
   install
   quickstart_seviri
   quickstart_avhrr
   quickstart_viirs
   quickstart_custom
   ..
      quickstart_bufr
   quickstart_earsnwc
   recipes
   past_workshops
   manifest
   guidelines
   five_year_anniversary
   shop

Contact us: https://groups.google.com/group/pytroll

