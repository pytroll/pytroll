# -*-python-*- 
#
"""A Message goes like: 
<subject> <type> <timestamp> <sender> [data]

Message('pytroll:/DC/juhu', 'info', 'jhuuuu !!!')
will be encoded as (at the right time and by the right user at the right host):
pytroll:/DC/juhu info 2010-12-01T12:21:11 henry@prodsat jhuuuu !!!
"""
import re
from datetime import datetime

class MessageError(Exception):
    pass

#-----------------------------------------------------------------------------
#
# Utillities.
#
#-----------------------------------------------------------------------------
def is_valid_subject(s):
    """Currently we only check for empty stings
    """
    return isinstance(s, str) and bool(s)

def is_valid_type(s):
    """Currently we only check for empty stings
    """
    return isinstance(s, str) and bool(s)

def is_valid_sender(s):
    """Currently we only check for empty stings
    """
    return isinstance(s, str) and bool(s)

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

  def __init__(self, subject='', atype='', data='', empty=False):
      """A Message needs at least a subject and a type ... if not specified as empty.
      """
      if not empty:
          self.subject = subject
          self.type = atype
          self.time = datetime.utcnow()
          self.sender = _getsender()
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

  @staticmethod
  def decode(rawstr):
      m = Message(empty=True)
      m.__dict__ = _decode(rawstr)
      m._validate()
      return m

  def encode(self):
      self._validate()
      rawstr = "%s %s %s %s"%(self.subject, self.type, self.time.isoformat(), self.sender)
      return rawstr + ' ' + self.data

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
# Small internal helpers.
#
#-----------------------------------------------------------------------------
def _decode(rawstr):
    a = re.split(r"\s+", rawstr, maxsplit=4)
    if len(a) < 4:
        raise MessageError, "Could node decode raw string: '%s ...'"%str(rawstr[:36])
    d = dict((('subject', a[0].strip()),
              ('type', a[1].strip()),
              ('time', _strptime(a[2].strip())),
              ('sender', a[3].strip())))
    try:
        d['data'] = a[4]
    except IndexError:
        d['data'] = ''
    return d

def _strptime(str):
    _isoformat = "%Y-%m-%dT%H:%M:%S.%f"
    return datetime.strptime(str, _isoformat)

def _getsender():
    import getpass
    import socket
    host = socket.gethostname()
    user = getpass.getuser()
    return "%s@%s"%(user, host)

if __name__ == '__main__':
    import pickle
    import os

    m1 = Message('/test/whatup/doc', 'info', data='not much to say')
    sender = '%s@%s'%(m1.user, m1.host)
    print sender
    if sender != m1.sender:
        print 'OOPS ... deconding sender failed'
    m2 = Message.decode(m1.encode())
    print m2
    if str(m2) != str(m1):
        print 'OOPS ... decoding/encoding message failed'  
    rawstr = "/test/what/todo info 2008-04-11T22:13:22.123000 ras@hawaii what's up doc"
    m = Message.decode(rawstr)
    print m
    if str(m) != rawstr:
        print 'OOPS ... decoding/encoding message failed'  
