import logging
logging.basicConfig(level=logging.DEBUG)

REST_ENABLE_CORS = True



# IP_ELASTIC = '192.168.56.6'
# IP_POSGRE = '192.168.56.3'
# IP_RABBIT = '192.168.56.4'
# IP_REDIS = '192.168.56.5'


IP_ELASTIC = 'crai-sceiba-elastic0.upr.edu.cu'
IP_POSGRE = 'crai-posgre.upr.edu.cu'
IP_RABBIT = 'crai-sceiba-rabbit.upr.edu.cu'
IP_REDIS = 'crai-sceiba-redis.upr.edu.cu'


#: Since HAProxy and Nginx route all requests no matter the host header
#: provided, the allowed hosts variable is set to localhost. In production it
#: should be set to the correct host and it is strongly recommended to only
#: route correct hosts to the application.
APP_ALLOWED_HOSTS = ['cuor.cu', 'localhost', '127.0.0.1', '10.2.83.160']


CUOR_DATA_DIRECTORY = 'data'
