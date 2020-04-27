
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from dateutil.rrule import rrule, MONTHLY, DAILY
from isodate.duration import Duration
from isodate import duration_isoformat
import calendar
from typing import List
import numpy as np


class DatePeriod(object):

    _VALID_PERIOD_TYPES = ["monthly", "default_week", "daily"]

    def __init__(self, tcs, tce):

        self._set_time_coverage(tcs, tce)
        self._period_type = self._get_base_period()
        
    def clip_to_range(self, range_start, range_stop):
        """ Clip the current time range to an defined time range """

        is_clipped = False

        if self._tcs_dt < range_start < self._tce_dt:
            is_clipped = True
            self._tcs_dt = range_start
        elif self._tcs_dt < range_start and self._tce_dt < range_start:
            is_clipped = True
            self._tcs_dt = None
            self._tce_dt = None

        if self._tce_dt > range_stop > self._tcs_dt:
            is_clipped = True
            self._tce_dt = range_stop
        elif self._tce_dt > range_stop and self._tcs_dt > range_stop:
            is_clipped = True
            self._tcs_dt = None
            self._tce_dt = None

        return is_clipped

    def get_id(self, dt_fmt="%Y%m%dT%H%M%S"):
        """ Returns an id of the period with customizable date format """
        return self.tcs.strftime(dt_fmt)+"_"+self.tce.strftime(dt_fmt)

    def get_period_segments(self, target_period, exclude_month=[]):
        """ Return a list of segments for the number of periods in the
        time range """

        # monthly periods: return a list of time ranges that cover the full
        # month from the first to the last month
        if target_period == "monthly":
            segments = self._get_monthly_period_segments(exclude_month)

        # default week periods: return a list of time ranges for each default
        # week definition (from Monday to Sunday)
        elif target_period == "default_week":
            segments = self._get_default_week_period_segments(exclude_month)

        # daily periods: return a list of time ranges for each day
        # in the requested period (exclude_month still applies)
        elif target_period == "daily":
            segments = self._get_daily_period_segments(exclude_month)

        # This should be caught before, but always terminate an
        # an if-elif-else
        else:
            msg = "Invalid period: %s" % str(target_period)
            raise ValueError(msg)

        return segments

    def _set_time_coverage(self, tcs, tce):
        """ Set the range of the request, tcs and stop_data can
        be either int lists (year, month, [day]) or datetime objects """

        # 1. Check if datetime objects
        valid_start, valid_stop = False, False
        if isinstance(tcs, datetime):
            tcs_full_day = datetime(tcs.year, tcs.month, tcs.day)
            self._tcs_dt = tcs_full_day
            valid_start = True
        if isinstance(tce, datetime):
            tce_full_day = datetime(tce.year, tce.month, tce.day)
            tce_full_day = tce_full_day + relativedelta(days=1, microseconds=-1)
            self._tce_dt = tce_full_day 
            valid_stop = True

        if valid_start and valid_stop:
            self._validate_range()
            return

        # 2. Check and decode integer lists
        msg_template = "invalid %s time (not integer list or datetime)"
        if isinstance(tcs, list):
            if all(isinstance(item, int) for item in tcs):
                self._tcs_dt = self._decode_int_list(tcs, "start")
            else:
                raise ValueError(msg_template)

        if isinstance(tce, list):
            if all(isinstance(item, int) for item in tce):
                self._tce_dt = self._decode_int_list(tce, "stop")
            else:
                raise ValueError(msg_template)

        # 4. Check range
        self._validate_range()



    def _validate_range(self):
        # Check if start and stop are in the right order
        if self.tce <= self.tcs:
            msg = "stop [%s] before start [%s]"
            msg = msg % (str(self.tce), str(self.tcs))
            raise ValueError(msg)

    def _get_base_period(self):
        """ Use tcs and tce to identify the period type """

        tcs, tce = self.tcs, self.tce
        duration_days = relativedelta(tce, tcs).days
        tce_next_sec = tce + relativedelta(seconds=1)

        # Test a number of conditions
        tcs_tce_same_month = tcs.year == tce.year and tcs.month == tce.month
        tcs_tce_same_day = duration_days < 1
        tcs_is_first_day_of_month = tcs.day == 1
        tce_is_last_day = tce.month != tce_next_sec.month
        tcs_is_monday = tcs.isoweekday() == 1
        tce_is_sunday = tce.isoweekday() == 7

        if tcs_tce_same_day:
            return "daily"

        if tcs_is_monday and tce_is_sunday and duration_days == 6:
            return "default_week"

        if tcs_is_first_day_of_month and tcs_tce_same_month and tce_is_last_day:
            return "monthly"

        return "custom"

    def _get_monthly_period_segments(self, exclude_month=[]):
        """ Create a list of segments with calendar monthly base period """
        # Create Iterations
        segments = []
        months = month_list(self.tcs, self.tce, exclude_month)
        n_segments = len(months)
        index = 1

        # Loop over all calendar month in the period
        for year, month in months:

            # Per default get the full month
            period_start, period_stop = get_month_time_range(year, month)

            # Clip time range to actual days for first and last iteration
            # (only if the first and the last month are not in the
            #  exclude_month list)
            first_month = self.tcs.month
            first_month_excluded = first_month in exclude_month
            if index == 1 and not first_month_excluded:
                period_start = self.tcs

            last_month = self.tce.month
            last_month_excluded = last_month in exclude_month
            if index == n_segments and not last_month_excluded:
                period_stop = self.tce

            # set final time range
            # iteration will be a of type TimeRangeIteration
            time_range = DatePeriod(period_start, period_stop)
            segments.append(time_range)
            index += 1

        return segments

    def _get_default_week_period_segments(self, exclude_month=[]):
        """ Create iterator with default_week (Monday throught Sunday)
        period """

        # Start with empty iteration
        iterations = []
        index = 1

        # Get the start date: period start date (if is monday) or previous
        # monday. If the day is not monday we can use the isoweekday
        # (monday=1, sunday=7) to compute the number days we have to subtract
        # from the start day of the period
        start_offset_days = self.tcs.isoweekday() - 1
        week_start_day = self.tcs - relativedelta(days=start_offset_days)

        # Same for the stop date: Make sure the end date either a Sunday
        # already or a Sunday after the stop date of the period
        stop_offset_days = 7 - self.tce.isoweekday()
        week_stop_day = self.tce + relativedelta(days=stop_offset_days)

        # Get the list of weeks
        weeks = weeks_list(week_start_day, week_stop_day, exclude_month)

        for start_day, stop_day in weeks:

            # weeks list provide only a
            start = datetime(start_day[0], start_day[1], start_day[2])
            stop = start + relativedelta(days=7, microseconds=-1)

            # set final time range
            # iteration will be a of type TimeRangeIteration
            time_range = DatePeriod(start, stop)
            iterations.append(time_range)
            index += 1

        return iterations

    def _get_daily_period_segments(self, exclude_month=[]):
        """ Create iterator with daily period """

        # Get list of days
        days = days_list(self.tcs, self.tce, exclude_month)
        iterations = []
        
        # Loop over days
        for year, month, day in days:

            # Start and stop are beginning/end of day
            start = datetime(year, month, day)
            stop = start + relativedelta(days=1, microseconds=-1)

            # Create the iteration
            time_range = DatePeriod(start, stop)
            iterations.append(time_range)
        
        return iterations

    @property
    def tcs(self):
        """ tcs: time coverage start as datetime object """
        return self._tcs_dt

    @property
    def tce(self):
        """ tce: time coverage end as datetime object """
        return self._tce_dt

    @property
    def label(self):
        return str(self.tcs)+" till "+str(self.tce)

    @property
    def period_type(self):
        return self._period_type

    @property
    def duration(self):
        """ Return a duration object """
        if self.period_type == "monthly":
            return Duration(months=1)
        elif self.period_type == "daily":
            return Duration(days=1)
        else:
            timedelta = relativedelta(dt1=self.tce, dt2=self.tcs)
            return Duration(years=timedelta.years, months=timedelta.months, 
                            days=timedelta.days, hours=timedelta.hours, 
                            minutes=timedelta.minutes, seconds=timedelta.seconds)

    @property
    def duration_isoformat(self):
        return duration_isoformat(self.duration)

    def __repr__(self):
        output = "Period object:\n"
        for field in ["tcs", "tce"]:
            output += "%12s: %s" % (field, getattr(self, field))
            output += "\n"
        return output


