from dotenv import load_dotenv

def load_environment(env_file=None):
    if env_file:
        load_dotenv(env_file)
    else:
        load_dotenv()
