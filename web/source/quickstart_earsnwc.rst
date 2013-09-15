.. meta::
   :description: Reading EARS-NWC cloud products from NWC SAF PPS on NOAA/Metop AVHRR with python
   :keywords: EARS, NWC, AVHRR, NOAA, Metop, Nowcasting SAF, PPS, Cloud, Parameters, reader, read, reading, python, pytroll

=========================
 Quickstart with EARS-NWC
=========================

In December 2012 EUMETSAT_ extended the EARS_ services to include a new pilot
service with the purpose of supporting European users with cloud information
from polar orbiting satellites in near real time.

This *EARS-NWC* service provides the parameters *Cloud Mask*, *Cloud Type* and
*Cloud Top Temperature and Height (CTTH)* as derived using the Polar Platform
System (PPS_) software package from the `NWC SAF`_. The products are derived
from AVHRR data received at the EARS core stations with a reception coverage
including Europe and the North Atlantic. Products are disseminated on
EUMETCast_ (EUMETSAT `data channel 1`_) with a timeliness better than 30
minutes, and available in hdf5 format. The geolocation information is available
on a tie-point grid and stored in each product.

At the moment the satellites contributing to the service are Metop-A (being
substituted by Metop-B later during the spring 2013) and NOAA-19.

For this tutorial template config files (see :doc:`install`) can be used. These
are located in the *etc* dir of the mpop_ source. Copy *mpop.cfg.template*,
*areas.def.template*. *regionalnoaa19.cfg.template*, and
*regionalmetopa.cfg.template* to another dir and remove the *.template*
extension. In the config file *regionalnoaa19.cfg* locate the section
:attr:`avhrr-level3` and modify the defined :attr:`dir` to point to the dir of
your ears-nwc (bzip2 compressed) hdf5 files. The section :attr:`avhrr-level3`
should look something like this:

.. code-block:: ini

    [avhrr-level3]
    filename = %(product)s_%Y%m%d_%H%M00_%(satellite)s.h5*
    dir = /path/to/my/ears/nwc/data
    format = nwcsaf_pps

Set PPP_CONFIG_DIR to the directory containing your modified mpop_ config files.

Loading
=======

    >>> from mpop.satellites import PolarFactory
    >>> from datetime import datetime
    >>> orbit = ''
    >>> time_slot = datetime(2012, 12, 10, 11, 3)
    >>> glbd = PolarFactory.create_scene('noaa', '19', "avhrr", time_slot, orbit, variant='regional')
    >>> glbd.load(['CloudType'])
    [WARNING: 2013-02-14 22:17:12 : satin/nwcsaf_pps] No option 'geodir' in level3 section
    [WARNING: 2013-02-14 22:17:12 : satin/nwcsaf_pps] No Geo file specified: Geolocation will be loaded from product

Now we have loaded the Cloudtype product granule

    >>> print glbd['CloudType'].cloudtype.data
    [[ 8  8  8 ...,  8  8  8]
     [ 8  8  8 ...,  6  8  8]
     [ 8  8  8 ..., 19  8  8]
     ..., 
     [ 8  8  8 ..., 19  2 15]
     [ 8  8  8 ...,  2  2 16]
     [ 8  8  8 ...,  2  2  2]]

Also the geolocation has been unpacked. That is the the full resolution
geolocation information has been recreated from the tie point grid by
interpolating and extrapolating the longitudes and latitudes on the tie point
grid. This is accomplished using the python-geotiepoints_ tool, but this is
transparent to the user:

    >>> print glbd['CloudType'].area.lats.shape
    (351, 2048)

Now lets visualise the cloudtype data using the Nowcasting SAF palette:

    >>> import mpop.imageo.palettes
    >>> from mpop.imageo import geo_image
    >>> palette = mpop.imageo.palettes.cms_modified()
    >>> img = geo_image.GeoImage(glbd['CloudType'].cloudtype.data, None, time_slot, 
                                 fill_value = (0), mode = "P", palette = palette)
    >>> img.show()

.. image:: images/earsnwc_demo1.png

And for Metop-A:

   >>> orbit = ''
   >>> time_slot = datetime(2012, 12, 12, 8, 57)
   >>> glbd = PolarFactory.create_scene('metop', 'a', "avhrr", 
                                         time_slot, orbit, variant='regional')
   >>> glbd.load(['CloudType'])
   >>> print glbd['CloudType'].cloudtype.data
   [[ 2  2  2 ...,  1  1  1]
    [ 2  2  2 ...,  1  1  1]
    [ 2  2  2 ...,  1  1  1]
    ..., 
    [ 2  8 19 ...,  1  1  1]
    [ 6  8  8 ...,  1  1  1]
    [ 6  8  8 ...,  1  1  1]]


Stitching together the granules
===============================

