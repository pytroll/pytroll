//{\footnotesize\begin{verbatim}
//////////////////////////////////////////////////////////////////////
// MessageClientDemo.cpp
//  
//////////////////////////////////////////////////////////////////////
//#define _UNIX_OS_
#ifndef _UNIX_OS_ 
#pragma warning (disable: 4786 4251 4275)
#endif

#include "mccapi/mccapi.h"
#include "posttroll++/message.h"
#include "posttroll++/publisher.h"
#include <iomanip>
#include <signal.h>
#include <zmq.hpp>

//////////////////////////////////////////////////////////////////////
// MessageServiceSample class
//////////////////////////////////////////////////////////////////////

/**
 * A simple application that uses a MCC MessageClient to receive messages 
 * from any connected MCC MessageServices
 *
 *  - It implements the MCC MessageListener the callback interface to receive message notifications
 *  - It uses a MCC MessageClient passed as an argument of the constructor to register the listener
 */
static volatile sig_atomic_t sig_caught = 0;

void handle_sighup(int signum)
{
  sig_caught = 1;
}

class MessageClientDemo : 
  public mcc::MessageListener, mcc::DataReceiver
{
public:

  MessageClientDemo(mcc::MessageClient* msg_client, 
                    mcc::DataClient* data_client) 
	:	m_DataClient(data_client) {
    m_DataClient->addDataReceiver(this);
    m_ReceivedChanges=false;
    
    msg_client->addMessageListener(this);
    m_PathLost=false;
    satellite = "None";
    risetime = "None";
    orbit_number = 0;
    // Zmq stuff
    //context = new zmq::context_t(1);
    //publisher = new zmq::socket_t(*context, ZMQ_PUB);
    //publisher->bind("tcp://*:9331");
    publisher = new Publisher("*", 9331);
    usleep(500 * 1000);
  }

	~MessageClientDemo() { 
	}


	// MessageListener Implementation

	/**
	 * Invoked when a new message is received.
	 *
	 * @param message  the message passed to the listener
	 */
	void newMessage(const mcc::Message& message) {


          std::string fildis("FILDIS");
          std::string stoprc("STOPRC");
          
          std::cout << message.toString() << std::endl;



          if(!message.getBody().compare(0, fildis.size(), fildis) ||
             !message.getBody().compare(0, stoprc.size(), stoprc))
            {
              std::cout << "Forwarding..." << std::endl;
              //zmq::message_t zmessage(message.toString().length() + 1);
              //sprintf ((char *) zmessage.data(), "%s\0", message.toString().c_str());
              //publisher->send(zmessage);
              Message msg("/oper/2met!", "2met!", message.toString().c_str(), false);
              publisher->send(msg);
            }

	}

	/**
	 * Invoked when a collection of new messages is received.
	 *
	 * @param messageList the received collection
	 */
	void newMessageList(const std::vector<mcc::Message>& messageList) {
		std::cout << "New Message List: " << messageList.size() << std::endl;
		
		if (!messageList.empty()) {
			std::vector<mcc::Message>::const_iterator msgIt = messageList.begin(); 
			for (; msgIt != messageList.end(); ++msgIt) {
				std::cout << "  + " << msgIt->toString() << std::endl;
			}
		}
	}

	/**
	 * Invoked when the source to the specified path is no longer available
	 *
	 * @param pathname the identifier of the data source
	 */
	void pathLost(const std::string& path) {
		// trace...
		std::cout << "Lost message source for path: "<< path << std::endl; 
        m_PathLost=true;
	}

    /**
     * Returns true if the path has been lost
     */
    bool pathLost()
    {
        return m_PathLost;
    }

  // Data client part

  /**
   * Invoked when monitoring data is received
   *
   * @param path  the pathname of the received node
   * @param tree  the node received
   * @param deep  true if the child nodes are affected
   */
  void dataChanged(const std::string& path, mcc::Node* tree, bool deep) {
    // TODO: use getChildNode
    mcc::Leaf* leaf=tree->getChildLeaf("LastSatellite");
    if(leaf !=NULL)
      satellite=leaf->getStringValue();
    leaf=tree->getChildLeaf("LastRisetime");
    if(leaf !=NULL)
      risetime=leaf->getStringValue();
    leaf=tree->getChildLeaf("LastRevNum");
    if(leaf !=NULL)
      orbit_number=leaf->getIntValue();

  }

  /**
   * Invoked when an upadte of the monitoring data tree is received
   *
   * @param path  the pathname of the received node
   * @param tree  the node received
   * @param deep  true if the child nodes are affected
   */
  void structureChanged(const std::string& path, mcc::Node* tree, bool deep) {
    m_ReceivedChanges=true;
    // trace...
    std::cout << "Received data structure for path: " << path << std::endl; 
  }
  

private:
  bool m_PathLost;
  bool m_ReceivedChanges;
  mcc::DataClient* m_DataClient;
  std::string satellite;
  std::string risetime;
  int orbit_number;
  //  zmq::context_t * context;
  //  zmq::socket_t * publisher;
  Publisher * publisher;
};

//////////////////////////////////////////////////////////////////////
// Main 
//////////////////////////////////////////////////////////////////////

/**
 * This sample program creates
 *   - a MCC Connection object (default is TCP Server at :12701)
 *   - a MCC MessageClient for the specified input path (default is 'mcc.message.sample')
 * It then opens the Connection allowing the MessageClient to receive messages
 * The program terminates when the source to the specified path is no longer available
 */
int main(int argC, char* argV[]) 
{
  signal(SIGINT, handle_sighup);
	try {
		// Default arguments 
		unsigned short port = 10500;
		std::string host = "172.22.8.16";
                //std::string host = "127.0.0.1";
                // getting only dispatch messages
                std::string path = "2met.data";

		// Parse command line arguments
		for (int index = 1; index < argC; ++index) {

			// server port option
			if (!strncmp(argV[index], "-p=", 3) 
				||  !strncmp(argV[index], "-P=", 3)) {
				const char* const parm = &argV[index][3];
				port = (unsigned short) atoi(parm);
			}

			// server address option
			else if (!strncmp(argV[index], "-h=", 3) 
				||  !strncmp(argV[index], "-H=", 3)) {
				const char* const parm = &argV[index][3];
				host = std::string(parm);
			}

			// user pathname option
			else if (!strncmp(argV[index], "-u=", 3) 
				||  !strncmp(argV[index], "-U=", 3)) {
				const char* const parm = &argV[index][3];
				path = std::string(parm);
			}

		}

		
		// Create the Connection object
		mcc::Connection* conn = (host == "") 
			? mcc::ConnectionFactory::createServerConnection("ServerConn", port)
			: mcc::ConnectionFactory::createClientConnection("ClientConn", host, port);


		// Create the MCC MessageClient Object
		MessageClientDemo demo(conn->createMessageClient(path, "MessageClientDemo"),
                                       conn->createDataClient(path, "DataClientDemo"));



		// Connect...
		conn->open();
                
                // Wait for SIGINT
                while (sig_caught == 0) {
                  vcs::waitMilliSec(5000);
		}
                
                std::cout << "Received interrupt. Exiting..." << std::endl;

		conn->close();

		// Free resources
		delete conn;
                std::cout << "Done. Bye !" << std::endl;

	
	}
	catch(...) {
		std::cout << "Error occured in the MessageClient demo program" << std::endl; 
		VCS_LOGCATCH;	// this will print the error message to the stdout
		return 2;
	}

	// 
	return 0;
}

//\end{verbatim}}
