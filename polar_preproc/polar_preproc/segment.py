#
# A general segment.
#
import os
import re
from datetime import datetime
import json

from polar_preproc import NPPStamp

_RE_TIME_ISOFORMATS = [(re.compile(
            '^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$'),
                        "%Y-%m-%dT%H:%M:%S"),
                       (re.compile(
            '^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+$'),
                        "%Y-%m-%dT%H:%M:%S.%f")]

class Segment(object):
    description = None
    use_stamp_in_list = True

    def __init__(self, platform=None, start_time=None, end_time=None, orbit_number=None,
                 create_time=None, site=None, domain=None, name=None,
                 description=None, items=[]):
        self.platform = platform
        self.start_time = start_time
        self.end_time = end_time
        self.orbit_number = orbit_number
        self.create_time = create_time or datetime.now()
        self.site = site or SITE
        self.domain = domain or DOMAIN
        self.name = name
        self.description = description or self.description # convert to an attribute
        self._attrs = self.__dict__.keys()
        self.items = items

    def append(self, item, start_time=None, end_time=None, orbit_number=None):
        if item in self.items:
            return
        if len(self.items) == 0:
            self.start_time = start_time or item.start_time
            self.orbit_number = orbit_number or item.orbit_number
        self.end_time = end_time or item.end_time         
        self.items.append(item)

    def extend(self, items, start_time=None, end_time=None, orbit_number=None):
        for i in items:
            self.append(i, start_time, end_time, orbit_number)

    @property
    def stamp(self):
        self._check()
        return str(NPPStamp(self.platform, self.start_time, self.end_time,
                            self.orbit_number))

    def dump(self, filename):
        self._check()
        json_dump(self, filename)

    def __str__(self):
        self._check()
        return json_dumps(self)

    def is_valid(self):
        return bool(self.platform and self.start_time and
                    self.end_time and self.orbit_number)

    def _check(self):
        if not self.is_valid():
            raise TypeError("Not a valid segmet, missing attributes.")

def json_dumps(seg):
    nfo = {}
    for k in seg._attrs:
        v = getattr(seg, k)
        if v != None:
            if isinstance(v, datetime):
                nfo[k] = v.isoformat()
            else:
                nfo[k] = v
    items = []
    for i in seg.items:
        if seg.use_stamp_in_list:
            try:
                i = i.stamp
            except AttributeError:
                pass
        items.append(i)
    return json.dumps((nfo, items),
                      sort_keys=True, indent=4)

def json_dump(seg, filename):
    with open(filename, 'w') as fp:
        fp.write(json_dumps(seg) + '\n')
     
def json_loads(blob):
    nfo, items = json.loads(blob)
    for key, val in nfo.items():
        for fmt in _RE_TIME_ISOFORMATS:
            if fmt[0].match(str(val)):
                nfo[key] = datetime.strptime(val, fmt[1])
    nfo['items'] = items
    return Segment(**nfo)

def json_load(filename):
    with open(filename) as fp:
        return json_loads(fp.read())

if __name__ == '__main__':
    import sys
    s = json_load(sys.argv[1])
    print s
    json_dump(s, "xxx.json")
