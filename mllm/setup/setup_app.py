import os, dotenv
import time
# to use the .env.mllm file
import mllm

try:
    import streamlit as st
except ImportError:
    print("Streamlit not installed. Please install it using `pip install streamlit`.")
    exit(1)

def update_env_var(dotenv_file, env_var_name, env_var_value):
    dotenv.set_key(dotenv_file, env_var_name, env_var_value)
    dotenv.load_dotenv(dotenv_file, override=True)

provider_key_dict = {
    "openai": ["OPENAI_API_KEY"],
    "anthropic": ["ANTHROPIC_API_KEY"],
    "replicate": ["REPLICATE_API_KEY"],
    "gemini": ["GEMINI_API_KEY"],
    "deepseek": ["DEEPSEEK_API_KEY"],
    "openrouter": ["OPENROUTER_API_KEY"],
}

st.title("MinimalLLM Setup Wizard")
st.write("This wizard will help you set up your environment to use MLLM.")

try:
    dotenv_file = dotenv.find_dotenv(".mllm.env", raise_error_if_not_found=True)
    dotenv_file_dir = os.path.dirname(dotenv_file)
    st.write(f"Using .env.mllm file at `{dotenv_file}`")
except IOError:
    dotenv_file = os.path.join(os.getcwd(), ".mllm.env")
    st.write(f"No .env file found. Will create a new one at the following directory")
    dotenv_file_dir = os.path.dirname(dotenv_file)
    dotenv_file_dir = st.text_input("Enter the path to the .env file:", value=dotenv_file_dir)

# Provider selection
provider = st.selectbox("Select your provider:", list(provider_key_dict.keys()))
st.write(f"You have selected **{provider}** as your provider.")

# Check and display current environment variables
st.write("### Required Environment Variables")
not_set = False

env_values = {}
for env_var in provider_key_dict[provider]:
    env_values[env_var] = os.environ.get(env_var)
    if env_values[env_var] is None:
        not_set = True
        st.write(f"- {env_var}: **Not Set** ❌")
    else:
        st.write(f"- {env_var}: `{env_values[env_var]}` ✅")

# Prompt to set environment variables if needed
if not_set:
    set_vars = st.checkbox(
        "Some environment variables are not set. Do you want to set them?")
else:
    set_vars = st.checkbox(
        "All environment variables are set. Do you want to change them?")

if set_vars:
    new_values = {}
    for env_var in provider_key_dict[provider]:
        new_values[env_var] = st.text_input(f"Enter the value for {env_var}:", value=env_values[env_var])

    if st.button("Save Environment Variables"):
        for env_var, value in new_values.items():
            if value and value != env_values[env_var]:
                dotenv_file = os.path.join(dotenv_file_dir, ".mllm.env")
                update_env_var(dotenv_file, env_var, value)
                os.environ[env_var] = value  # Ensure it's updated in the session
        st.write(f"Environment variables set to {dotenv_file}!")
        refresh_secs = 1
        st.write(f"Restarting the app in {refresh_secs} seconds...")
        time.sleep(refresh_secs)
        st.rerun()