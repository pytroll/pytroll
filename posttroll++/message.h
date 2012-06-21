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

#ifndef __message_h__
#define __message_h__

#include <string>

#define _MAGICK  "pytroll:/"
#define _VERSION "v1.01"

using namespace std;

class Message {
  string subject;
  string type;
  string sender;
  string time;
  string data;
  string version;
  bool binary;
public:
  Message(const char*, const char*, const char*, bool);
  string toString();
};

#endif
