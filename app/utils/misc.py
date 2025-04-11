import socket

def is_local_environment():
    hostname = socket.gethostname()
    local_hostnames = ['localhost', '127.0.0.1', 'LAP-CDE']
    return hostname in local_hostnames
