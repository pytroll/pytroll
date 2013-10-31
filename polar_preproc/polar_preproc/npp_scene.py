from polar_preproc.segment import Segment

class NPPScene(Segment):

    description = "List of overlapping granules"

    def __init__(self, platform='npp', start_time=None, **kwargs):
        super(NPPScene, self).__init__(platform=platform,
                                       start_time=start_time,
                                       **kwargs)

    def append(self, filename):
        stamp = get_npp_stamp(filename)
        super(NPPScene, self).append(str(stamp), stamp.start_time,
                                     stamp.end_time, stamp.orbit)