The assemble_segments function in mpop.scene as for instance demonstrated in
the :doc:`quickstart_viirs` tutorial does not yet support stiching together
other data than the bare (level-1) instrument channel data. So for now we use
the internal attribute *_projectables* and create a custom function:

.. code-block:: python

    def assemble_segments(segments, projectables, parameter):
        """Concatenate the PPS parameters and geolocation on segments into one
        swath"""
        import numpy as np
    
        resdict = {}
        for item in projectables:
            resdict[item] = np.ma.concatenate([getattr(seg[parameter], item).data 
                                               for seg in segments])

        longitudes = np.ma.concatenate([seg[parameter].area.lons[:] 
                                        for seg in segments])
        latitudes = np.ma.concatenate([seg[parameter].area.lats[:] 
                                       for seg in segments])

        return resdict, longitudes, latitudes


We can now demonstrate how to collect CTTH granules and display it as one
swath:

.. code-block:: python

    >>> from mpop.satellites import PolarFactory
    >>> import mpop.imageo.palettes
    >>> from mpop.imageo import geo_image
    >>> from datetime import datetime, timedelta

    >>> orbit = ''
    >>> starttime = datetime(2012, 12, 10, 11, 0)
    >>> endtime = datetime(2012, 12, 10, 11, 15)

    >>> global_data = []
    >>> time_slot = starttime
    >>> tdelta = timedelta(seconds=60)
    >>> while time_slot < endtime + tdelta:
           glbd = PolarFactory.create_scene('noaa', '19', "avhrr", 
                                             time_slot, orbit, variant='regional')
           glbd.load(['CTTH'])
           # We only want to append it if data was really loaded:
           if len(glbd.channels) == 7:
               global_data.append(glbd) 
           time_slot = time_slot + tdelta

Now all the granules between 11:00 UTC and 11:15 UTC December 10, 2012, are
loaded and contained in the list *global_data*. Let's collect them with our
custom function above:

    >>> params, lons, lats = assemble_segments(global_data,
                                               global_data[0]['CTTH']._projectables,
                                               'CTTH')

And now we can display the data as usual, using the `NWC SAF`_ cloud top height palette:

    >>> palette = mpop.imageo.palettes.ctth_height_pps()
    >>> img = geo_image.GeoImage(params['height'], 
                                 None, time_slot, fill_value = (252), 
                                 mode = "P", palette = palette)
    >>> img.show()

.. image:: images/earsnwc_demo3.png


Re-projecting the collected swath
=================================

So, now it is time to re-project it to the area of interest. We then need pyresample_.

    >>> from pyresample import utils
    >>> from pyresample import kd_tree, geometry

And we need an area definition, which we have already defined in the
*areas.def* file:

    >>> import os
    >>> PPP_CONFIG_DIR = os.environ.get("PPP_CONFIG_DIR")
    >>> AREA_CONFIG_FILE = os.path.join(PPP_CONFIG_DIR, "areas.def")
    >>> area_def = utils.parse_area_file(AREA_CONFIG_FILE, areaid)[0]

Then we use the longitudes and latitudes from our assembled swath and
re-project or map the data:

    >>> swath_def = geometry.SwathDefinition(lons=lons, lats=lats)
    >>> pps_mapped = kd_tree.resample_nearest(swath_def, 
                                              params['height'].data, 
                                              area_def, 
                                              radius_of_influence=10000,
                                              fill_value=252,
                                              epsilon=100)
    >>> img = geo_image.GeoImage(pps_mapped, 
                                 areaid, 
                                 starttime, 
                                 fill_value = None,
                                 mode = "P",
                                 palette = palette)

And then add coast lines and political borders using pycoast_:

    >>> from pycoast import ContourWriter
    >>> cw_ = ContourWriter('/local_disk/data/shapes')
    >>> img = img.pil_image()
    >>> cw_.add_coastlines(img, area_def, resolution='i', level=3)
    >>> img.show()

.. image:: images/earsnwc_demo4.png


.. _EARS: http://www.eumetsat.int/home/main/satellites/groundnetwork/earssystem/index.htm
.. _EUMETCast: http://www.eumetsat.int/home/main/dataaccess/eumetcast/index.htm
.. _EUMETSAT: http://www.eumetsat.int/
.. _`NWC SAF`: http://www.nwcsaf.org/
.. _PPS: http://nwcsaf.smhi.se/
.. _python-geotiepoints: http://www.github.com/adybbroe/python-geotiepoints
.. _mpop: http://www.github.com/mraspaud/mpop
.. _pyresample: http://pyresample.googlecode.com
.. _pycoast: http://pycoast.googlecode.com
.. _`data channel 1`: http://www.eumetsat.int/home/main/dataaccess/eumetcast/receptionstationset-up/sp_20100623124251305?l=en
