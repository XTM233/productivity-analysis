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
    """
    Given a list of projects and time entries corresponding to those projects,
    writes the data in CSV format to `out`. Will join the project names with the
    time entries via `time_entry.project_id`.
    """
    # Map project ID to name.
    name_from_project_id = {p.id: p.name for p in projects}
    with open(out, "w+", newline="") as f:
        writer = csv.writer(f, delimiter=",")
        writer.writerow(["Project Name", "Start Time", "End Time", "Description"])
        for t in time_entries:
            writer.writerow(
                [
                    name_from_project_id[t.project_id],
                    t.start.isoformat(),
                    t.stop.isoformat(),
                    t.description,
                ]
            )


@click.command()
@click.option("--email", required=True)
@click.password_option(required=True)
@click.option("--start_date", type=click.DateTime(formats=["%Y-%m-%d"]), required=True)
@click.option("--end_date", type=click.DateTime(formats=["%Y-%m-%d"]), required=True)
@click.option(
    "--out",
    type=click.Path(file_okay=True, dir_okay=False, writable=True, path_type=Path),
    required=True,
)
def load_data(
    email: str,
    password: str,
    start_date: datetime,
    end_date: datetime,
    out: Path,
):
    """
    Loads project and time entry data from the Toggl API and writes it to a CSV file.

    EMAIL: email address of the Toggl account.
    PASSWORD: password for the Toggl account.
    START_DATE: start date for which to load time entries, inclusive, in YYYY-MM-DD format.
    END_DATE: end date for which to load time entries, exclusive, in YYYY-MM-DD format.
    OUT: path to the CSV file to write data to. Will create the file if it doesn't exist, or overwrite an existing file.
    """
    api = TogglApi(email, password)
    click.echo(f"Fetching data from `me` endpoint...")
    my_data = api.me()
    workspace_id = my_data["default_workspace_id"]
    click.echo(f"Got default workspace {workspace_id}.")

    projects = api.project_data(workspace_id)
    click.echo(f"Got data for {len(projects)} projects.")

    # Load all time entries via the `detailed_reports` API.
    # Note: it seems that Toggl limits the results to 100 entries, at least for my free account.
    time_entries: List[TimeEntry] = []
    next_row = 0
    while True:
        click.echo(f"Calling DetailedReports API with next_row={next_row}.")
        next_res = api.detailed_reports(
            workspace_id, start_date.date(), end_date.date(), next_row=next_row
        )
        time_entries += next_res.time_entries
        # We will need another call if the response has a `next_row_number` and that
        # number is bigger than the one we just requested.
        if next_res.x_next_row_number and int(next_res.x_next_row_number) > next_row:
            next_row = int(next_res.x_next_row_number)
        else:
            # No more results.
            break

    click.echo(f"Got data for {len(time_entries)} time entries.")
    write_to_csv(projects, time_entries, out)
    click.echo(f"Wrote data to {out}.")


if __name__ == "__main__":
    load_data()
