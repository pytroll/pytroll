================
 Test procedure
================

Needs pyinotify


Edit the sattorrent_dmi.cfg file to fit the current settings.

create the hrpt directory in /tmp directory::
  
  mkdir /tmp/hrpt

start the data writer::

  python test_write 20120704120000 &

start the server::

  python trollcast/server.py sattorrent_dmi.cfg &

start the client::

  python test_client.py sattorrent_dmi.cfg &

Now relax and enjoy :)

Martin
