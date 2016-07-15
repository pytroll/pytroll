.. meta::
   :description: Reading NPP VIIRS SDR files with python
   :keywords: VIIRS, NPP, SDR, reader, read, reading, python, pytroll

==================
VIIRS with Pytroll
==================
The NOAA/NASA weather satellite Suomi National Polar Partnership (Suomi-NPP)
satellite was successfully launched October 28th, 2011.

Suomi-NPP carries the Visible Infrared Imaging Radiometer Suite (VIIRS) which
is a moderate resolution Imager with herritage from MODIS onboard the EOS
satellites Aqua and Terra, the AVHRR onboard the NOAA and Metop platforms, and
the OLS onboard the DMSP satellites. VIIRS has a nearly constant spatial
resolution across a very large swath (width is around 3000km).

In preparation for VIIRS we made a plugin reader and custom compositer to
mpop_. This was tested on synthetic (sample) data prior to launch, allowing us
to produce VIIRS imagery as soon as Direct Readout was turned on.

The example images below have been generated from direct readout data from the
station in Norrköping. We have been using the Community Satellite Processing
Package (CSPP) to go from RDR to SDR - see cspp_

For this tutorial template config files (see :doc:`install`) can be used.
These are located in the *etc* dir of the mpop_ source. Copy
*mpop.cfg.template*, *areas.def.template* and *Suomi-NPP.cfg.template* to another dir
and remove the *.template* extension. In the config file *Suomi-NPP.cfg* locate the
section :attr:`viirs-level2` and modify the defined :attr:`dir` to point to the
directory where you keep the SDR data.

Set PPP_CONFIG_DIR to the directory containing your modified mpop_ config files.


Loading
=======

    >>> from mpop.satellites import PolarFactory
    >>> from datetime import datetime
    >>> time_slot = datetime(2013, 6, 25, 11, 15)
    >>> orbit = "08599"
    >>> global_data = PolarFactory.create_scene("Suomi-NPP", "", "viirs", time_slot, orbit)
    >>> global_data.load([1.38])
    >>> print global_data
     -------> print(global_data)
     'M01: (0.402,0.412,0.422)μm, resolution 742m, not loaded'
     'M02: (0.436,0.445,0.454)μm, resolution 742m, not loaded'
     'M03: (0.478,0.488,0.498)μm, resolution 742m, not loaded'
     'M04: (0.545,0.555,0.565)μm, resolution 742m, not loaded'
     'M05: (0.662,0.672,0.682)μm, resolution 742m, not loaded'
     'M06: (0.739,0.746,0.754)μm, resolution 742m, not loaded'
     'M07: (0.846,0.865,0.885)μm, resolution 742m, not loaded'
     'M08: (1.230,1.240,1.250)μm, resolution 742m, not loaded'
     'M09: (1.371,1.378,1.386)μm, shape (768, 3200), resolution 742m'
     'M10: (1.580,1.610,1.640)μm, resolution 742m, not loaded'
     'M11: (2.225,2.250,2.275)μm, resolution 742m, not loaded'
     'M12: (3.610,3.700,3.790)μm, resolution 742m, not loaded'
     'M13: (3.973,4.050,4.128)μm, resolution 742m, not loaded'
     'M14: (8.400,8.550,8.700)μm, resolution 742m, not loaded'
     'M15: (10.263,10.763,11.263)μm, resolution 742m, not loaded'
     'M16: (11.538,12.013,12.489)μm, resolution 742m, not loaded'
     'I01: (0.600,0.640,0.680)μm, resolution 371m, not loaded'
     'I02: (0.845,0.865,0.884)μm, resolution 371m, not loaded'
     'I03: (1.580,1.610,1.640)μm, resolution 371m, not loaded'
     'I04: (3.580,3.740,3.900)μm, resolution 371m, not loaded'
     'I05: (10.500,11.450,12.300)μm, resolution 371m, not loaded'
     'DNB: (0.500,0.700,0.900)μm, resolution 742m, not loaded'

We have now loaded the VIIRS M09 band. Now let us look at the data:
 
    >>> img = global_data.image.channel_image(1.38)
    >>> img.enhance(stretch='histogram')
    >>> img.show()

.. image:: images/viirs_m09.png


