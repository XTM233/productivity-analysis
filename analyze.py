import os
import dataclasses as dc
import datetime as dt
import matplotlib.pyplot as plt
from api import TogglApi


# Names of expected environment variables
ENV_EMAIL = 'TOGGL_EMAIL'
ENV_PASSWORD = 'TOGGL_PASSWORD'


@dc.dataclass
class Me:
    default_workspace_id: str


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
    start: dt.datetime
    stop: dt.datetime
    duration: int
    description: str


if __name__ == '__main__':
    """You need to set TOGGL_EMAIL and TOGGL_PASSWORD as environment variables"""
    if ENV_EMAIL not in os.environ:
        raise ValueError(f'"{ENV_EMAIL}" environment variable must be set')
    if ENV_PASSWORD not in os.environ:
        raise ValueError(f'"{ENV_PASSWORD}" environment variable must be set')

    email = os.environ[ENV_EMAIL]
    password = os.environ[ENV_PASSWORD]

    api = TogglApi(email, password)
    WORKSPACE_ID = '5684519'
    projects = {
        raw['id']: Project(
            raw['id'],
            raw['name'],
            raw['workspace_id'],
            raw['color'],
            int(raw['actual_hours']),
        ) for raw in api.get_project_data(WORKSPACE_ID)
    }
    print(projects)
    # api.get_my_data()

    fig, ax = plt.subplots()
    fig.suptitle('Time Spent')
    ax.pie([p.actual_hours for p in projects.values()], labels=[p.name for p in projects.values()], autopct='%1.1f%%')
    plt.show()
