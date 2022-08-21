import os
from api import TogglApi


# Names of expected environment variables
ENV_EMAIL = 'TOGGL_EMAIL'
ENV_PASSWORD = 'TOGGL_PASSWORD'


if __name__ == '__main__':
    """You need to set TOGGL_EMAIL and TOGGL_PASSWORD as environment variables"""
    if ENV_EMAIL not in os.environ:
        raise ValueError(f'"{ENV_EMAIL}" environment variable must be set')
    if ENV_PASSWORD not in os.environ:
        raise ValueError(f'"{ENV_PASSWORD}" environment variable must be set')

    email = os.environ[ENV_EMAIL]
    password = os.environ[ENV_PASSWORD]

    api = TogglApi(email, password)
    api.get_project_data('5684519')
