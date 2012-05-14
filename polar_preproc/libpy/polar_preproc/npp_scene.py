from polar_preproc.segment import Segment

class NPPScene(Segment):

    description = "List of overlapping granules"

    def __init__(self, satellite_name='npp', start_time=None, **kwargs):
        super(NPPScene, self).__init__(satellite_name=satellite_name,
                                       start_time=start_time,
                                       **kwargs)

    def append(self, filename):
        stamp = get_npp_stamp(filename)
        super(NPPScene, self).append(str(stamp), stamp.start_time,
                                     stamp.end_time, stamp.orbit)
