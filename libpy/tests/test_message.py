import os
import sys
import unittest

sys.path = [os.path.abspath(os.path.dirname(__file__) + '/..'),] + sys.path
from message import Message

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
        rawstr = "/test/1/2/3 info 2008-04-11T22:13:22.123000 ras@hawaii v1.0 what's up doc"
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
            self.assertTrue(str(m1) == str(m2), msg='Messaging, decoding of msec failed')
        finally:
            try:
                os.remove('pickle.message')
            except OSError:
                pass

if __name__ == '__main__':
    import nose
    sys.argv.append('-s') # when run individually, don't capture stdout
    nose.main()
