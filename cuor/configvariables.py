IP_ELASTIC = '10.118.31.125'
IP_POSGRE = '10.118.31.44'
IP_RABBIT = '10.118.31.100'
IP_REDIS = '10.118.31.237'

#: Since HAProxy and Nginx route all requests no matter the host header
#: provided, the allowed hosts variable is set to localhost. In production it
#: should be set to the correct host and it is strongly recommended to only
#: route correct hosts to the application.
APP_ALLOWED_HOSTS = ['cuor.cu', 'localhost', '127.0.0.1']


CUOR_DATA_DIRECTORY = 'data'
