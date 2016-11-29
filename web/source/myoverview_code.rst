Making SEVIRI RGB Overview composite
=====================================

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
