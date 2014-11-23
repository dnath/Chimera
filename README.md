# Chimera
A Paxos-based replicated bank

## Preparing the environment
From the Chimera directory, run the following commands

	$ cd chimera-api
	$ virtualenv env
	New python executable in env/bin/python
	Installing setuptools, pip...done.
	$ ./env/bin/pip install flask
	...
	$ ../curl_test.sh /
	Chimera node is running

## Useful links
* [Flask -- a small RESTful API framework](http://flask.pocoo.org/)
  * [Background tasks with Celery](http://flask.pocoo.org/docs/0.10/patterns/celery/)
* [Paxos made simple](http://research.microsoft.com/en-us/um/people/lamport/pubs/paxos-simple.pdf)
  * [Using Paxos for replicated logs](http://www.youtube.com/watch?v=JEpsBg0AO6o)
