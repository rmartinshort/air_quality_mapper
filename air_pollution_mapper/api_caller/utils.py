from dotenv import load_dotenv
from pathlib import Path
import os
def load_secrets():
    load_dotenv()
    env_path = Path(".") / ".env"
    load_dotenv(dotenv_path=env_path)

    google_maps_key = os.getenv("GOOGLE_MAPS_API_KEY")

    return {
        "GOOGLE_MAPS_API_KEY": google_maps_key,
    }


def assert_secrets(secrets_dict):
    assert secrets_dict["GOOGLE_MAPS_API_KEY"] is not None