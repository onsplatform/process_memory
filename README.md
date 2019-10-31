# Process Memory
This is the processing memory of each instanced app, which keeps a history of what happened to the data.

This application is built using the following high level architecture:
- Nginx: Reverse HTTP proxy
- Gunicorn:  WSGI HTTP Server
- Flask: Application Server
- Document Database (must be compatible with MongoDB 3.6+)

# Configuration

# Running the Process Memory App

```shell script
gunicorn wsgi:process_memory_app
```


## MongoDB Support

The following line inside *requirements.txt* installs a series of packages that work together with PyMongo:
```python
(pymongo[tls,srv,gssapi]==3.8.0)
```
- **pymongo**: installs pymongo
- **tls**: TLS / SSL support may require ipaddress and certifi or wincertstore depending on the Python version in use.
- **srv**: Support for mongodb+srv:// URIs requires dnspython
- **gssapi**: authentication requires pykerberos on Unix or WinKerberos on Windows.