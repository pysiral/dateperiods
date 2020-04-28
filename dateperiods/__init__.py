
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from dateutil.rrule import rrule, MONTHLY, DAILY
from isodate.duration import Duration
from isodate import duration_isoformat
import calendar
from typing import List
import numpy as np


class DatePeriod(object):
    """
    Container for managing periods of dates and their segmentation into sub-periods
    """

    def __init__(self, tcs_def, tce_def):
        """
        Establish a period defined by the start (tcs) and end (tce) of the time coverage.
        The start and end time can be specified with the following tpyes:

            1) datetime.datetime
            2) datetime.date
            3) List/tuple of integers: [year, [month], [day]]

        In case of option 3, the values for either (a) day or (b) month+day can be omitted and will be
        automatically completed to the beginning, respective end of the month (a) or year (b).

        :param tcs_def: The definition for the start of the time coverage.
        :param tce_def: The definition for the end of the time coverage.
        """

        # Process the input date definitions
        self._tcs = _DateDefinition(tcs_def, "tcs")
        self._tce = _DateDefinition(tce_def, "tce")

        # Make sure the period is valid, e.g. that start is before ends
        if self._tce.dt < self._tcs.dt:
            msg = "stop [%s] before end [%s]"
            msg = msg % (str(self.tce.dt), str(self.tcs.dt))
            raise ValueError(msg)

        # Init the duration property
        self._duration = _DateDuration(self.tcs, self.tce)

    def clip(self, start=None, end=None):
        """
        Clip
        :param start:
        :param end:
        :return:
        """
        """ Clip the current time range to an defined time range """
        pass

        # is_clipped = False
        #
        # if self._tcs_dt < range_start < self._tce_dt:
        #     is_clipped = True
        #     self._tcs_dt = range_start
        # elif self._tcs_dt < range_start and self._tce_dt < range_start:
        #     is_clipped = True
        #     self._tcs_dt = None
        #     self._tce_dt = None
        #
        # if self._tce_dt > range_stop > self._tcs_dt:
        #     is_clipped = True
        #     self._tce_dt = range_stop
        # elif self._tce_dt > range_stop and self._tcs_dt > range_stop:
        #     is_clipped = True
        #     self._tcs_dt = None
        #     self._tce_dt = None
        #
        # return is_clipped

    def get_id(self, dt_fmt="%Y%m%dT%H%M%S"):
        """
        Returns an id of the period with customizable date format
        :param dt_fmt: 
        :return: 
        """
        return self.tcs.dt.strftime(dt_fmt)+"_"+self.tce.dt.strftime(dt_fmt)

    def get_segments(self, duration_type: str, **filter_kwargs):
        """
        Return an iterator that divides the period into the segments with the specified duration.
        The iterations will be of type DatePeriod. If a duration is longer than the duration of the
        base period, the iterator will contain the iterations of the base period where this period will
        intersect.

        In addition, the resulting iterator can be filtered, according to the filter rules of the
        PeriodIterator class

        :param duration_type:
        :param filter_kwargs:
        :return: 
        """

        # NOTE: Sanity Check of input args will be done in the PeriodIterator instance
        prditer = PeriodIterator(self, duration_type)
        return prditer

    def get_netcdf_attributes(self, zulu=True):
        """
        Get a dictionary with standard netCDF attributes for a period

        time_coverage_start: 20120131T070000Z
        time_coverage_end: 20120131T083000Z
        time_coverage_duration: P1Y
        time_coverage_resolution: P1D

        :param zulu: bool: If true (default) the datetime str will contain a `Z` timezone indicator

        :return: dict
        """
        dt_fmt = "%Y%m%dT%H%M%S"
        if zulu:
            dt_fmt = dt_fmt + "Z"
        ncattrs = dict(time_coverage_start=self.tcs.dt.strftime(dt_fmt),
                       time_coverage_end=self.tce.dt.strftime(dt_fmt),
                       time_coverage_duration=self.duration.isoformat,
                       time_coverage_resolution=self.duration.isoformat)
        return ncattrs

        # # monthly periods: return a list of time ranges that cover the full
        # # month from the first to the last month
        # if target_period == "monthly":
        #     segments = self._get_monthly_period_segments(exclude_month)
        #
        # # default week periods: return a list of time ranges for each default
        # # week definition (from Monday to Sunday)
        # elif target_period == "default_week":
        #     segments = self._get_default_week_period_segments(exclude_month)
        #
        # # daily periods: return a list of time ranges for each day
        # # in the requested period (exclude_month still applies)
        # elif target_period == "daily":
        #     segments = self._get_daily_period_segments(exclude_month)
        #
        # # This should be caught before, but always terminate an
        # # an if-elif-else
        # else:
        #     msg = "Invalid period: %s" % str(target_period)
        #     raise ValueError(msg)
        #
        # return segments

    # def _get_base_period(self):
    #     """ Use tcs and tce to identify the period type """
    #     # Test a number of conditions
    #
    #
    #     tcs_tce_same_month = self.tcs.year == self.tce.year and self.tcs.month == self.tce.month
    #
    #     # Same dates (period duration is daily)
    #     tcs_tce_same_day = self.tcs.date == self.tce.date
    #     if tcs_tce_same_day:
    #         return "daily"
    #
    #     if self.tcs.is_monday and self.tce.is_sunday and duration_days == 6:
    #         return "default_week"
    #
    #     if tcs_is_first_day_of_month and tcs_tce_same_month and tce_is_last_day:
    #         return "monthly"
    #
    #     return "custom"

    # def _get_monthly_period_segments(self, exclude_month=[]):
    #     """ Create a list of segments with calendar monthly base period """
    #     # Create Iterations
    #     segments = []
    #     months = month_list(self.tcs, self.tce, exclude_month)
    #     n_segments = len(months)
    #     index = 1
    #
    #     # Loop over all calendar month in the period
    #     for year, month in months:
    #
    #         # Per default get the full month
    #         period_start, period_stop = get_month_time_range(year, month)
    #
    #         # Clip time range to actual days for first and last iteration
    #         # (only if the first and the last month are not in the
    #         #  exclude_month list)
    #         first_month = self.tcs.month
    #         first_month_excluded = first_month in exclude_month
    #         if index == 1 and not first_month_excluded:
    #             period_start = self.tcs
    #
    #         last_month = self.tce.month
    #         last_month_excluded = last_month in exclude_month
    #         if index == n_segments and not last_month_excluded:
    #             period_stop = self.tce
    #
    #         # set final time range
    #         # iteration will be a of type TimeRangeIteration
    #         time_range = DatePeriod(period_start, period_stop)
    #         segments.append(time_range)
    #         index += 1
    #
    #     return segments
    #
    # def _get_default_week_period_segments(self, exclude_month=[]):
    #     """ Create iterator with default_week (Monday throught Sunday)
    #     period """
    #
    #     # Start with empty iteration
    #     iterations = []
    #     index = 1
    #
    #     # Get the start date: period start date (if is monday) or previous
    #     # monday. If the day is not monday we can use the isoweekday
    #     # (monday=1, sunday=7) to compute the number days we have to subtract
    #     # from the start day of the period
    #     start_offset_days = self.tcs.dt.isoweekday() - 1
    #     week_start_day = self.tcs.dt - relativedelta(days=start_offset_days)
    #
    #     # Same for the stop date: Make sure the end date either a Sunday
    #     # already or a Sunday after the stop date of the period
    #     stop_offset_days = 7 - self.tce.dt.isoweekday()
    #     week_stop_day = self.tce.dt + relativedelta(days=stop_offset_days)
    #
    #     # Get the list of weeks
    #     weeks = weeks_list(week_start_day, week_stop_day, exclude_month)
    #
    #     for start_day, stop_day in weeks:
    #
    #         # weeks list provide only a
    #         start = datetime(start_day[0], start_day[1], start_day[2])
    #         stop = start + relativedelta(days=7, microseconds=-1)
    #
    #         # set final time range
    #         # iteration will be a of type TimeRangeIteration
    #         time_range = DatePeriod(start, stop)
    #         iterations.append(time_range)
    #         index += 1
    #
    #     return iterations
    #
    # def _get_daily_period_segments(self, exclude_month=[]):
    #     """ Create iterator with daily period """
    #
    #     # Get list of days
    #     days = days_list(self.tcs, self.tce, exclude_month)
    #     iterations = []
    #
    #     # Loop over days
    #     for year, month, day in days:
    #
    #         # Start and stop are beginning/end of day
    #         start = datetime(year, month, day)
    #         stop = start + relativedelta(days=1, microseconds=-1)
    #
    #         # Create the iteration
    #         time_range = DatePeriod(start, stop)
    #         iterations.append(time_range)
    #
    #     return iterations

    @property
    def tcs(self):
        """ tcs: time coverage start as datetime object """
        return self._tcs

    @property
    def tce(self):
        """ tce: time coverage end as datetime object """
        return self._tce

    @property
    def duration(self):
        return self._duration

    @property
    def label(self):
        return str(self.tcs.dt)+" till "+str(self.tce.dt)

    # @property
    # def period_type(self):
    #     return self._period_type

    # @property
    # def duration(self):
    #     """ Return a duration object """
    #     if self.period_type == "monthly":
    #         return Duration(months=1)
    #     elif self.period_type == "daily":
    #         return Duration(days=1)
    #     else:
    #         tdelta = relativedelta(dt1=self.tce.dt, dt2=self.tcs.dt)
    #         return Duration(years=tdelta.years, months=tdelta.months,
    #                         days=tdelta.days, hours=tdelta.hours,
    #                         minutes=tdelta.minutes, seconds=tdelta.seconds)
    #
    # @property
    # def duration_isoformat(self):
    #     return duration_isoformat(self.duration)

    def __repr__(self):
        output = "DatePeriod:\n"
        for field in ["tcs", "tce"]:
            output += "%12s: %s" % (field, getattr(self, field))
            output += "\n"
        return output


