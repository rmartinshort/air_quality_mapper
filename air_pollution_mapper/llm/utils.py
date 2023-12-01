from dotenv import load_dotenv
from pathlib import Path
import os


def load_secrets():
    load_dotenv()
    env_path = Path(".") / ".env"
    load_dotenv(dotenv_path=env_path)

    open_ai_api_key = os.getenv("OPENAI_API_KEY")

    return {
        "OPENAI_API_KEY": open_ai_api_key,
    }


def assert_secrets(secrets_dict):
    assert secrets_dict["OPENAI_API_KEY"] is not None