class _DateDefinition(object):
    """
    Container for a start or end date with corresponding properties, with the functionality
    to either define a date or generate from year, year+month, year+month+day lists
    """

    def __init__(self, date_def, tcs_or_tce: str):
        """
        Creates date container from various input formats. Valid date definitions are:
            1. datetime.datetime
            2. datetime.date
            3. List/tuple of integers: [year, [month], [day]]
        In case only year or only month is passed (option 3), than the date will be constructed
        based on the value of tce_or_tcs:
            - if day is omitted, the date will be set as first (tcs) or last (tce) day of the month
            - if day and month are omitted, the date will be set to the first (tcs) or last (tce)
              day of the year
        :param date_def:
        :param tcs_or_tce:
        """

        # Store args
        self._date_def = date_def
        if tcs_or_tce in self.valid_tcs_or_tce_values:
            self._tcs_or_tce = tcs_or_tce
        else:
            msg = "Invalid tce_or_tcs: {} -> must be 'tcs' or 'tce'".format(str(tcs_or_tce))
            raise ValueError(msg)

        # Init Properties
        self._year = None
        self._month = None
        self._day = None

        # Decode the input date definition and store the result in the
        # main year, month, day class properties
        self._decode_date_def()

    def _decode_date_def(self):
        """
        Decode the input date definition to this class
        :return:
        """

        # date definition is either a datetime.datetime or datetime.date,
        # -> the year, month, day properties can be simply transferred to this class
        if isinstance(self._date_def, (datetime, date)):
            year, month, day = self._date_def.year, self._date_def.month, self._date_def.day

        # date definition is a list or tuple
        # -> the list may contain year, [month], [day] with month and day may be generated
        # based on the tcs_or_tce property
        elif isinstance(self._date_def, (list, tuple)):
            year, month, day = self._decode_int_list(self._date_def, self.type)

        # date definition is neither of the previous instances
        # -> raise ValueError
        else:
            msg = "Invalid date definition: {} [datetime.datetime, datetime.date, list/tuple (yyyy, mm, dd)]"
            msg = msg.format(type(self._date_def))
            raise ValueError(msg)

    @staticmethod
    def _decode_int_list(int_list: List[int], tcs_or_tce: str):
        """ Returns a datetime object from a integer date list of type [yyyy, mm, [dd]].
        The datetime object will point to the first microsecond of the day for the
        start time (start_or_stop := "start") or the last microsecond
        """

        # Validate input
        n_entries = len(int_list)
        if n_entries < 1 or n_entries > 3:
            msg = "Invalid integer date definition: {} -> (year, [month], [day]".format(str(int_list))
            raise ValueError(msg)

        # Auto fill integer list if day or month+day are omitted
        # -> in this case the date will be either the beginning or the end of the either monthly or yearly period
        #    (based on the choice of tcs_or_tce)

        # Get the year (mandatory argument)
        year = int_list[0]

        # Get month (either list entry, or Jan for tcs and Dec for tce)
        month_defaults = {"tcs": 1, "tce": 12}
        month = month_defaults[tcs_or_tce] if n_entries == 1 else int_list[1]

        # Get the day
        # NOTE: The construction of the default day might cause an exception if the year, month numbers
        #       are invalid. This will cause an custom exception in the calendar module
        day_defaults = {"tcs": 1, "tce": calendar.monthrange(year, month)[1]}
        day = day_defaults[tcs_or_tce] if n_entries < 3 else int_list[2]

        # All variables (year, month, day) are defined at this point. This must be a valid date for datetime
        try:
            _ = datetime(year, month, day)
        except ValueError:
            msg = "Invalid date: {}, {}, {} []".format(year, month, day, tcs_or_tce)
            raise ValueError(msg)

        # All done, return the values
        return year, month, day

    @property
    def year(self):
        return int(self._year)

    @property
    def month(self):
        return int(self._month)

    @property
    def day(self):
        return int(self._day)

    @property
    def date(self):
        return date(self.year, self.month, self.day)

    @property
    def dt(self):
        """
        Return the date as datetime object. Note: if this date definition is the end of the time coverage,
        the time coverage will be extended to 23:59:59.9999 of the date
        :return:
        """
        dt = datetime(self.year, self.month, self.day)
        if self.type == "tce":
            extra_period = relativedelta(days=1, microseconds=-1)
            dt = dt + extra_period
        return dt


    @property
    def type(self):
        return str(self._tcs_or_tce)

    @property
    def is_tcs(self):
        return self.type == "tcs"

    @property
    def is_tce(self):
        return self.type == "tce"

    @property
    def valid_tcs_or_tce_values(self):
        return list(["tcs", "tce"])


