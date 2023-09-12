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
import os
import matplotlib.pyplot as plt
from api import TogglApi


# Names of expected environment variables
ENV_EMAIL = "TOGGL_EMAIL"
ENV_PASSWORD = "TOGGL_PASSWORD"


if __name__ == "__main__":
    """You need to set TOGGL_EMAIL and TOGGL_PASSWORD as environment variables"""
    if ENV_EMAIL not in os.environ:
        raise ValueError(f'"{ENV_EMAIL}" environment variable must be set')
    if ENV_PASSWORD not in os.environ:
        raise ValueError(f'"{ENV_PASSWORD}" environment variable must be set')

    email = os.environ[ENV_EMAIL]
    password = os.environ[ENV_PASSWORD]

    api = TogglApi(email, password)
    WORKSPACE_ID = "5684519"
    projects = api.get_project_data(WORKSPACE_ID)
    print(projects)

    fig, ax = plt.subplots()
    fig.suptitle("Time Spent")
    ax.pie(
        [p.actual_hours for p in projects],
        labels=[p.name for p in projects],
        autopct="%1.1f%%",
    )
    plt.show()
