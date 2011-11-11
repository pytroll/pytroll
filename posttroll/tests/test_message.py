#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2010-2011.

# Author(s):
 
#   Lars Ø. Rasmussen <ras@dmi.dk>
#   Martin Raspaud <martin.raspaud@smhi.se>

# This file is part of pytroll.

# Pytroll is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.

# Pytroll is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along with
# pytroll.  If not, see <http://www.gnu.org/licenses/>.

"""Test module for the message class.
"""

import os
import sys
import unittest

from posttroll.message import Message, _MAGICK


HOME = os.path.dirname(__file__) or '.'
sys.path = [os.path.abspath(HOME + '/../..'),] + sys.path


DATADIR = HOME + '/data'
SOME_METADATA = {'timestamp': '2010-12-03T16:28:39',
                 'satellite': 'metop2',
                 'uri': 'file://data/my/path/to/hrpt/files/myfile',
                 'orbit': 1222,
                 'format': 'hrpt',
                 'afloat': 1.2345}

class Test(unittest.TestCase):
    """Test class.
    """

    def test_encode_decode(self):
        """Test the encoding/decoding of the message class.
        """
        msg1 = Message('/test/whatup/doc', 'info', data='not much to say')
        #print msg1.__dict__
        sender = '%s@%s' % (msg1.user, msg1.host)
        self.assertTrue(sender == msg1.sender,
                        msg='Messaging, decoding user, host from sender failed')
        msg2 = Message.decode(msg1.encode())
        self.assertTrue(str(msg2) == str(msg1),
                        msg='Messaging, encoding, decoding failed')


    def test_decode(self):
        """Test the decoding of a message.
        """
        rawstr = (_MAGICK + 
                  '/test/1/2/3 info ras@hawaii 2008-04-11T22:13:22.123000 v1.01'
                  + ' application/json "what\'s up doc"')
        msg = Message.decode(rawstr)
        print msg
        self.assertTrue(str(msg) == rawstr,
                        msg='Messaging, decoding of msec failed')

    def test_encode(self):
        """Test the encoding of a message.
        """
        subject = '/test/whatup/doc'
        atype = "info"
        data = 'not much to say'
        msg1 = Message(subject, atype, data=data)
        sender = '%s@%s' % (msg1.user, msg1.host)
        self.assertEquals(_MAGICK +
                          subject + " " +
                          atype + " " +
                          sender + " " +
                          str(msg1.time.isoformat()) + " " +
                          msg1.version + " "
                          + 'application/json' + " " +
                          '"' + data + '"',
                          msg1.encode())

    def test_pickle(self):
        """Test pickling.
        """
        import pickle
        msg1 = Message('/test/whatup/doc', 'info', data='not much to say')
        try:
            fp_ = open("pickle.message", 'w')
            pickle.dump(msg1, fp_)
            fp_.close()
            fp_ = open("pickle.message")
            msg2 = pickle.load(fp_)
            print msg2
            fp_.close()
            self.assertTrue(str(msg1) == str(msg2),
                            msg='Messaging, pickle failed')
        finally:
            try:
                os.remove('pickle.message')
            except OSError:
                pass

    def test_metadata(self):
        """Test metadata encoding/decoding.
        """
        metadata = SOME_METADATA
        msg = Message.decode(Message('/sat/polar/smb/level1', 'file',
                                   data=metadata).encode())
        print msg
        self.assertTrue(msg.data == metadata,
                        msg='Messaging, metadata decoding / encoding failed')
        
    def test_serialization(self):
        """Test json serialization.
        """
        compare_file = '/message_metadata.dumps'
        try:
            import json
        except ImportError:
            import simplejson as json
            compare_file += '.simplejson'
        metadata = SOME_METADATA
        fp_ = open(DATADIR + compare_file)
        dump = fp_.read()
        fp_.close()
        # dumps differ ... maybe it's not a problem
        self.assertTrue(dump == json.dumps(metadata),
                        msg='Messaging, JSON serialization has changed,'
                        ' dumps differ')
        msg = json.loads(dump)
        self.assertTrue(msg == metadata,
                        msg='Messaging, JSON serialization'
                        ' has changed, python objects differ')

if __name__ == '__main__':
    unittest.main()
