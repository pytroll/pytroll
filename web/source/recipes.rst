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

    if sys.version_info < (2, 5):
        import time
        def strptime(string, fmt=None):
            """This function is available in the datetime module only
            from Python >= 2.5.
            """

            return datetime(*time.strptime(string, fmt)[:6])

    else:
        strptime = datetime.strptime

    if __name__ == '__main__':
        if len(sys.argv) < 2:
            print "Usage: " + sys.argv[0] + " time_string"
            sys.exit()

        time_string = sys.argv[1]
        time_slot = strptime(time_string, "%Y%m%d%H%M")
        global_data = GeostationaryFactory.create_scene("meteosat", "09",
                                                        "seviri", time_slot)

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

    if sys.version_info < (2, 5):
        import time
        def strptime(string, fmt=None):
            """This function is available in the datetime module only
            from Python >= 2.5.
            """

            return datetime(*time.strptime(string, fmt)[:6])

    else:
        strptime = datetime.strptime

    if __name__ == '__main__':
        if len(sys.argv) < 3:
            print "Usage: " + sys.argv[0] + " time_string orbit"
            sys.exit()

        time_string = sys.argv[1]
        orbit = sys.argv[2] 
        time_slot = strptime(time_string, "%Y%m%d%H%M")
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

We take the case of level 1b data (calibrated and geolocalized) from metop A,
as received through the global data service of Eumetsat.

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
   dir=/data/prod/satellit/gds/avhrr
   filename=AVHR_xxx_1B_M02_%Y%m%d%H%M*


- Here is a minimal script that monitors a directory and builds composites:

  .. code-block:: python

    import sys
    from datetime import timedelta, datetime
    import glob
    import os
    import time

    from mpop.saturn.gatherer import Granule, Gatherer


    def get_files_newer_than(directory, time_stamp):
        """Get the list of files from the *directory* which are newer than a given
     *time_stamp*.
        """
        filelist = glob.glob(os.path.join(directory, "*"))
        return [filename for filename in filelist
                if datetime.fromtimestamp(os.stat(filename)[8]) > time_stamp]


    if __name__ == '__main__':
        if len(sys.argv) < 3:
            print "Usage: " + sys.argv[0] + " directory wait_for_more"
            sys.exit()

        directory = sys.argv[1]
        # if we wait for files in the directory forever or not
        wait_for_more = eval(sys.argv[2])

        areas = ["euro4", "scan2"]

        gatherer = None

        time_stamp = datetime(1970, 1, 1)

        while True:

            # Scanning directory

            new_time_stamp = datetime.now()
            filenames = get_files_newer_than(directory, time_stamp)
            time_stamp = new_time_stamp

            # Adding files to the gatherer

            for filename in filenames:
                granule = Granule(filename)
                if gatherer is None:
                    gatherer = Gatherer(areas_of_interest=areas,
                                        timeliness=timedelta(minutes=150),
                                        satname=granule.satname,
                                        number=granule.number,
                                        variant=granule.variant)
                gatherer.add(granule)

            # Build finished swath and process them.

            for swath in gatherer.finished_swaths:
                global_data = swath.concatenate()

                local_data = global_data.project(swath.area)

                time_string = global_data.time_slot.strftime("%Y%m%d%H%M")

                area_id = swath.area.area_id

                img = local_data.image.overview()
                img.save("overview_" + area_id + "_" + time_string + ".png")

                img = local_data.image.natural()
                img.save("natural_" + area_id + "_" + time_string + ".png")

            if not wait_for_more:
                break

            # wait 60 seconds before restarting
            time.sleep(60)