The black stripes are due to the so called *bowtie deletion*, which is handled
onboard the satellite. The *bowtie* effect is a geometric feature of the VIIRS
scan. Similar to the MODIS sensor individual VIIRS lines will overlap as one
approach the edge of the swath. These overlapping samples/pixels have been
removed onboard in order to minimise the bandwidth usage on the broadcast. Thus
when data are displayed un-projected these no-data lines will appear in the
image.


Making RGB's
============

Here is an example making a true color RGB with the VIIRS bands:

    >>> global_data.load(global_data.image.truecolor.prerequisites)
    >>> img = global_data.image.truecolor()
    >>> img.save("./viirs_truecolor.png")

.. image:: images/viirs_truecolor.png

.. include:: viirs_geoloc.rst

Map projection
==============

Reprojecting data is done in exactly the same way the AVHRR data was reprojected in 
the :doc:`quickstart_avhrr` tutorial:

    >>> local_data = global_data.project("scan500m", mode="nearest")
    >>> img = local_data.image.truecolor()
    >>> img.save('./viirs_truecolor_proj.png')

Here we have defined an area called *area500m* covering Scandinavia, and with a
pixel resolution of 500 meters. This definition is stored in the
*areas.def.template* file. See the :doc:`quickstart_avhrr` tutorial.

It is easier to navigate in the image if we add coastlines and poltical
boarders, so lets do that with PIL and pycoast_:

    >>> from PIL import Image
    >>> from pycoast import ContourWriter
    >>> from mpop.projector import get_area_def
    >>> cw = ContourWriter('/local_disk/data/shapes')
    >>> img = Image.open('./viirs_truecolor_proj.png')
    >>> area_def = get_area_def("scan500m")
    >>> cw.add_coastlines(img, area_def, resolution='i', level=3)
    >>> img.save('./viirs_truecolor_proj_with_overlay.png')

.. image:: images/viirs_truecolor_proj_with_overlay.png

But what we actually wanted was to load all the available data (VIIRS granules)
received that covers the area. To do this in a smart and economical way we only
load the granules that are inside the area of interest. The VIIRS reader in
mpop_ version 1.x and later supports loading of granules within a certain time
interval. Optimally we would like to load granules by area coverage, but this
is not yet possible in mpop_ alone. With the functionality provided by
pyorbital_ and pyresample_ it will however be possible to do this. We leave
this for an other time, and instead we try load the granules by specifying a
time interval that we think will cover the area of interest:


    >>> from mpop.satellites import PolarFactory
    >>> from datetime import datetime
    >>> orbit = "08599"
    >>> tslot = datetime(2013, 6, 25, 11, 11)
    >>> starttime = datetime(2013, 6, 25, 11, 11)
    >>> endtime = datetime(2013, 6, 25, 11, 18)
    >>> glbd = PolarFactory.create_scene("Suomi-NPP", "", 
    ...                                  "viirs", tslot, 
    ...                                   orbit)
    >>> glbd.load(glbd.image.green_snow.prerequisites |
    ...           glbd.image.natural.prerequisites,
    ...           time_interval=(starttime, endtime))
    >>> img = glbd.image.natural()
    >>> img.show()

.. image:: images/npp_20130625_1111_08599_natural.png

And now lets project it to the area:

    >>> local_data = glb_data.project(areaid, mode="nearest", radius=2000)

We can display the *green_snow* composite as we already made sure to load the
necessary channels earlier (see code above):

    >>> img = local_data.image.green_snow()
    >>> img.show()

.. image:: images/npp_20130625_1111_08599_scan500m_green_snow.png


High resolution images
======================

The VIIRS sensor have 5 AVHRR-like channels with a resolution 3 times higher or
even better (at edge of swath). These are the I-bands seen in the list
above. Making imagery from these goes exactly the same way as for the
M-bands. However, since there is overlap in the spectral range between I-bands
and M-bands, you need to specify also the resolution or use the band name when
loading:

    >>> global_data.load(['I03'])
    >>> global_data['I03'].show()

.. image:: images/viirs_i03.png


Generating and mapping the overview of the I-bands is done in the same way as
for the M-bands of course.  Here we have made a specific I-band overview method
called *hr_overview*:

    >>> from mpop.satellites import PolarFactory
    >>> from datetime import datetime
    >>> orbit = "08599"
    >>> time_slot = datetime(2013, 6, 25, 11, 15)
    >>> global_data = PolarFactory.create_scene("Suomi-NPP", "", "viirs", time_slot, orbit)
    >>> global_data.load(global_data.image.hr_overview.prerequisites)
    >>> local_data = global_data.project("scan500m", mode="nearest")
    >>> img = local_data.image.hr_overview()
    >>> img.show()

