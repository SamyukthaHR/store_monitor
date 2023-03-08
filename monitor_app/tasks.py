import json
from datetime import datetime

from monitor_app.models import AppConstants, StoreStatus, StoreMenuHours, StoreTimezone, ReportDetails
from monitor_app.serializer import AppConstantsSerializer, StoreStatusSerializer, StoreMenuHoursSerializer, \
    StoreTimezoneSerializer
from store_monitor.celery import app
from utils.aws import upload_to_s3
from utils.constants import FAILED, PROCESSING, DONE
from utils.util import get_const_data, get_datetime_obj, format_serializer_data, get_list_of_tuples_to_list, \
    time_frame_dates, get_curr_timestamp_utc, get_store_menu_data, get_local_timezone_data, \
    get_utc_menu_hours, get_store_report, write_to_csv


def get_constants():
    const_qs = AppConstants.objects.all()
    data_s = (AppConstantsSerializer(const_qs, many=True)).data
    const_data = json.loads(json.dumps(data_s))
    const_key_val = get_const_data(const_data)
    return const_key_val


def get_latest_store_status(start_date, end_date, store_id=None):
    if store_id:
        store_status_qs = StoreStatus.objects.filter(timestamp_utc__range=(start_date, end_date),
                                                     store_id=store_id).order_by('timestamp_utc')
        store_ids = [store_id]
    else:
        store_status_qs = StoreStatus.objects.filter(timestamp_utc__range=(start_date,
                                                                           end_date)).order_by('timestamp_utc')
        store_ids_qs = store_status_qs.order_by().values_list('store_id').distinct()
        store_ids = get_list_of_tuples_to_list(list(store_ids_qs))
    store_status_s = StoreStatusSerializer(store_status_qs, many=True)
    store_status_data = format_serializer_data(store_status_s.data)
    return store_status_data, store_ids


def get_local_menu_hours(store_ids):
    menu_hours_week_qs = StoreMenuHours.objects.filter(store_id__in=store_ids).order_by('day')
    menu_hours_week_s = StoreMenuHoursSerializer(menu_hours_week_qs, many=True)
    menu_hours_week_data = format_serializer_data(menu_hours_week_s.data)
    store_menu_data = get_store_menu_data(menu_hours_week_data)
    return store_menu_data


def get_store_timezone(store_ids):
    store_timezone_qs = StoreTimezone.objects.filter(store_id__in=store_ids)
    store_timezone_s = StoreTimezoneSerializer(store_timezone_qs, many=True)
    store_timezone_data = format_serializer_data(store_timezone_s.data)
    local_timezone_data = get_local_timezone_data(store_timezone_data)
    return local_timezone_data


def update_report_status(report_id, report_status, report_url=None, err_msg=None):
    try:
        report = ReportDetails.objects.get(report_id=report_id)
        report.status = report_status
        report.report_url = report_url
        report.err_msg = err_msg
        report.updated_at = get_curr_timestamp_utc()
        report.save()
    except Exception as e:
        print(f"Exception due to {e}")
        raise e


@app.task
def trigger_report(body, report_id):
    try:
        report_status = PROCESSING
        update_report_status(report_id, report_status)
        curr_timestamp = get_curr_timestamp_utc()
        constants_data = get_constants()
        if int(constants_data.get('test', 0)):
            curr_timestamp = get_datetime_obj(constants_data['curr_timestamp_utc'])
        no_of_weeks = body.get('no_of_weeks', int(constants_data.get('no_of_weeks', 1)))
        store_id = body.get('store_id')
        start_date, end_date = time_frame_dates(curr_timestamp, no_of_weeks)
        store_status_res, store_ids = get_latest_store_status(start_date, end_date, store_id=store_id)
        store_menu_hours = get_local_menu_hours(store_ids)
        store_local_timezone = get_store_timezone(store_ids)
        utc_menu_hours = get_utc_menu_hours(store_menu_hours, store_local_timezone, start_date, end_date)
        report_dict = get_store_report(store_status_res, utc_menu_hours, start_date, end_date)
        write_to_csv(report_dict)
        file_name = str(datetime.now())
        report_url = upload_to_s3(file_name)
        report_status = FAILED if report_url is None else DONE
        update_report_status(report_id, report_status, report_url=report_url)
    except Exception as e:
        print("Exception in outer")
        report_status = FAILED
        update_report_status(report_id, report_status, err_msg=str(e))
