
Some words on geolocation
=========================

Before we continue projecting the data to a map projection, just some words on
geolocation. For both the M- and the I-bands there are normally two geolocation
files available. The ones using a terrain correction are prefixed *GMTCO* for
the M-bands and *GITCO* for the I-bands. Correspondingly there are two
geolocation files where the topography has been neglected, and these are
prefixed *GMODO* and *GIMGO*. For the Day-Night band there shall be only one
geolocation file, prefixed *GDNBO*. In the configuration file you have some
flexibility to constrain what type of geolocation to apply (terrain corrected
or the non-corrected geoid files). However, normally it would be sufficient to
allow all kinds of geolocations and let the viirs reader in *mpop* choose the
appropriate one for you:

.. code-block:: ini

    [viirs-level2]
    geo_filenames = G????_%(satellite)s_d%Y%m%d_t%H%M???_e???????_b%(orbit)s_c*_cspp_dev.h5
    filename = SV???_%(satellite)s_d%Y%m%d_t%H%M???_e???????_b%(orbit)s_c*_cspp_dev.h5
    dir = /data/viirs/sdr
    format = viirs_sdr.ViirsSDRReader

If the list of geo-files is not specified in the config file or some of them do
not exist, the viirs reader will rely on what is written in the band-data
metadata header. For each band the SDR files contain an attribute giving the
name of the matching geolocation file. The reader will assume that this gile is
lying in the same directory as the band data given by the path *dir* above. If
this file is not there no geolocation will be loaded.

With the above configuration, the viirs reader will search first for the
terrain corrected files matching the string above. If the terrain corrected
files are not available, the reader will try the geoid ones. If no geoid files
matching the string above are found the reader will not load any
geolocation. Without geolocation the data cannot be projected to a
map-projetion, of course.
