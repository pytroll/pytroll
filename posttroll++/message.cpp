/*
 * Copyright (c) 2012.

 * Author(s): 
 *   Martin Raspaud <martin.raspaud@smhi.se>

 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program. If not, see <http://www.gnu.org/licenses/>.
 */

#include <stdio.h>
#include <unistd.h>
#include <sys/types.h>
#include <pwd.h>
#include <time.h>
#include <sys/time.h> 
#include <iostream>
#include "message.h"

Message::Message(const char* sub, 
                 const char* typ,
                 const char* dat,
                 bool bin) {
  subject = sub;
  type = typ;
  data = dat;
  binary = bin;
  
  /* sender */

  char hostname[1024];
  hostname[1023] = '\0';
  gethostname(hostname, 1023);
  
  struct passwd *pw = getpwuid(getuid());
  
  sender = pw->pw_name;
  sender += "@";
  sender += hostname;

  /* protocol version */

  version = _VERSION;


  /* utc time in isoformat */


  struct timeval tv; 
  struct tm* ptm; 
  char time_string[32]; 
  char microseconds[7];

  /* Obtain the time of day, and convert it to a tm struct. */ 
  gettimeofday (&tv, NULL); 
  ptm = gmtime (&tv.tv_sec); 

  /* Format the date and time, down to a single second. */ 
  strftime(time_string, sizeof(time_string), "%Y-%m-%dT%H:%M:%S", ptm); 

  sprintf(microseconds, "%06ld", tv.tv_usec);
  
  time = time_string;
  time += ".";
  time += microseconds;

}

string
Message::toString() {
  string msg(_MAGICK);
  msg += subject;
  msg += " ";
  msg += type;
  msg += " ";
  msg += sender;
  msg += " ";
  msg += time;
  msg += " ";
  msg += version;
  msg += " ";

  if(binary) {
    msg += "binary/octet-stream";
  } else {
    msg += "text/ascii";
  }
  msg += " ";
  msg += data;

  return msg;
}

