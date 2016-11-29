Making SEVIRI RGB Overview composite with mpop
==============================================

    >>> from mpop.satellites import GeostationaryFactory
    >>> from mpop.projector import get_area_def
    >>> from datetime import datetime
    >>> time_slot = datetime(2009, 10, 8, 14, 30)
    >>> global_data = GeostationaryFactory.create_scene("Meteosat-9", "", "seviri", time_slot)
    >>> europe = get_area_def("EuropeCanary")
    >>> global_data.load([0.6, 0.8, 10.8], area_extent=europe.area_extent)
    >>> img = global_data.image.overview()
    >>> img.show()

.. image:: images/myoverview.png

Necessary configuration settings
--------------------------------

For this tutorial template config files (see :doc:`install`) can be used. These
are located in the *etc* dir of the mpop_ source. Copy *mpop.cfg.template*,
*areas.def.template* and *Meteosat-9.cfg.template* to another dir and remove
the *.template* extension. In the config file *Meteosat-9.cfg* locate the
section :attr:`severi-level1` and modify the defined :attr:`dir` to point to
the dir of your uncompressed HRIT data.

Set PPP_CONFIG_DIR to the directory containing your modified mpop_ config files.

.. _mpop: http://www.github.com/mraspaud/mpop
