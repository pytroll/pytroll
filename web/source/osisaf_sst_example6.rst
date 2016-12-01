VIIRS OSISAF SSTs with color scale and coastlines
=================================================

   >>> from mpop.satellites import PolarFactory
   >>> from mpop.imageo import geo_image, palettes
   >>> import numpy as np
   >>> from datetime import datetime

   >>> glbd = PolarFactory.create_scene("Suomi-NPP", "", "viirs",
                                        datetime(2016, 9, 8, 13, 0), "")
   >>> glbd.load(['SST'])
   >>> areaid = 'euro4'
   >>> localdata = glbd.project(areaid)
   >>> sstdata = localdata["SST"].sst.data
   >>> palette = palettes.sstlut_osisaf_metno()

Mask data and convert from Kelvin to Celcius:

   >>> x = np.ma.where(np.less_equal(sstdata, 0), 0, sstdata - 273.15)

Convert sst to numbers between 0 and 28, corresponding to the lut:

   >>> data = np.ma.where(np.less(x, 0), 28, 28.0 - x)
   >>> data = np.ma.where(np.greater(x, 23.0), 4, data)
   
And we want discrete values:

   >>> data = data.round().astype('uint8')
   >>> img = geo_image.GeoImage(data,
                                areaid,
                                glbd.time_slot,
                                fill_value=(0),
                                mode="P",
                                palette=palette)
   >>> img.add_overlay(color=(220, 220, 220))
   >>> img.show()


.. image:: images/osisaf_sst_viirs.png


Necessary configuration settings
--------------------------------

For this tutorial template config files (see :doc:`install`) can be used. These
are located in the *etc* dir of the mpop_ source. Copy *mpop.cfg.template*,
*areas.def.template* and *Suomi-NPP.cfg.template* to another dir and remove
the *.template* extension. In the config file *Suomi-NPP.cfg* add a section
:attr:`viirs-level4` and modify the defined :attr:`sst_product_dir` to point to
the dir of your OSISAF SST data:

.. code-block:: ini

   [viirs-level4]
   sst_product_filename =S-OSI_-FRA_-NPP_-NARSST_FIELD-%Y%m%d%H00Z.nc
   sst_product_dir = /home/a000680/data/osisaf
   format = nc_osisaf_l2.OSISAF_SST_Reader


Set PPP_CONFIG_DIR to the directory containing your modified mpop_ config files.



.. _mpop: http://www.github.com/pytroll/mpop

