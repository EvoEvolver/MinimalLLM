import os


def update_env_var(env_var_name, env_var_value, verbose):
    rc_file = get_rc_file_path()
    # open the rc file
    with open(rc_file, "r") as f:
        lines = f.readlines()
    # find the line to update
    for i, line in enumerate(lines):
        if env_var_name in line:
            lines[i] = f"export {env_var_name}=\"{env_var_value}\"\n"
            break
    else:
        if verbose:
            print(f"Fail to find the environment variable {env_var_name} in the rc file.")
            print("Possible reasons:")
            print("1. The environment variable is not set in the rc file. (we only support RC file)")
            print("2. The environment variable is set in the rc file but with a different format. (we only support export VAR_NAME=\"VAR_VALUE\")")
            print(f"You might need to manually update the environment variable in the rc file.")
        return
    # write the lines back to the rc file
    with open(rc_file, "w") as f:
        f.writelines(lines)
    # source the rc file
    os.system(f"source {rc_file}")
    if verbose:
        print(f"Environment variable {env_var_name} has been updated to {env_var_value}.")
        print(f"RC file: {rc_file} has been updated.")
    return



def inject_env_var(env_var_name, env_var_value, verbose=True):
    """
    Inject an environment variable into the system by writing to the .xxxrc file
    :param env_var_name:
    :param env_var_value:
    :return:
    """
    # judge if the env var is already in the system
    if os.environ.get(env_var_name):
        if verbose:
            print(f"Environment variable {env_var_name} already exists in the system.")
        # compare whether the value is the same
        if os.environ.get(env_var_name) == env_var_value:
            if verbose:
                print(f"Environment variable {env_var_name} has the same value as the one you are trying to inject.")
        else:
            update_env_var(env_var_name, env_var_value, verbose)
        return

    rc_file = get_rc_file_path()

    export_cmd = f"export {env_var_name}=\"{env_var_value}\"\n"
    # open the rc file and write the export command to the first line
    with open(rc_file, "r") as f:
        lines = f.readlines()
    lines.insert(0, export_cmd)
    with open(rc_file, "w") as f:
        f.writelines(lines)

    # source the rc file
    os.system(f"source {rc_file}")

    # return the rc file

    if verbose:
        print(f"Environment variable {env_var_name} with value {env_var_value} has been injected into the system.")
        print(f"RC file: {rc_file} has been updated.")

    return


def get_rc_file_path():
    # get the current terminal type. zsh, bash
    terminal_type = os.environ.get("SHELL")
    terminal_type = terminal_type.split("/")[-1]
    # get the home directory
    home_dir = os.environ.get("HOME")
    # get the rc file
    rc_file = f"{home_dir}/.{terminal_type}rc"
    return rc_file


if __name__ == '__main__':
    inject_env_var("MY_VAR", "MY_VALUE1")
    print(os.environ.get("MY_VAR"))