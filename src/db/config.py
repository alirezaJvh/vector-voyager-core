from decouple import config as decouple_config

# DATABASE_NAME = decouple_config('DATABASE_NAME', default="")
OPENAI_API_KEY = decouple_config('OPENAI_API_KEY', default="")
