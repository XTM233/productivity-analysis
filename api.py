# Copyright 2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import requests
import dataclasses as dc
from base64 import b64encode
from typing import Dict, List
from datetime import date, datetime


@dc.dataclass
class Project:
    id: str
    name: str
    workspace_id: str
    color: str
    actual_hours: int


@dc.dataclass
class TimeEntry:
    id: str
    workspace_id: str
    project_id: str
    start: datetime
    stop: datetime
    duration: int
    description: str


class TogglApi:
    """Simple wrapper to the Toggle API."""

    def __init__(self, email: str, password: str):
        self.email = email
        self.password = password

    # TODO: rename `me`
    def get_my_data(self) -> Dict:
        """
        Retrieve data about 'me'
        See: https://developers.track.toggl.com/docs/api/me
        """
        res = requests.get(
            "https://api.track.toggl.com/api/v9/me",
            headers={
                "content-type": "application/json",
                "Authorization": self._make_auth_string(),
            },
        )
        return res.json()

    def get_time_entries(self, start_date: date, end_date: date) -> List[TimeEntry]:
        """
        Retrieve time entries from start_date until end_date, inclusive.
        See: https://developers.track.toggl.com/docs/api/time_entries/index.html
        """
        res = requests.get(
            "https://api.track.toggl.com/api/v9/me/time_entries",
            params={
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
            },
            headers={
                "content-type": "application/json",
                "Authorization": self._make_auth_string(),
            },
        )
        return [
            TimeEntry(
                raw["id"],
                raw["workspace_id"],
                raw["project_id"],
                datetime.fromisoformat(raw["start"]),
                datetime.fromisoformat(raw["stop"]),
                int(raw["duration"]),
                raw["description"],
            )
            for raw in res.json()
        ]

    def get_project_data(self, workspace_id: str) -> List[Project]:
        """
        Retrieve data from the Projects API.
        See https://developers.track.toggl.com/docs/api/projects/index.html#get-workspaceprojects
        """
        res = requests.get(
            f"https://api.track.toggl.com/api/v9/workspaces/{workspace_id}/projects",
            headers={
                "content-type": "application/json",
                "Authorization": self._make_auth_string(),
            },
        )
        return [
            Project(
                raw["id"],
                raw["name"],
                raw["workspace_id"],
                raw["color"],
                int(raw["actual_hours"]),
            )
            for raw in res.json()
        ]

    def _make_auth_string(self) -> str:
        """
        Formats and returns a string for use with Toggl basic auth.
        See: https://developers.track.toggl.com/docs/authentication
        """
        return "Basic " + b64encode(
            bytes(f"{self.email}:{self.password}", "utf-8")
        ).decode("ascii")
