import csv
import datetime
from datetime import datetime as dt
import json

import pytz

from utils.constants import INITIATED, PROCESSING, DONE, DEFAULT_TIMEZONE, FAILED


def format_report_response(data):
    res = dict()
    if data[0]['status'] == DONE:
        res['report_url'] = data[0]['report_url']
    if data[0]['status'] in (FAILED, PROCESSING, INITIATED):
        res['report_url'] = None
    res['status'] = data[0]['status']
    return res


def get_const_data(data):
    const_k_v = {item['key']: item['value'] for item in data}
    return const_k_v


def get_datetime_obj(datetime_str):
    datetime_obj = datetime.datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S.%f%z')
    return datetime_obj


def format_serializer_data(serializer_data):
    return json.loads(json.dumps(serializer_data))


def get_list_of_tuples_to_list(list_of_tuples):
    return [t_item for l_item in list_of_tuples for t_item in l_item]


def time_frame_dates(curr_timestamp, no_of_weeks):
    start_date = curr_timestamp + datetime.timedelta(-(no_of_weeks * 7))
    end_date = curr_timestamp
    return start_date, end_date


def get_curr_timestamp_utc():
    return datetime.datetime.now(datetime.timezone.utc)


def get_previous_day_of_week(timestamp_utc):
    prev_date = timestamp_utc + datetime.timedelta(-1)
    return prev_date.weekday()


def get_curr_day_of_week(timestamp_utc):
    return timestamp_utc.weekday()


def get_time_object(time_str):
    time_obj = dt.strptime(time_str, '%H:%M:%S').time()
    return time_obj


def get_store_menu_data(menu_data):
    menu_dict = dict()
    for item in menu_data:
        store_id = item['store_id']
        start_time_local = get_time_object(item['start_time_local'])
        end_time_local = get_time_object(item['end_time_local'])
        timings = [start_time_local, end_time_local]
        if menu_dict.get(store_id):
            if menu_dict.get(store_id).get(item['day']):
                menu_dict[store_id][item['day']].append(timings)
            else:
                menu_dict[store_id][item['day']] = [timings]
        else:
            menu_dict[store_id] = {item['day']: [timings]}
    return menu_dict


def get_local_timezone_data(timezone_data):
    return {item['store_id']: item['timezone_str'] for item in timezone_data}


def get_timezone(timezone_str):
    return pytz.timezone(timezone_str)


def get_datetime_utc(timezone, date_, time_str):
    return timezone.localize(dt.combine(date_.date(), time_str)).astimezone(pytz.utc)


def get_curr_day_start(timestamp):
    curr_day = timestamp.replace(hour=0, minute=0, second=0, microsecond=0)
    return curr_day


def get_specific_date(timestamp, delta=1, is_hours=False, hours=1):
    if is_hours:
        prev_datetime = timestamp + datetime.timedelta(hours=hours)
    else:
        prev_datetime = timestamp + datetime.timedelta(-delta)
    return prev_datetime


def get_timeframe_dates(start_date, end_date):
    delta = end_date - start_date
    day_date = {}
    for i in range(delta.days + 1):
        date_ = start_date + datetime.timedelta(days=i)
        day_ = get_curr_day_of_week(date_)
        day_date[day_] = date_
    return day_date


def get_store_menu_utc(menu, store_timezone, day_date):
    utc_menu = dict()
    for k, v in menu.items():
        timings = []
        for item in v:
            _date = day_date[k]
            start_time_utc = get_datetime_utc(store_timezone, _date, item[0])
            end_time_utc = get_datetime_utc(store_timezone, _date, item[1])
            if start_time_utc >= end_time_utc:
                end_time_utc += datetime.timedelta(days=1)
            timings.append([start_time_utc, end_time_utc])
        utc_menu[k] = timings
    return utc_menu


def get_utc_menu_hours(store_menu_hours, store_local_timezone, start_date, end_date):
    timezones = dict()
    time_period_dates = get_timeframe_dates(start_date, end_date)
    utc_menu_hours = {}
    for store, menu in store_menu_hours.items():
        local_timezone_str = store_local_timezone.get(store, DEFAULT_TIMEZONE)
        if timezones.get(local_timezone_str):
            store_timezone = timezones.get(local_timezone_str)
        else:
            store_timezone = get_timezone(local_timezone_str)
            timezones[local_timezone_str] = store_timezone
        utc_menu_hours[store] = get_store_menu_utc(menu, store_timezone, time_period_dates)
    return utc_menu_hours


