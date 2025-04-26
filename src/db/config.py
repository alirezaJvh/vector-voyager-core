from decouple import config as decouple_config

# DATABASE_NAME = decouple_config('DATABASE_NAME', default="")
# REDIS_URL = decouple_config('REDIS_URL', default="")
REDIS_PORT = decouple_config('REDIS_PORT', default="")
OPENAI_API_KEY = decouple_config('OPENAI_API_KEY', default="")