class PeriodIterator(object):
    """
    Class that allows to segment a period into subset periods of a given duration. The class then can be used
    as an iterator, but also filtered after initial segmentation
    """

    def __init__(self, base_period: DatePeriod, segment_duration: str):
        """
        Create an iterator over a segmented of a base period with a given duration
        :param base_period:
        :param segment_duration:
        """

        # Store args
        self.base_period = base_period
        if segment_duration not in self.valid_segment_duration:
            msg = "Invalid segment duration: {} [{}]"
            msg = msg.format(segment_duration, ",".join(self.valid_segment_duration))
            raise ValueError(msg)
        self.segment_duration = segment_duration

        # Construct the list of periods
        self._segment_list = []
        self._get_segment_list()

    def _get_segment_list(self):
    def __iter__(self):
        """
        Mandatory iteration init method
        :return:
        """

        self.index = 0
        return self

    def __next__(self):
        """
        Mandatory iteration method
        :return:
        """
        index = int(self.index)
        if index > self.n_periods - 1:
            raise StopIteration
        self.index += 1
        return self._segment_list[index]

        # Dictionary of methods that will be called to get a list of tcs/tce's for each segment
        # based on the choice of segment_duration
        funcs = dict(day=self.get_days, isoweek=self.get_isoweeks, month=self.get_months)
        base_tcs, base_tce = self.base_period.tcs.dt, self.base_period.tce.dt
        for period_def in funcs[self.segment_duration](base_tcs, base_tce):
            self._segment_list.append(DatePeriod(period_def, period_def))

    @staticmethod
    def days_list(year, month):
        """ returns an iterator over all days in given month """
        all_days = calendar.monthrange(year, month)
        start = datetime(year, month, 1)
        end = datetime(year, month, all_days[-1])
        return [(d.year, d.month, d.day) for d in rrule(DAILY, dtstart=start, until=end)]

    @staticmethod
    def months_list(start_year, start_month, end_year, end_month):
        """ returns an iterator over months """
        start = datetime(start_year, start_month, 1)
        end = datetime(end_year, end_month, 1)
        return [(d.year, d.month) for d in rrule(MONTHLY, dtstart=start, until=end)]

    @classmethod
    def get_days(cls, start_dt, end_dt):
        """ Returns a list of all days (exclude_month applies) """
        days = []
        months = cls.get_months(start_dt, end_dt)
        n_month = len(months)
        start_day, stop_day = start_dt.day, end_dt.day
        for i, month in enumerate(months):
            # List of all days in given month
            monthly_days = cls.days_list(*month)
            # Clip potential omitted days in the start request
            if i == 0:
                monthly_days = [d for d in monthly_days if d[2] >= start_day]
            # Clip potential omitted days in the stop request
            if i == n_month - 1:
                monthly_days = [d for d in monthly_days if d[2] <= stop_day]
            days.extend(monthly_days)
        return days

    @classmethod
    def get_isoweeks(cls, start_dt, end_dt):
        """ Returns a list of all weeks (start_dt + 7 days) in the period.
        exclude_month is applied, but partial overlap of weeks and exclude_month
        is allowed """

        weeks = []
        # Get the number of weeks (without exclude month)
        list_of_days = cls.get_days(start_dt, end_dt)
        n_weeks = np.ceil(float(len(list_of_days)) / 7.).astype(int)

        for i in np.arange(n_weeks):

            # Compute start and stop date for each week
            d1 = start_dt + relativedelta(days=int(i * 7))
            d2 = start_dt + relativedelta(days=int((i + 1) * 7 - 1))

            # store start and stop day for each week
            weeks.append([[d1.year, d1.month, d1.day], [d2.year, d2.month, d2.day]])

        return weeks

    @classmethod
    def get_months(cls, start_dt, end_dt):
        """ Returns a list of all month (exclude_month applies) """
        # Get an iterator for integer year and month
        months = cls.months_list(start_dt.year, start_dt.month, end_dt.year, end_dt.month)
        return months

    @property
    def valid_segment_duration(self):
        return ["month", "isoweek", "day"]

    @property
    def n_periods(self):
        return len(self._segment_list)


