#!/usr/bin/env python
#
# Copyright (c) 2010-2012.

# Author(s):
 
#   Lars O. Rasmussen <ras@dmi.dk>
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

"""A Message goes like: 
<subject> <type> <sender> <timestamp> <version> [mime-type data]

Message('/DC/juhu', 'info', 'jhuuuu !!!')
will be encoded as (at the right time and by the right user at the right host):
pytroll://DC/juhu info henry@prodsat 2010-12-01T12:21:11.123456 v1.0 \
application/json "jhuuuu !!!"

Note: It's not optimized for BIG messages.
"""
import re
from datetime import datetime
try:
    import json
except ImportError:
    import simplejson as json

from posttroll import strp_isoformat

_MAGICK = 'pytroll:/'
_VERSION = 'v1.01'

class MessageError(Exception):
    """This modules exceptions.
    """
    pass

#-----------------------------------------------------------------------------
#
# Utillities.
#
#-----------------------------------------------------------------------------
def is_valid_subject(obj):
    """Currently we only check for empty strings.
    """
    return isinstance(obj, str) and bool(obj)

def is_valid_type(obj):
    """Currently we only check for empty strings.
    """
    return isinstance(obj, str) and bool(obj)

def is_valid_sender(obj):
    """Currently we only check for empty strings.
    """
    return isinstance(obj, str) and bool(obj)

def is_valid_data(obj):
    """Check if data is JSON serializable.
    """
    if obj:
        try:
            tmp = json.dumps(obj)
            del tmp
        except (TypeError, UnicodeDecodeError):
            return False
    return True

#-----------------------------------------------------------------------------
#
# Message class.
#
#-----------------------------------------------------------------------------
class Message:
    """A Message.

    - Has to be initialized with a 'subject', 'type' and optionally 'data'.
    - It will add add few extra attributes.
    - It will make a Message pickleable.
    """

    def __init__(self, subject='', atype='', data='', rawstr=None):
        """Initialize a Message from a subject, type and data ... 
        or from a raw string.
        """
        if rawstr:
            self.__dict__ = _decode(rawstr)
        else:
            self.subject = subject
            self.type = atype
            self.sender = _getsender()
            self.time = datetime.utcnow()
            self.data = data
        self.version = _VERSION
        self._validate()

    @property
    def user(self):
        """Try to return a user from a sender.
        """
        try:
            return self.sender[:self.sender.index('@')]
        except ValueError:
            return ''
      
    @property
    def host(self):
        """Try to return a host from a sender.
        """
        try:
            return self.sender[self.sender.index('@')+1:]
        except ValueError:
            return ''

    @property
    def head(self):
        """Return header of a message (a message without the data part).
        """
        self._validate()
        return _encode(self, head=True)

    @staticmethod
    def decode(rawstr):
        """Decode a raw string into a Message.
        """
        return Message(rawstr=rawstr)
    
    def encode(self):
        """Encode a Message to a raw string.
        """
        self._validate()
        return _encode(self, raw=self.raw)

    def __repr__(self):
        return self.encode()

    def __str__(self):
        return self.encode()

    def _validate(self):
        """Validate a messages attributes.
        """
        if not is_valid_subject(self.subject):
            raise MessageError, "Invalid subject: '%s'" % self.subject
        if not is_valid_subject(self.type):
            raise MessageError, "Invalid type: '%s'" % self.type
        if not is_valid_subject(self.sender):
            raise MessageError, "Invalid sender: '%s'" % self.sender
        if not is_valid_data(self.data):
            self.raw = True
        else:
            self.raw = False
            #raise MessageError, "Invalid data: data is not JSON serializable"
        
    #
    # Make it pickleable.
    #
    def __getstate__(self):
        return self.encode()

    def __setstate__(self, state):
        self.__dict__.clear()
        self.__dict__ = _decode(state)

#-----------------------------------------------------------------------------
#
# Decode / encode
#
#-----------------------------------------------------------------------------
def _is_valid_version(version):
    """Check version.
    """
    return version == _VERSION

def _decode(rawstr):
    """Convert a raw string to a Message.
    """
    # Check for the magick word.
    if not rawstr.startswith(_MAGICK):
        raise MessageError, "This is not a '%s' message (wrong magick word)"\
            % _MAGICK
    rawstr = rawstr[len(_MAGICK):]

    # Check for element count and version
    raw = re.split(r"\s+", rawstr, maxsplit=6)
    if len(raw) < 5:
        raise MessageError, "Could node decode raw string: '%s ...'"\
            % str(rawstr[:36])
    version = raw[4][:len(_VERSION)]
    if not _is_valid_version(version):
        raise MessageError, "Invalid Message version: '%s'" % str(version)

    # Start to build message
    msg = dict((('subject', raw[0].strip()),
                ('type', raw[1].strip()),
                ('sender', raw[2].strip()),
                ('time', strp_isoformat(raw[3].strip())),
                ('version', version)))

    # Data part
    try:
        mimetype = raw[5].lower()
        data = raw[6]
    except IndexError:
        mimetype = None

    if mimetype == None:
        msg['data'] = ''
    elif mimetype == 'application/json':
        try:
            msg['data'] = json.loads(raw[6])
        except ValueError:
            del msg
            raise MessageError, "JSON decode failed on '%s ...'" % raw[6][:36]
    elif mimetype == 'text/ascii':
        msg['data'] = str(data)
    else:
        raise MessageError, "Unknown mime-type '%s'" % mimetype

    return msg

def _encode(msg, head=False, raw=False):
    """Convert a Message to a raw string.
    """
    rawstr = _MAGICK + "%s %s %s %s %s" % \
             (msg.subject, msg.type, msg.sender,
              msg.time.isoformat(), msg.version)
    if not head and msg.data and not raw:
        return rawstr + ' ' + 'application/json' + ' ' + json.dumps(msg.data)
    if not head and msg.data and raw:
        return rawstr + ' ' + 'text/ascii' + ' ' + msg.data
    return rawstr

#-----------------------------------------------------------------------------
#
# Small internal helpers.
#
#-----------------------------------------------------------------------------
def _getsender():
    """Return local sender.
    Don't use the getpass module, it looks at various environment variables
    and is unreliable.
    """
    import os
    import pwd
    import socket
    host = socket.gethostname()
    user = pwd.getpwuid(os.getuid())[0]
    return "%s@%s" % (user, host)

#-----------------------------------------------------------------------------
if __name__ == '__main__':
    msg_ = Message('/test/1/2/3/nodata', 'heartbeat')
    print msg_

    msg1_ = Message('/test/whatup/doc', 'info', data='not much to say')
    sender_ = '%s@%s' % (msg1_.user, msg1_.host)
    print sender_
    if sender_ != msg1_.sender:
        print 'OOPS 1 ... deconding sender failed'
    msg2_ = Message.decode(msg1_.encode())
    print msg2_
    if str(msg2_) != str(msg1_):
        print 'OOPS 2 ... decoding/encoding message failed'  

    raws = _MAGICK + \
        '/test/what/todo info ras@hawaii 2008-04-11T22:13:22.123456 ' + \
        _VERSION + ' application/json "what\'s up doc"'
    msg_ = Message.decode(raws)
    print msg_.head
    print msg_
    if str(msg_) != raws:
        print 'OOPS 3 ... decoding/encoding message failed'  
