IP_ELASTIC = '10.2.4.62'
IP_POSGRE = '10.20.231.28'
IP_RABBIT = '10.20.231.157'
IP_REDIS = '10.20.231.163'

#: Since HAProxy and Nginx route all requests no matter the host header
#: provided, the allowed hosts variable is set to localhost. In production it
#: should be set to the correct host and it is strongly recommended to only
#: route correct hosts to the application.
APP_ALLOWED_HOSTS = ['cuor.cu', 'localhost', '127.0.0.1']


CUOR_DATA_DIRECTORY = 'data'
