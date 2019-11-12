# Process Memory
This is the processing memory of each instanced app, which keeps a history of what happened to the data.

This application is built using the following high level architecture:
- Nginx: Reverse HTTP proxy
- Gunicorn:  WSGI HTTP Server
- Flask: Application Server
- Document Database (must be compatible with MongoDB 3.6+)

## Configuration

Use a Document Database, MongoDB 3.6 compatible and proceed to create the database and collection.

- Database Name: platform
- Collection Name: process_memory

You need to configure the environment variables to activate the service. They have default values that should be only
used for development.

### Libraries

Make sure the development environment has been correctly configured. 
If you get errors like *fatal error: Python.h: No such file or directory* you may be missing development packages.

```shell script
sudo apt install libpython3.7-dev python3.7-dev
sudo apt-get install -y libsnappy-dev
```

O Windows, you need to install the provided whl snappy file. Below, the file is for Python 3.7 32-bit.
If you need other versions, download them from <https://www.lfd.uci.edu/~gohlke/pythonlibs/#python-snappy>
```shell script
pip install python_snappy-0.5.4-cp37-cp37m-win_amd32.whl
```

Then, install it on your virtual environment (VE). Make sure you are in the correct VE folder.
```shell script
pipenv shell
pipenv install python_snappy-0.5.4-cp37-cp37m-win_amd32.whl
```


### DOCDB        

The process memory uses a document database repository to save its data. These are the environment variables that 
should be used to correctly configure the service:
        
- **DOCDB_USER**: database username;
- **DOCDB_SECRET**: database password;
- **DOCDB_HOST**: database server address;
- **DOCDB_COLLECTION**: default collection that you want to access;
- **DOCDB_OPTIONS**: these are other configuration options necessary to connect.
- **DOCDB_MAX_DATA**: the maximum accepted value for this is 16 million bytes.

Follow the examples below for all of the listed above.

**Linux**

```shell script
export DOCDB_HOST=myproject.cluster-xpto123.us-east-3.something.amazonaws.com
export DOCDB_COLLECTION=my_collection
export DOCDB_OPTIONS=/test?ssl=true&replicaSet=rs0&readPreference=secondaryPreferred
```

**Windows**
```shell script
set DOCDB_HOST=myproject.cluster-xpto123.us-east-3.something.amazonaws.com
set DOCDB_COLLECTION=my_collection
set DOCDB_OPTIONS=/test?ssl=true&replicaSet=rs0&readPreference=secondaryPreferred
```

## Running the Process Memory App
There are two options to create and read logs.

Below, use the '-' sign to output logs to the console. This is useful for development, testing and debugging.
```shell script
gunicorn wsgi:process_memory_app --log-level debug --log-file -
```

Another option is to log only errors and output to a file instead of the console.
```shell script
gunicorn wsgi:process_memory_app --name Memory --workers 3 --log-level error --log-file memorylog.txt
```
Where
1. **gunicorn** starts the WSGI server.
1. **--bind 0.0.0.0:5000** binds the server to the address and port.
1. **wsgi:process_memory_app** configures the gunicorn entry point (wsgi.py) and the app to execute.
1. **-w 3** tells gunicorn to start 3 workers to take requests.
1. **--log-level** states the log level: debug | info | warning | error | critical

### Reference
http://docs.gunicorn.org/en/stable/settings.html

## MongoDB Support

The following line inside *requirements.txt* installs a series of packages that work together with PyMongo:
```python
(pymongo[tls,srv,gssapi]==3.8.0)
```
- **pymongo**: installs pymongo
- **tls**: TLS / SSL support may require ipaddress and certifi or wincertstore depending on the Python version in use.
- **srv**: Support for mongodb+srv:// URIs requires dnspython
- **gssapi**: authentication requires pykerberos on Unix or WinKerberos on Windows.