def compute_uptime_downtime(timestamp, _status, report_store, start_date, end_date, time_info):
    curr_timestamp = end_date
    last_status_timestamp = report_store['last_timestamp']
    curr_day_start = time_info['curr_day_start']
    prev_day_start = time_info['prev_day_start']
    last_hour = time_info['last_hour']
    last_hour_diff_mins = (timestamp - last_hour).days * 24 * 60
    if report_store.get('utc_menu_hours') is None:
        report_store['utc_menu_hours'] = {0: [[start_date, end_date]]}
    status_time_diff = timestamp - last_status_timestamp
    report_store['last_timestamp'] = last_status_timestamp
    status_time_diff_mins = status_time_diff.days * 24 * 60
    for k, utc_hours in report_store['utc_menu_hours'].items():
        for item in utc_hours:
            start_hour = item[0]
            end_hour = item[1]
            if (start_hour < timestamp < end_hour) and status_time_diff_mins >= 30:
                if _status == 'active':
                    report_store['uptime_last_week(in hours)'] = report_store['uptime_last_week(in hours)'] + 1
                    if curr_day_start > timestamp > prev_day_start:
                        report_store['uptime_last_day(in hours)'] = report_store['uptime_last_day(in hours)'] + 1
                        if curr_timestamp > timestamp > last_hour:
                            report_store['uptime_last_hour(in minutes)'] = report_store[
                                                                               'uptime_last_hour(in minutes)'] \
                                                                           + last_hour_diff_mins
                else:
                    report_store['downtime_last_week(in hours)'] = report_store['downtime_last_week(in hours)'] + 1
                    if curr_day_start > timestamp > prev_day_start:
                        report_store['downtime_last_day(in hours)'] = report_store['downtime_last_day(in hours)'] + 1
                        if curr_timestamp > timestamp > last_hour:
                            report_store['downtime_last_hour(in minutes)'] = report_store[
                                                                                 'downtime_last_hour(in minutes)'] \
                                                                             + last_hour_diff_mins
    store_status = report_store
    return store_status


def write_to_csv(report_dict):
    report = []
    for store, status in report_dict.items():
        status.pop('utc_menu_hours')
        status.pop('last_timestamp')
        report.append(status)
    col_names = ['store_id', 'uptime_last_hour(in minutes)', 'uptime_last_day(in hours)', 'uptime_last_week(in hours)',
                 'downtime_last_hour(in minutes)', 'downtime_last_day(in hours)', 'downtime_last_week(in hours)']
    with open('report.csv', 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=col_names)
        writer.writeheader()
        writer.writerows(report)


def get_store_report(store_status, utc_menu_hours, start_date, end_date):
    report_dict = {}
    curr_day_start = get_curr_day_start(end_date)
    prev_day_start = get_curr_day_start(get_specific_date(end_date))
    last_hour = get_specific_date(end_date)
    time_info = {
        "curr_day_start": curr_day_start,
        "prev_day_start": prev_day_start,
        "last_hour": last_hour
    }
    for item in store_status:
        if report_dict.get(item['store_id']) is None:
            report_dict[item['store_id']] = {
                "store_id": item['store_id'],
                "uptime_last_hour(in minutes)": 0,
                "uptime_last_day(in hours)": 0,
                "uptime_last_week(in hours)": 0,
                "downtime_last_hour(in minutes)": 0,
                "downtime_last_day(in hours)": 0,
                "downtime_last_week(in hours)": 0,
                "last_timestamp": start_date,
                "utc_menu_hours": utc_menu_hours.get(item['store_id'])
            }
        timestamp = get_datetime_obj(item['timestamp_utc'])
        status = compute_uptime_downtime(timestamp, item['status'], report_dict[item['store_id']],
                                         start_date, end_date, time_info)
        report_dict[item['store_id']] = status
    return report_dict
