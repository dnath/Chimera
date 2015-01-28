# Chimera
Paxos-based Replicated Bank Ledger

Authors: Daniel Kudrow, Dev Nath

## Running Chimera
For the Chimera node server,
	
	$ ./server.py <ip_addr>:<port> <url_to_node_config> > server.log

For running a Chimera client,

	$ ./client.py <node_ip_addr>:<port>


## Useful links
* [Flask -- a small RESTful API framework](http://flask.pocoo.org/)
* [Background tasks with Celery](http://flask.pocoo.org/docs/0.10/patterns/celery/)
* [Paxos made Simple](http://research.microsoft.com/en-us/um/people/lamport/pubs/paxos-simple.pdf)
* [Using Paxos for replicated logs](http://www.youtube.com/watch?v=JEpsBg0AO6o)

