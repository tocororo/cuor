import logging
logging.basicConfig(level=logging.DEBUG)

REST_ENABLE_CORS = True



IP_ELASTIC = '10.143.231.141'
IP_POSGRE = '10.143.231.120'
IP_RABBIT = '10.143.231.15'
IP_REDIS = '10.143.231.43'


# IP_ELASTIC = 'crai-sceiba-elastic0.upr.edu.cu'
# IP_POSGRE = 'crai-posgre.upr.edu.cu'
# IP_RABBIT = 'crai-sceiba-rabbit.upr.edu.cu'
# IP_REDIS = 'crai-sceiba-redis.upr.edu.cu'


#: Since HAProxy and Nginx route all requests no matter the host header
#: provided, the allowed hosts variable is set to localhost. In production it
#: should be set to the correct host and it is strongly recommended to only
#: route correct hosts to the application.
APP_ALLOWED_HOSTS = ['cuor.cu', 'localhost', '127.0.0.1', '10.2.83.160','192.168.1.100']

INTERNAL_CLIENT_APPS_SECRETS = ["Vpb7TPrQcM9FVyjxGnuuwtdlNY869DQV5KVfiTNmgT4embZK6zFTI9fz8xQS"]
CUOR_DATA_DIRECTORY = 'data'