class _DateDefinition(object):
    """
    Container for a start or end date with corresponding properties, with the functionality
    to either define a date or generate from year, year+month, year+month+day lists
    """

    def __init__(self, date_def, tcs_or_tce: str) -> None:
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

        # All done, safe properties
        self._year = year
        self._month = month
        self._day = day

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
        """
        The year as integer number
        :return: int
        """
        return int(self._year)

    @property
    def month(self):
        """
        The month as integer number
        :return: int
        """
        return int(self._month)

    @property
    def day(self):
        """
        The day as integer number
        :return: int
        """
        return int(self._day)

    @property
    def date(self):
        """
        The date definition as datetime.date
        :return: datetime.date
        """
        return date(self.year, self.month, self.day)

    @property
    def dt(self):
        """
        The date as datetime object. Note: if this date definition is the end of the time coverage,
        the time coverage will be extended to 23:59:59.9999 of the date
        :return: datetime.datetime
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
        """
        Flag if the date definition is marked as the beginning of the time coverage
        :return: bool
        """
        return self.type == "tcs"

    @property
    def is_tce(self):
        """
        Flag if the date definition is marked as the end of the time coverage
        :return: bool
        """
        return self.type == "tce"

    @property
    def is_monday(self):
        """
        Flag if the current day is a Monday
        :return: bool
        """
        return self.dt.isoweekday() == 1

    @property
    def is_sunday(self):
        """
        Flag if the current day is a Sunday
        :return: bool
        """
        return self.dt.isoweekday() == 7

    @property
    def is_last_day_of_month(self):
        """
        Flag if the current day is the last day in a month
        :return: bool
        """
        next_date = self.dt + relativedelta(days=1)
        return self.dt.month != next_date.month

    @property
    def valid_tcs_or_tce_values(self):
        """
        The valid tags for time coverage start and time coverage end
        :return: str list
        """
        return list(["tcs", "tce"])


class _DateDuration(object):
    """
    Container for duration parameters of the period between two dates
    """

    def __init__(self, tcs: _DateDefinition, tce: _DateDefinition):
        """
        Compute the duration between two dates
        :param tcs: _DateDefinition
        :param tce: _DateDefinition
        """

        # Basic sanity check
        if tce.dt <= tcs.dt:
            raise ValueError("End {} <= Start {}".format(tcs, tce))

        # Arguments
        self._tcs = tcs
        self._tce = tce

    @property
    def tcs(self):
        return self._tcs

    @property
    def tce(self):
        return self._tce

    @property
    def total_seconds(self):
        """
        The number of seconds
        :return: int
        """
        return (self.tce.dt-self.tcs.dt).total_seconds()

    @property
    def total_days(self):
        """
        Number of days between start and end (1 if both are the same day)
        :return: int
        """
        return relativedelta(self.tce.dt, self.tcs.dt).days + 1

    @property
    def is_day(self):
        """
        Flag if the period is a full month
        :return: bool
        """
        return self.tcs.date == self.tce.date

    @property
    def is_isoweek(self):
        """
        Flag if period is a default week (Monday to following Sunday)
        :return:
        """
        return self.tcs.is_monday and self.tce.is_sunday and self.total_days == 7

    @property
    def is_month(self):
        """
        Compute flag if the period is a full month
        :return: bool
        """

        # Must be same month
        condition1 = [self.tcs.dt.year, self.tcs.dt.month] == [self.tce.dt.year, self.tce.dt.month]

        # Start must be first day of month
        condition2 = self.tcs.day == 1

        # Stop must be last day of month
        condition3 = self.tce.is_last_day_of_month

        return condition1 and condition2 and condition3

    @property
    def is_year(self):
        """
        Compute flag if the period is a full year
        :return: bool
        """

        # Must be same month
        condition1 = [self.tcs.month, self.tcs.day] == [1, 1]

        # Start must be first day of month
        condition2 = [self.tce.month, self.tce.day] == [12, 31]

        # Stop must be last day of month
        condition3 = self.tcs.year == self.tce.year

        return condition1 and condition2 and condition3

    @property
    def duration(self):
        """
        Return a duration
        :return:
        """
        """ Return a duration object """
        if self.is_day:
            return Duration(days=1)
        elif self.is_month:
            return Duration(months=1)
        elif self.is_year:
            return Duration(years=1)
        else:
            tdelta = relativedelta(dt1=self.tce.dt, dt2=self.tcs.dt)
            return Duration(years=tdelta.years, months=tdelta.months,
                            days=tdelta.days, hours=tdelta.hours,
                            minutes=tdelta.minutes, seconds=tdelta.seconds+1)

    @property
    def isoformat(self):
        return duration_isoformat(self.duration)

    @property
    def type(self):
        """
        Return a classifier that indicates the period duration type
        (e.g. year, month, isoweek, day, custom)
        :return: str
        """

        if self.is_year:
            return "year"

        if self.is_month:
            return "month"

        if self.is_isoweek:
            return "isoweek"

        if self.is_day:
            return "day"

        return "custom"