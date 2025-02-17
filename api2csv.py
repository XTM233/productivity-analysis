import api
import requests
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from datetime import date, datetime, timezone
from base64 import b64encode
from dateutil.relativedelta import relativedelta

# Enter your Toggl email and password here.
TOGGL_EMAIL = r'shenmingxin2000@gmail.com'
TOGGL_PASSWORD = r'79C4666496efe567311ec8bd1f768580'

_api = api.TogglApi(TOGGL_EMAIL, TOGGL_PASSWORD)

def api_to_csv(api, out_dir):

    # Call the `me` endpoint and get the default workspace ID.
    my_data = api.me()
    WORKSPACE_ID = my_data['default_workspace_id']
    print(f"Default workspace_id is {WORKSPACE_ID}.")

    # Load project data.
    projects = api.project_data(WORKSPACE_ID)
    print(f"Loaded data for {len(projects)} projects.")

    # Calculate the sum of hours tracked.
    print(f"You tracked a total of {sum(p.actual_hours for p in projects)} hours.")

    # Sort projects by time spent.
    projects.sort(key=lambda p: p.actual_hours, reverse=True)
    print('\n'.join(f"{p.name}: {p.actual_hours} hours" for p in projects))

    # Load all tracked time entries from the past three months.
    # This is the maximum amount of time that the Toggl TimeEntry API supports.
    start_date = (datetime.now() - relativedelta(months=3)).date()
    end_date = datetime.now().date()

    time_entries = api.time_entries(start_date, end_date)
    print(f"Loaded {len(time_entries)} time entries between {start_date} and {end_date}.")

    df = create_df(time_entries, projects)

    if out_dir:
        df.to_csv(out_dir + f"/Toggl_time_entries_{start_date}_to_{end_date}.csv", header=True, index=False)

    return df

# Convert entries data into dataframe

def create_df(time_entries, projects):
    data = [entry.__dict__ for entry in time_entries]

    # 创建 DataFrame
    df = pd.DataFrame(data)

    # 优化时间列显示（如果时区信息未被自动识别）
    df['Start'] = pd.to_datetime(df['start'], utc=True)
    df['End'] = pd.to_datetime(df['stop'], utc=True)

    # 可选：将 duration 转换为时间增量（单位：秒）
    df['Duration'] = pd.to_timedelta(df['duration'], unit='s')
    # 将 projects 转换为字典映射：{project_id: project_name}
    project_id_to_name = {project.id: project.name for project in projects}

    # 使用 map 函数将 project_id 替换为 project name
    df['Project'] = df['project_id'].map(project_id_to_name)
    df.drop(columns=['project_id', 'workspace_id', 'start', 'stop'], inplace=True)
    print(df.head())
    return df

##########
# format #
##########
# Load our CSV file into a dataframe.
def process_export(year, in_dir='raw_data', out_dir='processed_data', filter_date=None, drop_columns=None):
    time_entries = pd.read_csv(
        in_dir + f"/Toggl_time_entries_{year}-01-01_to_{year}-12-31.csv", 
        parse_dates=["Start date", "End date"],
        date_format="%Y-%m-%d",
    )
    # print(f'Data has {time_entries.shape[0]} rows and {time_entries.shape[1]} columns')

    # Filter data by date (`start_date` inclusive, `end_date` exclusive).
    # NOTE by default, no filter is applied.
    if not filter_date:
        start_date = f'{year}-01-01'
        end_date = f'{year + 1}-01-01'
    else:
        raise NotImplementedError
    time_entries = time_entries[(time_entries['Start date'] >= start_date) & (time_entries['End date'] < end_date)]
    print(f'Data has {time_entries.shape[0]} rows after filtering.')
    time_entries.head()

    time_entries = time_entries.drop(['User', 'Email', 'Task', 'Billable'], axis=1)
    if drop_columns:
        raise NotImplementedError

    # Toggl provides the data with dates and times separated. We need to combine them back together.
    # First, we convert the "Start time" and "End time" columns to `pandas.dt.time`. 
    time_entries['Start time'] = pd.to_datetime(time_entries['Start time'], format="%H:%M:%S").dt.time
    time_entries['End time'] = pd.to_datetime(time_entries['End time'], format="%H:%M:%S").dt.time
    # Then we use `pd.Timestamp.combine()` to combine the date and time columns into new column called "Start" and "End". 
    time_entries['Start'] = time_entries.apply(lambda x: pd.Timestamp.combine(x['Start date'], x['Start time']), axis=1)
    time_entries['End'] = time_entries.apply(lambda x: pd.Timestamp.combine(x['End date'], x['End time']), axis=1)
    # Finally, we remove the original columns.
    time_entries = time_entries.drop(['Start date', 'Start time', 'End date', 'End time'], axis=1)

    # Recalculate the "Duration" column so that we get instances of `pandas.Timedelta`.
    time_entries['Duration'] = time_entries['End'] - time_entries['Start']
    time_entries.head()

    if out_dir:
        time_entries.to_csv(out_dir + f"/Toggl_time_entries_{year}-01-01_to_{year}-12-31.csv", header=True, index=False)
 
    return time_entries

