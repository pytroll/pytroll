# -*-python-*- 
#
"""A Message, goes like: 
<subject> <type> <timestamp> <sender> [data]

fx: pytroll:/DC/address info 2010-12-01T12:21:11 juhu@prodsat prodsat:22010
"""
from datetime import datetime

def _strptime(str):
    _isoformat = "%Y-%m-%dT%H:%M:%S.%f"
    return datetime.strptime(str, _isoformat)

def _getsender():
    import getpass
    import socket
    host = socket.gethostname()
    user = getpass.getuser()
    sender = "%s@%s"%(user, host)
    return sender, user, host

class Message:

  """Wrap a smsg dictonary into a Message class.

  - Has to be initialized with a 'subject', 'type' and optionally 'data'.
  - It will forbid rebinding of message specific attributes.
  - It will add a few extra attributes.
  - It will make a Message pickleable."""

  def __init__(self, subject, atype, data=''):
      """A Message needs at least a subject and type or a raw string
      """
      self.subject = subject
      self.type = atype
      self.time = datetime.utcnow()
      a = _getsender()
      self.sender = a[0]
      if len(a) > 2:
          self.user = a[1]
          self.host = a[2]
      self.data = data

  @staticmethod
  def decode(rawstr):
      a = rawstr.split(' ', 4)
      try:
          data = a[4]
      except IndexError:
          data = ''
      m = Message(a[0].strip(), a[1].strip(), data)
      m.time = _strptime(a[2].strip())
      m.sender = a[3].strip()
      # try to extract a user and a host
      hu = a[3].split('@', 1)
      if len(hu) > 1:
          m.user = hu[0]
          m.host = hu[1]
      return m

  def encode(self):
      text = "%s %s %s %s"%(self.subject, self.type, self.time.isoformat(), self.sender)
      return text + ' ' + self.data

  def __repr__(self):
      return self.encode()

  def __str__(self):
      return self.encode()

  #
  # Make it pickleable.
  #
  def __getstate__(self):
      return self.encode()

  def __setstate__(self, state):
      self.__dict__.clear()
      self.__dict__ = Message.decode(state).__dict__

def is_valid_subject(subj):
    return True

def is_valid_type(type):
    return True

if __name__ == '__main__':
    m1 = Message('/test/whatup/doc', 'info', data='not much to say')
    print m1
    m2 = Message.decode(m1.encode())
    if str(m1) != str(m2):
        print 'UUUPS'
  
    rawstr = "/test/what/todo info 2008-04-11T22:13:22.123 ras@hawaii what's up doc"
    m = Message.decode(rawstr)
    print m
