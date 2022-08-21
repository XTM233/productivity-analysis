import os
import requests
from base64 import b64encode


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

    # See: https://developers.track.toggl.com/docs/authentication
    auth_string = 'Basic ' + b64encode(bytes(f'{email}:{password}', 'utf-8')).decode('ascii')
    print(auth_string)

    # See: https://developers.track.toggl.com/docs/api/time_entries/index.html
    data = requests.get(
        'https://api.track.toggl.com/api/v9/me/time_entries',
        headers={
            'content-type': 'application/json',
            'Authorization': auth_string,
        },
    )
    print(data.json())
