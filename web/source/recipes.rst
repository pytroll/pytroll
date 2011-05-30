==============================
 Recipes: Operational Pytroll
==============================

Geostationary (Eumetcast) production
====================================

We take the case of HRIT data from meteosat 9, as send through eumetcast.

- Install mipp, mpop, and pyresample
- Don't forget to set up the PPP_CONFIG_DIR variable to point to your
  configuration files.
- Edit the meteosat09.cfg configuration file (a template is provided in case
  you don't have one) with your HRIT directory:

  .. code-block:: ini

   [seviri-level1]
   format = 'xrit/MSG'
   dir='/data/hrit_in'
   filename='H-000-MSG?__-MSG?________-%(channel)s-%(segment)s-%Y%m%d%H%M-__'
   filename_pro='H-000-MSG?__-MSG?________-_________-%(segment)s-%Y%m%d%H%M-__'
   filename_epi='H-000-MSG?__-MSG?________-_________-%(segment)s-%Y%m%d%H%M-__'

  where `/data/hrit_in` has to be changed to anything that suits your
  environment.

- Here is an example of a minimal script that has to be called as soon as an
  MSG slot has arrived (usually, watching the arrival of the epilogue file
  suffices):

  .. code-block:: python

    from mpop.satellites import GeostationaryFactory

    import sys
    from datetime import datetime

    if __name__ == '__main__':
        time_string = sys.argv[1]
        time_slot = datetime.strptime(time_string, "%Y%m%d%H%M")
        global_data = GeostationaryFactory.create_scene("meteosat", "09", "seviri", time_slot)

        global_data.load()

        areas = ["euro4", "scan2"]

        for area in areas:

            local_data = global_data.project(area)

            img = local_data.image.overview()
            img.save("overview_" + area + "_" + time_string + ".png")

            img = local_data.image.fog()
            img.save("fog_" + area + "_" + time_string + ".png")


Polar (hrpt) production
=======================

We take the case of level 1b data (calibrated and geolocalized) from noaa 19,
as output from AAPP.

- Install mpop and pyresample
- Don't forget to set up the PPP_CONFIG_DIR variable to point to your
  configuration files.
- Edit the noaa19.cfg configuration file (a template is provided in case
  you don't have one) with your data directory:

  .. code-block:: ini
  
   [avhrr-level2]
   filename = hrpt_%(satellite)s_%Y%m%d_%H%M_%(orbit)s.l1b
   dir = /data/polar/
   format = aapp1b

- Here is an example of a minimal script that has to be called as soon as a new
  swath has arrived:

  .. code-block:: python

    from mpop.satellites import PolarFactory

    import sys
    from datetime import datetime

    if __name__ == '__main__':
        if len(sys.argv) < 3:
            print "Usage: " + sys.argv[0] + " time_string orbit"
        time_string = sys.argv[1]
        orbit = sys.argv[2] 
        time_slot = datetime.strptime(time_string, "%Y%m%d%H%M")
        global_data = PolarFactory.create_scene("noaa", "19",
                                                "avhrr", time_slot, orbit)

        global_data.load()

        areas = ["euro4", "scan2"]

        for area in areas:

            local_data = global_data.project(area)

            img = local_data.image.overview()
            img.save("overview_" + area + "_" + time_string + ".png")

            img = local_data.image.cloudtop()
            img.save("cloudtop_" + area + "_" + time_string + ".png")



Segmented data (Eumetcast) production
=====================================

We take the case of level 1b data (calibrated and geolocalized) from noaa 19,
as output from AAPP.

- Install mpop and pyresample
- Don't forget to set up the PPP_CONFIG_DIR variable to point to your
  configuration files.
- Edit the gdsmetop02.cfg configuration file (a template is provided in case
  you don't have one) with your data directory:
  
  .. code-block:: ini
  
   [avhrr-granules]
   type=eps_avhrr
   granularity=60
   full_scan_period=0.1667
   scan_width=2048
   dir=/data/prod/satellit/ears/avhrr
   filename=AVHR_xxx_1B_M02_%Y%m%d%H%M*


- Here is a minimal script that monitors a directory and builds composites:

  .. code-block:: python

    import sys
    from datetime import timedelta, datetime

    from mpop.saturn.gatherer import Granule, Gatherer


    def get_files_newer_than(directory, time_stamp):
        """Get the list of files from the *directory* which are newer than a given
     *time_stamp*.
        """
        return []


    if __name__ == '__main__':

        directory = sys.argv[1]

        areas = ["euro4", "scan2"]

        gatherer = None

        time_stamp = datetime(1970, 1, 1)

        while True:
            new_time_stamp = datetime.now()
            filenames = get_files_newer_than(directory, time_stamp)
            time_stamp = new_time_stamp

            for filename in filenames:
                granule = Granule(filename)
                if gatherer is None:
                    gatherer = Gatherer(areas_of_interest=areas,
                                        timeliness=timedelta(minutes=150),
                                        satellite=granule.satname,
                                        number=granule.number,
                                        variant=granule.variant)
                gatherer.add(granule)

            for swath in gatherer.finished_swaths:
                global_data = swath.concatenate()

                local_data = global_data.project(swath.area)

                time_string = global_data.time_slot.strftime("%Y%m%d%H%M")

                img = local_data.image.overview()
                img.save("overview_" + swath.area + "_" + time_string + ".png")

                img = local_data.image.cloudtop()
                img.save("cloudtop_" + swath.area + "_" + time_string + ".png")

