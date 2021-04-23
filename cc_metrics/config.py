
from environs import Env
from fitin import views_config 

env = Env()
env.read_env()

config = views_config(env.str("KEYVAULT_URL"))