def month_list(start_dt, stop_dt, exclude_month=[]):
    """ Returns a list of all month (exclude_month applies) """
    # Get an iterator for integer year and month
    month_list = month_iterator(
        start_dt.year, start_dt.month,
        stop_dt.year, stop_dt.month)
    # Filter month that are excluded from processing
    month_list = [entry for entry in month_list if (
        entry[1] not in exclude_month)]
    return month_list

def weeks_list(start_dt, stop_dt, exclude_month=[]):
    """ Returns a list of all weeks (start_dt + 7 days) in the period.
    exclude_month is applied, but partial overlap of weeks and exclude_month
    is allowed """

    weeks = []
    # Get the number of weeks (without exclude month)
    list_of_days = days_list(start_dt, stop_dt, [])
    n_weeks = np.ceil(float(len(list_of_days))/7.).astype(int)

    for i in np.arange(n_weeks):

        # Compute start and stop date for each week
        d1 = start_dt + relativedelta(days=int(i*7))
        d2 = start_dt + relativedelta(days=int((i+1)*7-1))

        # exclude month only applies when both start and stop day of the week
        # are in an excluded month (partial overlap is allowed)
        if d1.month in exclude_month and d2.month in exclude_month:
            continue

        # store start and stop day for each week
        weeks.append([[d1.year, d1.month, d1.day],
                      [d2.year, d2.month, d2.day]])

    return weeks


