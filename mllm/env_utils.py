import os


def check_openai_env():
    return check_env_names(["OPENAI_API_KEY"])

def check_anthropic_env():
    return check_env_names(["ANTHROPIC_API_KEY"])

def check_google_env():
    return True

def check_replicate_env():
    return check_env_names(["REPLICATE_API_KEY"])

def check_env_names(names):
    for name in names:
        if name not in os.environ:
            set_env_var_prompt(name)
            return False
    return True

def set_env_var_prompt(env_var_name):
    print(f"Warning: Please set the environment variable {env_var_name} to the appropriate value.")