.. image:: images/viirs_hr_overview_proj.png


The Day/Night Band
==================

The VIIRS Day/Night band draws heritage from the DMSP Operational Linescan
System (OLS) and is a broad band channel in the Visible and Near-Infrared
spectral range. It operates with three different gains to optimise the
sensitivity independant of illumination. We find a nighttime case with some
moonlight, and make a stretched black and white image for display:

    >>> time_slot = datetime(2012, 8, 31, 1, 8)
    >>> orbit = "04365"
    >>> global_data = PolarFactory.create_scene("Suomi-NPP", "", "viirs", time_slot, orbit)
    >>> global_data.load(['DNB'])
    >>> global_data.image.dnb().show()

.. image:: images/npp_20131020_0126_10252_dnb_linear.png

During nighttime it is sufficiently sensitive so that useful information on
clouds and surfaces may be deduced from reflected moonlight. Naturally the
units of this band cannot be given as a solar reflectance factor, but instead
the radiance is provided:

    >>> print global_data['DNB'].info
        {'units': 'W sr-1 m-2', 'band_id': 'DNB'}

The units in the HDF5 SDR file is :math:`W cm^{-2} sr^{-1}` (see table 2.18.2-1, page 355 of
the NPOESS Common Data Format Control Book - Volume III - D34862-03 Rev E CDRL
No. A014). But in pytroll we keep to the physical units dictated by the netCDF
`CF convention`_ on metadata, which is :math:`W m^{-2} sr^{-1}`.

Observe that this is really the spectral radiance *integrated* over the entire
band of wavelengths from 500 to 900 nm, and *not* a spectral radiance
(e.g. unit W/(sr*m²*μm) which is otherwise common for narrow band channels.

    >>> print global_data['DNB'].data
    [[-- 0.000163395772688 0.000175373905222 ..., 0.000117216048238
      0.000115083799756 0.000105939005152]
     [-- 0.000170526851434 0.000165672157891 ..., 0.000114827875223
      0.000116445145977 0.000109282387712]
     [-- 0.000161146308528 0.000150438645505 ..., 0.000113979120215
      0.000117577423225 0.000114215945359]
     ..., 
     [-- 0.0001579762029 0.000168871047208 ..., 5.65401896893e-05
      5.81711428822e-05 6.36076947558e-05]
     [-- 0.000155943780555 0.000146388818393 ..., 6.1892089434e-05
      6.02728396188e-05 5.55949372938e-05]
     [-- 0.000157967660925 0.000157781381859 ..., 6.59923025523e-05
      6.20885184617e-05 5.79988991376e-05]]


We can check the range of radiaces in the granule and in print it in the units
given in the input file if we like:

    >>> print (global_data['DNB'].data * 10000).min()
    0.271491
    >>> print (global_data['DNB'].data * 10000).max()
    56.9676


Let us load a few granules and assemble them and reproject them to get an image
covering Scandinavia:

    >>> time_slot = datetime(2013, 10, 20, 1, 26)
    >>> starttime = datetime(2013, 10, 20, 1, 26)
    >>> endtime = datetime(2013, 10, 20, 1, 34)
    >>> orbit = "10252"
    >>> global_data = PolarFactory.create_scene("Suomi-NPP", "", "viirs", time_slot, orbit)
    >>> global_data.load(['DNB'], time_interval=(starttime, endtime))
    >>> local_data = global_data.project('scan500m', mode="nearest", radius=2000)
    >>> img = local_data.image.dnb(stretch='linear')
    >>> img.show()


.. image:: images/npp_20131020_0126_10252_scan500m_dnb.png



.. _`CF convention`: http://cf-pcmdi.llnl.gov/
.. _`NPP sample`: http://npp.gsfc.nasa.gov/NPP_NCT4_SAMPLE_PRODUCTS.zip
.. _mpop: http://www.github.com/mraspaud/mpop
.. _cspp: http://cimss.ssec.wisc.edu/cspp
.. _pycoast: http://pycoast.googlecode.com
.. _pyresample: http://pyresample.googlecode.com
.. _pyorbital: http://www.github.com/mraspaud/pyorbital