def days_list(start_dt, stop_dt, exclude_month=[]):
    """ Returns a list of all days (exclude_month applies) """
    days = []
    months = month_list(start_dt, stop_dt, exclude_month)
    n_month = len(months)
    start_day, stop_day = start_dt.day, stop_dt.day
    for i, month in enumerate(months):
        # List of all days in given month
        monthly_days = days_iterator(*month)
        # Clip potential omitted days in the start request
        if i == 0:
            monthly_days = [d for d in monthly_days if d[2] >= start_day]
        # Clip potential omitted days in the stop request
        if i == n_month-1:
            monthly_days = [d for d in monthly_days if d[2] <= stop_day]
        days.extend(monthly_days)
    return days


def month_iterator(start_year, start_month, end_year, end_month):
    """ returns an iterator over months """
    start = datetime(start_year, start_month, 1)
    end = datetime(end_year, end_month, 1)
    return [(d.year, d.month) for d in rrule(MONTHLY, dtstart=start, until=end)]


def days_iterator(year, month):
    """ returns an iterator over all days in given month """
    all_days = calendar.monthrange(year, month)
    start = datetime(year, month, 1)
    end = datetime(year, month, all_days[-1])
    return [(d.year, d.month, d.day) for d in rrule(DAILY, dtstart=start, until=end)]


def get_month_time_range(year, month):
    """ Returns the a start and stop datetime object for a given month """
    start_dt = datetime(year, month, 1)
    stop_dt = start_dt + relativedelta(months=1, microseconds=-1)
    return start_dt, stop_dt
