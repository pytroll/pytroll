import os
import sys
import unittest

home = os.path.dirname(__file__) or '.'
sys.path = [os.path.abspath(home + '/../..'),] + sys.path

from pytroll.message import Message, _magick

datadir = home + '/data'
some_metadata = {'timestamp': '2010-12-03T16:28:39',
                 'satellite': 'metop2',
                 'uri': 'file://data/my/path/to/hrpt/files/myfile',
                 'orbit': 1222,
                 'format': 'hrpt',
                 'afloat': 1.2345}

class Test(unittest.TestCase):

    def test_decode(self):
        m1 = Message('/test/whatup/doc', 'info', data='not much to say')
        sender = '%s@%s'%(m1.user, m1.host)
        print sender
        self.assertTrue(sender == m1.sender, msg='Messaging, decoding user, host from sender failed')
        m2 = Message.decode(m1.encode())
        print m2
        self.assertTrue(str(m2) == str(m1), msg='Messaging, encoding, decoding failed')
        return 

    def test_msec(self):
        rawstr = _magick + \
            '/test/1/2/3 info ras@hawaii 2008-04-11T22:13:22.123000 v1.01 application/json "what\'s up doc"'
        m = Message.decode(rawstr)
        print m
        self.assertTrue(str(m) == rawstr, msg='Messaging, decoding of msec failed')

    def test_pickle(self):
        import pickle
        m1 = Message('/test/whatup/doc', 'info', data='not much to say')
        try:
            f = open("pickle.message", 'w')
            pickle.dump(m1, f)
            f.close()
            f = open("pickle.message")
            m2 = pickle.load(f)
            print m2
            f.close()
            self.assertTrue(str(m1) == str(m2), msg='Messaging, pickle failed')
        finally:
            try:
                os.remove('pickle.message')
            except OSError:
                pass

    def test_metadata(self):
        metadata = some_metadata
        m = Message.decode(Message('/sat/polar/smb/level1', 'file', data=metadata).encode())
        print m
        self.assertTrue(m.data == metadata, msg='Messaging, metadata decoding / encoding failed')
        
    def test_serialization(self):
        import json
        metadata = some_metadata
        fp = open(datadir + '/message_metadata.dumps')
        dump = fp.read()
        fp.close()
        # dumps differ ... maybe it's not a problem
        self.assertTrue(dump == json.dumps(metadata), msg='Messaging, JSON serialization has changed, dumps differ')
        m = json.loads(dump)
        self.assertTrue(m == metadata, msg='Messaging, JSON serialization has changed, python objects differ')

if __name__ == '__main__':
    import nose
    sys.argv.append('-s') # when run individually, don't capture stdout
    nose.main()