###########
# analyze #
###########
    
def count_days(df, start_hour=0):
    """
    Count the number of days that have at least one entry in `df`. Consider a day to be from `start_hour` to `start_hour` the next day.
    """
    # if 'Start' is earlier than `start_hour`, we consider it to be part of the previous day.
    df['start_day'] = df['Start'].dt.floor('d') + pd.to_timedelta((df['Start'].dt.hour < start_hour).astype(int), unit='d')
    # if 'End' is earlier than `start_hour`, we consider it to be part of the previous day.
    df['end_day'] = df['End'].dt.floor('d') + pd.to_timedelta((df['End'].dt.hour < start_hour).astype(int), unit='d')
    
    # Combine start_day and end_day to get all unique days
    unique_days = pd.concat([df['start_day'], df['end_day']]).unique()
    
    return len(unique_days)

# 假设 df 是之前创建的 DataFrame
# 筛选出指定的 project_name
def hourly_chart(df, filter, normalised=False):
    filtered_df = df.copy()
    for _, key in enumerate(filter):
                filtered_df = filtered_df[filtered_df[key].isin(filter[key])]
    # 初始化一个字典，用于存储每个小时的时间贡献
    hourly_distribution = np.zeros(24)
    print(filtered_df)
    # 遍历筛选后的数据
    for _, row in filtered_df.iterrows():
        start = row['Start']
        stop = row['End']
        duration = (stop - start).total_seconds() / 60  # 将持续时间转换为分钟

        # 对 start 向后取整小时
        start_ceil = start.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
        
        # 对 stop 向前取整小时
        stop_floor = stop.replace(minute=0, second=0, microsecond=0)
        
        # 如果 start_ceil > stop_floor，说明没有完整的整小时区间
        if start_ceil > stop_floor:
            # 只有部分区间，直接计算 start 到 stop 的时间贡献
            segment_duration = (stop - start).total_seconds() / 60
            hour = start.hour
            hourly_distribution[hour] += segment_duration
        else:
            # 处理 start 到 start_ceil 的部分区间
            segment_duration = (start_ceil - start).total_seconds() / 60
            hour = start.hour
            hourly_distribution[hour] += segment_duration
            
            # 处理 stop_floor 到 stop 的部分区间
            segment_duration = (stop - stop_floor).total_seconds() / 60
            hour = stop.hour
            hourly_distribution[hour] += segment_duration
            
            # 处理中间的完整小时区间
            full_hours = np.arange(start_ceil.hour, stop_floor.hour)  # 完整的小时区间
            hourly_distribution[full_hours] += 60  # 每个完整小时 +60 分钟

    if normalised:
        days = count_days(filtered_df)
        hourly_distribution /= days 

    # 绘制条状图
    plt.figure(figsize=(12, 6))
    plt.bar(np.arange(24),hourly_distribution, color='#06a893')
    plt.xlabel('Hour of the Day')
    plt.ylabel('Total Minutes')
    if normalised:
        plt.ylim(0, 60)
    plt.title('Time Distribution by Hour for Selected Projects')
    plt.xticks(range(24), [f'{hour}:00-{hour+1}:00' for hour in range(24)], rotation=45)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()

    return hourly_distribution
