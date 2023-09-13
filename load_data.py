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
import click
import csv
from pathlib import Path
from datetime import datetime
from api import Project, TimeEntry, TogglApi
from typing import List


def write_to_csv(projects: List[Project], time_entries: List[TimeEntry], out: Path):
    # Map project ID to name.
    name_from_project_id = {p.id: p.name for p in projects}
    with open(out, "w", newline="") as f:
        writer = csv.writer(f, delimiter=",")
        writer.writerow(["Project Name", "Start Time", "End Time", "Duration (sec)"])
        for t in time_entries:
            t.start.isoformat()
            writer.writerow(
                [
                    name_from_project_id[t.project_id],
                    t.start.isoformat(),
                    t.stop.isoformat(),
                    t.duration,
                ]
            )


# TODO: document
@click.command()
@click.option("--email", required=True)
@click.password_option(required=True)
@click.option("--start_date", type=click.DateTime(formats=["%Y-%m-%d"]), required=True)
@click.option("--end_date", type=click.DateTime(formats=["%Y-%m-%d"]), required=True)
@click.option(
    "--out",
    type=click.Path(file_okay=True, dir_okay=False, writable=True, path_type=Path),
)
def load_data(
    email: str,
    password: str,
    start_date: datetime,
    end_date: datetime,
    out: Path,
):
    api = TogglApi(email, password)
    click.echo(f"Fetching data from `me` endpoint...")
    my_data = api.get_my_data()
    workspace_id = my_data["default_workspace_id"]
    click.echo(f"Got default workspace {workspace_id}.")
    projects = api.get_project_data(workspace_id)
    click.echo(f"Got data for {len(projects)} projects.")
    time_entries = api.get_time_entries(start_date.date(), end_date.date())
    click.echo(f"Got data for {len(time_entries)} time entries.")
    write_to_csv(projects, time_entries, out)
    click.echo(f"Wrote data to {out}.")


if __name__ == "__main__":
    load_data()
