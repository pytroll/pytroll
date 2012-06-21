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
#include <iostream>
#include <sstream>
#include "publisher.h"

Publisher::Publisher(const char* hostname, int port) {
  context = new zmq::context_t(1);
  publisher = new zmq::socket_t(*context, ZMQ_PUB);

  string address("tcp://");
  address += hostname;
  address += ":";

  stringstream out;
  out << port;
  address += out.str();

  publisher->bind(address.c_str());
}

void
Publisher::send(const char* msg) {
  zmq::message_t zmessage(strlen(msg));
  memcpy ((void *) zmessage.data(), msg, strlen(msg));
  publisher->send(zmessage);
}

void
Publisher::send(Message msg) {
  send(msg.toString().c_str());
}

// int main() {
//   Publisher pub("*", 9332);
//   /* wait a little to get the publisher started... */
//   usleep(500 * 1000);

//   Message msg("/DC/juhu", "info", "jhuuuu !!!", false);

//   cout << "publishing " << msg.toString() << endl;
//   pub.send(msg);

//   return 1;
// }
