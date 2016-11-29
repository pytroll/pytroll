SEVIRI RGB with the derived 3.9 micron reflectance
==================================================

    >>> from mpop.satellites import GeostationaryFactory
    >>> from datetime import datetime
    >>> tslot = datetime(2015, 4, 20, 10, 0)
    >>> glbd = GeostationaryFactory.create_scene("Meteosat-10", "", "seviri", tslot)

Load only the bands needed in order to create the *snow* RGB:

    >>> glbd.load(glbd.image.snow.prerequisites)
    >>> lcd = glbd.project('euro4')

And now we derive the *snow* rgb according to the `MSG Interpretation Guide`_. It requires pyspectral_:

    >>> img = lcd.image.snow()
    >>> img.add_overlay()
    >>> img.show()

.. image:: images/seviri_snow_euro4.png


Necessary configuration settings
--------------------------------

For this tutorial template config files (see :doc:`install`) can be used. These
are located in the *etc* dir of the mpop_ source. Copy *mpop.cfg.template*,
*areas.def.template* and *Meteosat-9.cfg.template* to another dir and remove
the *.template* extension. In the config file *Meteosat-9.cfg* locate the
section :attr:`severi-level1` and modify the defined :attr:`dir` to point to
the dir of your uncompressed HRIT data.

Set PPP_CONFIG_DIR to the directory containing your modified mpop_ config files.

.. _mpop: http://www.github.com/pytroll/mpop
.. _MSG Interpretation Guide: http://oiswww.eumetsat.org/WEBOPS/msg_interpretation/index.php 
.. _pyspectral: https://github.com/pytroll/pyspectral
