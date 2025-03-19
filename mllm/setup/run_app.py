from streamlit.web import cli
import os

def run_setup_app():
    this_path = os.path.dirname(os.path.abspath(__file__))
    cli.main_run([this_path + "/setup_app.py"])

if __name__ == '__main__':
    run_setup_app()