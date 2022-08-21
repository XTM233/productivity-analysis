import requests
from base64 import b64encode


class TogglApi:
    """Simple wrapper to the Toggle API."""
    def __init__(self, email: str, password: str):
        self.email = email
        self.password = password

    def get_time_entries(self):
        """
        Retrieve data from the TimeEntry API.
        See: https://developers.track.toggl.com/docs/api/time_entries/index.html
        """
        data = requests.get(
            'https://api.track.toggl.com/api/v9/me/time_entries',
            headers={
                'content-type': 'application/json',
                'Authorization': self._make_auth_string(),
            },
        )
        print(data.json())

    # TODO: get default workspace ID: https://developers.track.toggl.com/docs/api/me
    def get_project_data(self, workspace_id: str):
        """
        Retrieve data from the Projects API.
        See https://developers.track.toggl.com/docs/api/projects/index.html#get-workspaceprojects
        """
        data = requests.get(
            f'https://api.track.toggl.com/api/v9/workspaces/{workspace_id}/projects',
            headers={
                'content-type': 'application/json',
                'Authorization': self._make_auth_string(),
            },
        )
        print(data.json())

    def _make_auth_string(self) -> str:
        """
        Formats and returns a string for use with Toggl basic auth.
        See: https://developers.track.toggl.com/docs/authentication
        """
        return 'Basic ' + b64encode(bytes(f'{self.email}:{self.password}', 'utf-8')).decode('ascii')
