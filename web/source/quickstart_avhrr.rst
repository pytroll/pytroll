.. meta::
   :description: Reading NOAA/METOP AVHRR files with python
   :keywords: AVHRR, NOAA, METOP, AAPP, HRPT, reader, read, reading, python, pytroll

======================
 Quickstart with AVHRR
======================
For this tutorial, we will use AVHRR HRPT data in the level1b format produced
by AAPP_, read the data into mpop_, generate the full geolocation using
python-geotiepoints_, and resample it with pyresample_ and process it a
bit. Install theses packages first.

Observe that the AAPP_ level1b file does not contain the geolocation in full
resolution, but with the python-geotiepoints_ plugged in the full resolution
longitudes and latitudes will be provided to you when reading the data. You
should not normally notice that the interpolation and extrapolation is invoked.

For this tutorial template config files (see :doc:`install`) can be used. These
are located in the *etc* dir of the mpop_ source. Copy *mpop.cfg.template*,
*areas.def.template* and *NOAA-19.cfg.template* to another dir and remove the
*.template* extension. In the config file *noaa19.cfg* locate the section
:attr:`avhrr-level2` and modify the defined :attr:`dir` to point to the dir of
your level1b AVHRR data.

Set PPP_CONFIG_DIR to the directory containing your modified mpop_ config files.
    
First example: Loading data
===========================
This example assumes AAPP level1b data from NOAA-19 with the timestamp 29/8-2011
11:40 orbit 13173 exists in the :attr:`dir` defined in the :attr:`avhrr-level2`
section of your noaa19 configuration file. Change the arguments to the creation
of :attr:`time_slot` and the :attr:`create_scene` function in the code example
to match your data.

    >>> from mpop.satellites import PolarFactory
    >>> from datetime import datetime
    >>> orbit = "13173"
    >>> time_slot = datetime(2011,8,29,11,40)
    >>> global_data = PolarFactory.create_scene("NOAA-19", "", "avhrr", time_slot, orbit)
    >>> global_data.load([10.8])
    '1: (0.580,0.630,0.680)μm, resolution 1090m, not loaded'
    '2: (0.725,0.863,1.000)μm, resolution 1090m, not loaded'
    '3A: (1.580,1.610,1.640)μm, resolution 1090m, not loaded'
    '3B: (3.550,3.740,3.930)μm, resolution 1090m, not loaded'
    '4: (10.300,10.800,11.300)μm, shape (5489, 2048), resolution 1090m'
    '5: (11.500,12.000,12.500)μm, resolution 1090m, not loaded'
    
We have now loaded the 10.8 µm channel from the NOAA-19 swath.


.. note:: In earlier versions of mpop_ you would create the scene object by
          specifying *"noaa"* as the first argument and *"19"*
          as the second in :meth:`PolarFactory.create_scene`. However,
          now we have standardised the naming of satellites to follow the WMO
          naming conventions and thus leaving the second argument empry.

Handling data
=============
The :attr:`global_data` object supports the same operations when used for any
type of satellite data. So the examples from the :doc:`quickstart_seviri`
tutorial applies here as well.

Showing a channel:

    >>> global_data.image.channel_image(10.8).show()
    
.. image:: images/avhrr_ch4.png

Getting the data as a numpy array:

    >>> my_array = global_data[10.8].data
    >>> print type(my_array)
    <class 'numpy.ma.core.MaskedArray'>
    
Making RGB composites
=====================
The procedure for making RGBs is the same as in the :doc:`quickstart_seviri` tutorial:

    >>> global_data.load(global_data.image.overview.prerequisites)
    >>> img = global_data.image.overview()
    >>> img.save("./avhrr_overview.png")
    
.. image:: images/avhrr_overview.png

Note that the builtin composites available varies from sensor to sensor and the :meth:`load` method cannot take an :attr:`area_extent` argument when working with AVHRR data.

Projections
===========
Reprojecting data is done analogous to the way the SEVIRI data was reprojected in the :doc:`quickstart_seviri` tutorial:

    >>> local_data = global_data.project("euro_north", mode="nearest")
    >>> img = local_data.image.overview()
    >>> img.save("./avhrr_local_overview.png")

.. image:: images/avhrr_local_overview.png

Note the *mode="nearest"* argument for :meth:`project` is currently needed to make mpop select an appropriate type of resampling for swaths.

Channel arithmetics
===================

The common arithmetical operators are supported on channels, so that one can
run for example::

  >>> ndvi = (local_data["2"] - local_data["1"]) / (local_data["2"] + local_data["1"])
  >>> ndvi.show()
  
.. image:: images/avhrr_ndvi.png

Making custom composites
========================
Making custom composites can be done using the same recipe as described in the :doc:`quickstart_seviri` tutorial.

Assuming a *my_composites.py* file has been created as described in the :doc:`quickstart_seviri` tutorial add the following lines to the file::
    
    def red_clouds(self):
        """Make and RGB with red clouds
        """
        
        self.check_channels(0.6, 3.7, 10.8)
        img = GeoImage((self[0.6].data, self[3.7].data, self[10.8].data), 
                        self.area, self.time_slot,
                        fill_value=(0, 0, 0), mode="RGB")
        img.enhance(stretch="crude")
        return img

    red_clouds.prerequisites = set([0.6, 3.7, 10.8])
        
    avhrr = [red_clouds]
    
Add the dir containing *my_composites.py* to your PYTHONPATH. Now your new
:attr:`red_clouds` composite will be accessible on the :attr:`scene.image`
object for AVHRR like the builtin composites::

    >>> from mpop.satellites import PolarFactory
    >>> from datetime import datetime
    >>> orbit = "13173"
    >>> time_slot = datetime(2011,8,29,11,40)
    >>> global_data = PolarFactory.create_scene("NOAA-19", "", "avhrr", time_slot, orbit)
    >>> global_data.load(global_data.image.red_clouds.prerequisites)
    >>> local_data = global_data.project("euro_north", mode="nearest")
    >>> img = local_data.image.red_clouds()
    >>> img.show()
    
.. image:: images/avhrr_red_clouds.png

.. _AAPP: http://nwpsaf.eu/site/software/aapp/
.. _`NWC SAF`: http://www.nwcsaf.org/HD/MainNS.jsp
.. _`NWC SAF homepage`: http://www.nwcsaf.org/HD/MainNS.jsp
.. _mpop: http://www.github.com/pytroll/mpop
.. _python-geotiepoints: http://www.github.com/adybbroe/python-geotiepoints
.. _pyresample: http://www.github.com/pytroll/pyresample
.. _`Download the latest patched version of AHAMAP here`: _static/ahamap-pps-2010-patches_20110831-1.tgz
.. _numpy: http://numpy.scipy.org/
.. _proj4: http://trac.osgeo.org/proj/

