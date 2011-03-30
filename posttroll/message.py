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
import json

_magick = 'pytroll:/'

class MessageError(Exception):
    pass

#-----------------------------------------------------------------------------
#
# Utillities.
#
#-----------------------------------------------------------------------------
def is_valid_subject(s):
    """Currently we only check for empty strings.
    """
    return isinstance(s, str) and bool(s)

def is_valid_type(s):
    """Currently we only check for empty strings.
    """
    return isinstance(s, str) and bool(s)

def is_valid_sender(s):
    """Currently we only check for empty strings.
    """
    return isinstance(s, str) and bool(s)

def is_valid_data(s):
    """Check if data is JSON serializable.
    """
    if s:
        try:
            tmp = json.dumps(s)
            del tmp
        except TypeError:
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
    - It will make a Message pickleable."""

    _version = 'v1.01'

    def __init__(self, subject='', atype='', data='', empty=False):
        """A Message needs at least a subject and a type ... if not specified as empty.
        """
        if not empty:
            self.subject = subject
            self.type = atype
            self.sender = _getsender()
            self.time = datetime.utcnow()
            self.data = data
            self._validate()

    @property
    def user(self):
        try:
            return self.sender[:self.sender.index('@')]
        except ValueError:
            return ''
      
    @property
    def host(self):
        try:
            return self.sender[self.sender.index('@')+1:]
        except ValueError:
            return ''

    @property
    def head(self):
        self._validate()
        return _encode(self, head=True)

    @property
    def version(self):
        return self._version

    @staticmethod
    def decode(rawstr):
        m = Message(empty=True)
        m.__dict__ = _decode(rawstr)
        m._validate()
        return m
    
    def encode(self):
        self._validate()
        return _encode(self)

    def __repr__(self):
        return self.encode()

    def __str__(self):
        return self.encode()

    def _validate(self):
        if not is_valid_subject(self.subject):
            raise MessageError, "Invalid subject: '%s'"%self.subject
        if not is_valid_subject(self.type):
            raise MessageError, "Invalid type: '%s'"%self.type
        if not is_valid_subject(self.sender):
            raise MessageError, "Invalid sender: '%s'"%self.sender
        if not is_valid_data(self.data):
            raise MessageError, "Invalid data: data is not JSON serializable"
        
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
    return version == Message._version

def _decode(rawstr):
    # Check for the magick word.
    if not rawstr.startswith(_magick):
        raise MessageError, "This is not a '%s' message (wrong magick word)"%_magick
    rawstr = rawstr[len(_magick):]

    # Check for element count and version
    a = re.split(r"\s+", rawstr, maxsplit=6)
    if len(a) < 5:
        raise MessageError, "Could node decode raw string: '%s ...'"%str(rawstr[:36])
    version = a[4][:len(Message._version)]
    if not _is_valid_version(version):
        raise MessageError, "Invalid Message version: '%s'"%str(version)

    # Start to build message
    d = dict((('subject', a[0].strip()),
              ('type', a[1].strip()),
              ('sender', a[2].strip()),
              ('time', _strptime(a[3].strip()))))

    # Data part
    try:
        mimetype = a[5].lower()
        data = a[6]
    except IndexError:
        mimetype = None

    if mimetype == None:
        d['data'] = ''
    elif mimetype == 'application/json':
        try:
            d['data'] = json.loads(a[6])
        except ValueError:
            del d
            raise MessageError, "JSON decode failed on '%s ...'"%a[6][:36]
    elif mimetype == 'text/ascii':
        d['data'] = str(data)
    else:
        raise MessageError, "Unknown mime-type '%s'"%mimetype

    return d

def _encode(m, head=False):
    rawstr = _magick + \
             "%s %s %s %s %s"%(m.subject, m.type, m.sender, m.time.isoformat(), m.version)
    if not head and m.data:
        return rawstr + ' ' + 'application/json' + ' ' + json.dumps(m.data)
    return rawstr

#-----------------------------------------------------------------------------
#
# Small internal helpers.
#
#-----------------------------------------------------------------------------
def _strptime(strg):
    _isoformat = "%Y-%m-%dT%H:%M:%S.%f"
    return datetime.strptime(strg, _isoformat)

def _getsender():
    import getpass
    import socket
    host = socket.gethostname()
    user = getpass.getuser()
    return "%s@%s" % (user, host)

#-----------------------------------------------------------------------------
if __name__ == '__main__':
    MSG = Message('/test/1/2/3/nodata', 'heartbeat')
    print MSG

    MSG1 = Message('/test/whatup/doc', 'info', data='not much to say')
    SENDER = '%s@%s' % (MSG1.user, MSG1.host)
    print SENDER
    if SENDER != MSG1.sender:
        print 'OOPS 1 ... deconding SENDER failed'
    MSG2 = Message.decode(MSG1.encode())
    print MSG2
    if str(MSG2) != str(MSG1):
        print 'OOPS 2 ... decoding/encoding message failed'  

    RAWSTR = _magick + \
        '/test/what/todo info ras@hawaii 2008-04-11T22:13:22.123456 v1.0 '+\
        'application/json "what\'s up doc"'
    MSG = Message.decode(RAWSTR)
    print MSG.head
    print MSG
    if str(MSG) != RAWSTR:
        print 'OOPS 3 ... decoding/encoding message failed'  
