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
from typing import Dict, List, Optional
from datetime import date, datetime


@dc.dataclass
class Project:
    """Represents a Toggl project."""

    id: str
    name: str
    workspace_id: str
    color: str
    actual_hours: int


@dc.dataclass
class TimeEntry:
    """Represents a Toggl time entry."""

    id: str
    workspace_id: str
    project_id: str
    start: datetime
    stop: datetime
    duration: int
    description: str


@dc.dataclass
class DetailedReportsResult:
    """Represents the results of calling the `DetailedReports` API."""

    x_next_id: Optional[str]
    x_next_row_number: Optional[str]
    x_next_timestamp: Optional[str]
    x_page_size: str
    x_range_start: str
    x_range_end: str
    x_service_level: str
    time_entries: List[TimeEntry]


class TogglApi:
    """
    A simple wrapper to a few methods from the Toggle API, v9.
    See https://developers.track.toggl.com/docs/
    """

    def __init__(self, email: str, password: str):
        self.email = email
        self.password = password

    def me(self) -> Dict:
        """
        Retrieves data about 'me'
        See: https://developers.track.toggl.com/docs/api/me
        """
        res = requests.get(
            "https://api.track.toggl.com/api/v9/me",
            headers={
                "content-type": "application/json",
                "Authorization": self._make_auth_string(),
            },
        )
        if res.status_code != 200:
            raise ValueError(
                f"Request failed with status {res.status_code}: {res.text}."
            )
        return res.json()

    def time_entries(self, start_date: date, end_date: date) -> List[TimeEntry]:
        """
        Retrieves time entries from start_date inclusive until end_date exclusive.
        Note that Toggl only allows retrieving time entries from the past three months
        via this endpoint. For more, use the `detailed_reports()` method.
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
        if res.status_code != 200:
            raise ValueError(
                f"Request failed with status {res.status_code}: {res.text}."
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

    def project_data(self, workspace_id: str) -> List[Project]:
        """
        Retrieves data from the Projects API.
        See https://developers.track.toggl.com/docs/api/projects/index.html#get-workspaceprojects
        """
        res = requests.get(
            f"https://api.track.toggl.com/api/v9/workspaces/{workspace_id}/projects",
            headers={
                "content-type": "application/json",
                "Authorization": self._make_auth_string(),
            },
        )
        if res.status_code != 200:
            raise ValueError(
                f"Request failed with status {res.status_code}: {res.text}."
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

    def detailed_reports(
        self, workspace_id: str, start_date: date, end_date: date, next_row: int = 0
    ) -> DetailedReportsResult:
        """
        Retrieves data from the Detailed Reports API from start_date inclusive until
        end_date exclusive. See https://developers.track.toggl.com/docs/reports/detailed_reports
        """
        res = requests.post(
            f"https://api.track.toggl.com/reports/api/v3/workspace/{workspace_id}/search/time_entries",
            json={
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
            },
            headers={
                "content-type": "application/json",
                "X-Next-Row-Number": str(next_row),
                "Authorization": self._make_auth_string(),
            },
        )
        if res.status_code != 200:
            raise ValueError(
                f"Request failed with status {res.status_code}: {res.text}."
            )
        time_entries = [
            TimeEntry(
                str(raw["time_entries"][0]["id"]),
                workspace_id,
                raw["project_id"],
                datetime.fromisoformat(raw["time_entries"][0]["start"]),
                datetime.fromisoformat(raw["time_entries"][0]["stop"]),
                int(raw["time_entries"][0]["seconds"]),
                raw["description"],
            )
            for raw in res.json()
        ]
        return DetailedReportsResult(
            res.headers.get("X-Next-Id", None),
            res.headers.get("X-Next-Row-Number", None),
            res.headers.get("X-Next-Timestamp", None),
            res.headers["X-Page-Size"],
            res.headers["X-Range-Start"],
            res.headers["X-Range-End"],
            res.headers["X-Service-Level"],
            time_entries,
        )

    def _make_auth_string(self) -> str:
        """
        Formats and returns a string for use with Toggl basic auth.
        See: https://developers.track.toggl.com/docs/authentication
        """
        return "Basic " + b64encode(
            bytes(f"{self.email}:{self.password}", "utf-8")
        ).decode("ascii")
