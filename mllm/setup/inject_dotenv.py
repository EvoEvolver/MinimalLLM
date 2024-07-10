import os

import dotenv


def update_env_var(env_var_name, env_var_value, verbose):
    try:
        dotenv_file = dotenv.find_dotenv(raise_error_if_not_found=True)
        print("Updating .env file at " + dotenv_file + "? (y/n)")
        choice = input()
        if choice != "y":
            print("No .env file updated. Exiting.")
    except IOError:
        print("No .env file found.")
        print("Creating a new .env file at user home directory? (y/n)")
        choice = input()
        if choice == "y":
            dotenv_file = os.environ.get("HOME") + "/.env"
        else:
            print("No .env file created. Exiting.")
            return
    dotenv.set_key(dotenv_file, env_var_name, env_var_value)
    if verbose:
        print(f"Environment variable {env_var_name} has been updated to {env_var_value}.")
        print(f"env file: {dotenv_file} has been updated.")
    dotenv.load_dotenv(dotenv_file, override=True)
    return



if __name__ == '__main__':
    update_env_var("MY_VAR", "MY_VALUE1", True)
    print(os.environ.get("MY_VAR"))