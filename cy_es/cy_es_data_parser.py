import datetime
import re
def try_parse_date(str_date):
    if not isinstance(str_date, str):
        return None, False

    if not isinstance(str_date, str) or '+' not in str_date and str_date.__len__() >= 27:
        try:
            t = datetime.datetime.strptime(str_date[0:26] + 'Z', '%Y-%m-%dT%H:%M:%S.%fZ')

            return t, True
        except Exception as e:
            return None, False
    str_date_time = str_date.split('+')[0]
    try:
        t = datetime.datetime.strptime(str_date_time, '%Y-%m-%dT%H:%M:%S.%f')
        tz = datetime.datetime.strptime(str_date.split('+')[1], "%H:%M")
        ret = t + datetime.timedelta(tz.hour)
        return ret, True
    except Exception as e:

        pattern_full = re.compile("^([0-9]{4})-([0-9]{2})-([0-9]{2}):([0-9]{2}):([0-9]{2}):([0-9]{2})$")
        pattern_full_2 = re.compile("^([0-9]{4})\/([0-9]{2})\/([0-9]{2}):([0-9]{2}):([0-9]{2}):([0-9]{2})$")
        pattern_full_3 = re.compile("^([0-9]{4})-([0-9]{2})-([0-9]{2})T([0-9]{2}):([0-9]{2}):([0-9]{2})$")
        pattern_full_4 = re.compile("^([0-9]{4})\/([0-9]{2})\/([0-9]{2})T([0-9]{2}):([0-9]{2}):([0-9]{2})$")
        pattern_full_5 = re.compile(
            "^([0-9]{4})-([0-9]{2})-([0-9]{2})T([0-9]{2}):([0-9]{2}):([0-9]{2})\+([0-9]{2}):([0-9]{2})$")
        """2023-10-27T00:00:00+07:00"""
        pattern_full_6 = re.compile(
            "^([0-9]{4})-([0-9]{2})-([0-9]{2})T([0-9]{2}):([0-9]{2}):([0-9]{2})\-([0-9]{2}):([0-9]{2})$")
        """2023-10-27T00:00:00-07:00"""
        pattern_full_7 = re.compile(
            "^([0-9]{4})-([0-9]{2})-([0-9]{2})T([0-9]{2}):([0-9]{2}):([0-9]{2})Z$")
        """2023-10-25T17:00:00Z"""
        pattern = re.compile("^([0-9]{4})-([0-9]{2})-([0-9]{2})$")
        pattern_1 = re.compile("^([0-9]{4})\/([0-9]{2})\/([0-9]{2})$")

        years = -1
        months = -1
        days = -1
        hours = 0
        minutes = 0
        seconds = 0

        if pattern_full.match(str_date):
            str_date_only = str_date[:str_date.index(":")]
            str_time_only = str_date[str_date.index(":") + 1:]
            years = int(str_date_only.split('-')[0])
            months = int(str_date_only.split('-')[1])
            days = int(str_date_only.split('-')[2])
            hours = int(str_time_only.split(':')[0])
            minutes = int(str_time_only.split(':')[1])
            seconds = int(str_time_only.split(':')[2])
        elif pattern_full_2.match(str_date):
            str_date_only = str_date[:str_date.index(":")]
            str_time_only = str_date[str_date.index(":") + 1:]
            years = int(str_date_only.split('/')[0])
            months = int(str_date_only.split('/')[1])
            days = int(str_date_only.split('/')[2])
            hours = int(str_time_only.split(':')[0])
            minutes = int(str_time_only.split(':')[1])
            seconds = int(str_time_only.split(':')[2])
        elif pattern_full_3.match(str_date):
            str_date_only = str_date[:str_date.index("T")]
            str_time_only = str_date[str_date.index("T") + 1:]
            years = int(str_date_only.split('-')[0])
            months = int(str_date_only.split('-')[1])
            days = int(str_date_only.split('-')[2])
            hours = int(str_time_only.split(':')[0])
            minutes = int(str_time_only.split(':')[1])
            seconds = int(str_time_only.split(':')[2])
        elif pattern_full_4.match(str_date):
            str_date_only = str_date[:str_date.index("T")]
            str_time_only = str_date[str_date.index("T") + 1:]
            years = int(str_date_only.split('/')[0])
            months = int(str_date_only.split('/')[1])
            days = int(str_date_only.split('/')[2])
            hours = int(str_time_only.split(':')[0])
            minutes = int(str_time_only.split(':')[1])
            seconds = int(str_time_only.split(':')[2])
        elif pattern_full_5.match(str_date):
            str_date_only = str_date[:str_date.index("T")]
            str_time_only = str_date[str_date.index("T") + 1:]
            str_offset_time_only = str_time_only[str_time_only.index("+") + 1:]
            str_time_only = str_time_only[:str_time_only.index("+")]
            years = int(str_date_only.split('-')[0])
            months = int(str_date_only.split('-')[1])
            days = int(str_date_only.split('-')[2])
            hours = int(str_time_only.split(':')[0])
            minutes = int(str_time_only.split(':')[1])
            seconds = int(str_time_only.split(':')[2])
            offset_hours = int(str_offset_time_only.split(":")[0])
            offset_minutes = int(str_offset_time_only.split(":")[1])
            hours = hours + offset_hours
            minutes = minutes + offset_minutes
        elif pattern_full_6.match(str_date):
            str_date_only = str_date[:str_date.index("T")]
            str_time_only = str_date[str_date.index("T") + 1:]
            str_offset_time_only = str_time_only[str_time_only.index("-") + 1:]
            str_time_only = str_time_only[:str_time_only.index("-")]
            years = int(str_date_only.split('-')[0])
            months = int(str_date_only.split('-')[1])
            days = int(str_date_only.split('-')[2])
            hours = int(str_time_only.split(':')[0])
            minutes = int(str_time_only.split(':')[1])
            seconds = int(str_time_only.split(':')[2])
            offset_hours = int(str_offset_time_only.split(":")[0])
            offset_minutes = int(str_offset_time_only.split(":")[1])
            hours = hours + offset_hours
            minutes = minutes + offset_minutes
        elif pattern_full_7.match(str_date):
            str_date_only = str_date[:str_date.index("T")]
            str_time_only = str_date[str_date.index("T") + 1:-1]
            years = int(str_date_only.split('-')[0])
            months = int(str_date_only.split('-')[1])
            days = int(str_date_only.split('-')[2])
            hours = int(str_time_only.split(':')[0])
            minutes = int(str_time_only.split(':')[1])
            seconds = int(str_time_only.split(':')[2])

        elif pattern.match(str_date):
            str_date_only = str_date
            years = int(str_date_only.split('-')[0])
            months = int(str_date_only.split('-')[1])
            days = int(str_date_only.split('-')[2])
        elif pattern_1.match(str_date):
            str_date_only = str_date
            years = int(str_date_only.split('/')[0])
            months = int(str_date_only.split('/')[1])
            days = int(str_date_only.split('/')[2])
        if years > -1:
            return datetime.datetime(year=years, month=months, day=days, hour=hours, minute=minutes,
                                     second=seconds), True

        return None, False