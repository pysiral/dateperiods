# -*- coding: utf-8 -*-

"""

"""

import calendar
from typing import Dict, List, Tuple, Union, Optional

import re
import copy
from enum import StrEnum
import cftime
import numpy as np

from typing import Literal

from datetime import date, datetime, timedelta

from dateutil.relativedelta import relativedelta
from dateutil.rrule import DAILY, MONTHLY, YEARLY, rrule
from isodate import duration_isoformat
from isodate.duration import Duration

# Package Metadata
__version__ = "1.4.0"
__author__ = "Stefan Hendricks"
__author_email__ = "stefan.hendricks@awi.de"

# Imports
__all__ = ["DatePeriod", "PeriodIterator", "DateDefinition", "DateDuration"]


class DateDurationType(StrEnum):
    YEAR = "P1Y"
    MONTH = "P1M"
    ISOWEEK = "ISOWEEK"
    DAY = "P1D"
    YEARLY = "P1Y"
    MONTHLY = "P1M"
    ISOWEEKLY = "ISOWEEK"
    DAILY = "P1D"
    P1Y = "P1Y"
    P7D = "P7D"
    P1M = "P1M"
    P1D = "P1D"



class ExcludeRuleNotSet(object):
    """
    Default
    """

    def __init__(self) -> None:
        pass

    def __contains__(self, dt: datetime) -> Literal[False]:
        return False

    def __repr__(self) -> str:
        return "Exclude Rule Not Set"


class ExcludeMonth(object):
    """
    Rule to exclude certain months from the period iterator.

    Usage:

    >>> exclude_rule = ExcludeMonth([5, 6, 7, 8, 9])
    >>> datetime(2015, 6, 10) in exclude_rule
    True

    :param months: Month number of list of month numbers to exclude
        from iterator

    :raises ValueError: Invalid month number input
    """

    def __init__(self, months: Union[int, List[int]]) -> None:
        months = sorted(months) if isinstance(months, list) else [months]
        invalid_input = any(m not in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12] for m in months)
        if invalid_input:
            raise ValueError(f"input does contain invalid month number: {months} [1, ..., 12]")
        self.months = months

    def __contains__(self, dt: datetime) -> bool:
        return dt.month in self.months

    def __repr__(self) -> str:
        return f"ExcludeMonths: {self.months}"


class DatePeriod(object):
    """
    Container for managing periods of dates and their segmentation into sub-periods
    """

    def __init__(
        self,
        tcs_def: Union[List[int], str, "datetime", "date"],
        tce_def: Union[List[int], str, "datetime", "date"] = None,
        exclude_rule: Optional[ExcludeMonth] = None,
        unit: Optional[str] = None,
        calendar_name: Optional[str] = None
    ) -> None:
        """
        Establish a period defined by the start (tcs) and end (tce) of the time coverage.
        The start and end time can be specified with the following tpyes:

            1) `datetime.datetime`
            2) `datetime.date`
            3) List/tuple of integers: [year, [month], [day]]

        In case of option 3, the values for either (a) day or (b) month+day can be omitted and will be
        automatically completed to the beginning, respective end of the month (a) or year (b).

        :param tcs_def: The definition for the start of the time coverage.
        :param tce_def: The definition for the end of the time coverage.

        :param unit:
        :param calendar_name:
        """

        # Process the input date definitions
        self._unit = unit if unit is not None else "seconds since 1970-01-01"
        self._calendar = calendar_name if calendar_name is not None else "standard"
        self.exclude_rule = exclude_rule if isinstance(exclude_rule, ExcludeMonth) else ExcludeRuleNotSet()
        # if time coverage end is omitted, use time coverage start as the definition
        # of the period.
        if tce_def is None:
            tce_def = copy.copy(tcs_def)

        self._tcs = DateDefinition(tcs_def, "tcs", unit=self._unit, calendar_name=self._calendar)
        self._tce = DateDefinition(tce_def, "tce", unit=self._unit, calendar_name=self._calendar)

        # Make sure the period is valid, e.g. that start is before ends
        if self._tce.dt < self._tcs.dt:
            msg = "stop [%s] before end [%s]"
            msg %= (str(self.tce.dt), str(self.tcs.dt))
            raise ValueError(msg)

        # Init the duration property
        self._duration = DateDuration(self.tcs, self.tce)

    def get_id(self, dt_fmt: str = "%Y%m%dT%H%M%S") -> str:
        """
        Returns an id of the period with customizable date format
        :param dt_fmt:
        :return:
        """
        return f"{self.tcs.dt.strftime(dt_fmt)}_{self.tce.dt.strftime(dt_fmt)}"

    def get_segments(self, duration_type: str, crop_to_period: bool = False) -> "PeriodIterator":
        """
        Return an iterator that divides the period into the segments with the specified duration.
        The iterations will be of type DatePeriod. If a duration is longer than the duration of the
        base period, the iterator will contain the iterations of the base period where this period will
        intersect.

        In addition, the resulting iterator can be filtered, according to the filter rules of the
        PeriodIterator class

        :param duration_type:
        :param crop_to_period:
        :return:
        """

        # Input validation
        if not isinstance(crop_to_period, bool):
            msg = f"Keyword `limit_to_period` must be `True`or `False` (bool), was {crop_to_period}"
            raise ValueError(msg)

        if not isinstance(duration_type, str):
            msg = f"duration_type must be of type str, was {type(duration_type)}"
            raise ValueError(msg)

        # NOTE: Sanity Check of input args will be done in the PeriodIterator instance
        prditer = PeriodIterator(self, duration_type.upper())

        # Crop to the period of this instance. This means practically to limit the
        # duration of the iterator segments to the start and end date of this
        # DatePeriod instance.
        # E.g. if the duration of this period is from the middle of one month to the
        # middle of the next, PeriodIterator will have two segments that cover both full
        # month. Cropping the Iterator will result in the first segment to run from
        # the middle to the end of the first month and the seconds item from the beginning
        # to the middle of the second month.
        # This functionality is handled in PeriodIterator.
        if crop_to_period:
            prditer.crop_to_period(self)

        return prditer

    def get_netcdf_attributes(self, zulu: bool = True) -> Dict:
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
            dt_fmt += "Z"
        return dict(
            time_coverage_start=self.tcs.dt.strftime(dt_fmt),
            time_coverage_end=self.tce.dt.strftime(dt_fmt),
            time_coverage_duration=self.duration.isoformat,
            time_coverage_resolution=self.duration.isoformat
        )

    def has_overlap(self, period: "DatePeriod") -> bool:
        """
        Returns bool flag if this period has (partial) overlap with another period

        :param period:

        :return:
        """
        if not isinstance(period, DatePeriod):
            msg = f"period argument must be of type dateperiods.DatePeriod (was {type(period)})"
            raise ValueError(msg)
        return self.tcs.date <= period.tce.date and self.tce.date >= period.tcs.date

    def intersect(self, period: "DatePeriod") -> Union["DatePeriod", None]:
        """
        Computes the intersection and with another DatePeriod instance and returns
        a corresponding DatePeriod instance.
        :param period: dateperiods.DatePeriod
        :return: dateperiods.DatePeriod or None (if empty intersection)
        """

        # Input validation
        if not isinstance(period, DatePeriod):
            msg = "period argument must be of type dateperiods.DatePeriod (was {})"
            msg = msg.format(type(period))
            raise ValueError(msg)

        # Return None if intersection is empty
        if not self.has_overlap(period):
            return None

        # Compute the start and end date of the intersection
        intersect_start_date = max(self.tcs.date, period.tcs.date)
        intersect_end_date = min(self.tce.date, period.tce.date)

        # Create and return intersection Period
        return DatePeriod(intersect_start_date, intersect_end_date)

    @property
    def tcs(self) -> "DateDefinition":
        """ tcs: time coverage start as datetime object """
        return self._tcs

    @property
    def tce(self) -> "DateDefinition":
        """ tce: time coverage end as datetime object """
        return self._tce

    @property
    def duration(self) -> "DateDuration":
        return self._duration

    @property
    def label(self) -> str:
        return f"{str(self.tcs.dt)} till {str(self.tce.dt)}"

    @property
    def center(self) -> "datetime":
        tdelta_seconds = (self.tce.dt - self.tcs.dt).total_seconds()
        return self.tcs.dt + timedelta(seconds=int(round(0.5*tdelta_seconds, 0)))

    @property
    def center_datenum(self) -> float:
        return cftime.date2num(self.center, self.unit, self.calendar)

    @property
    def date_label(self) -> str:
        return f"{str(self.tcs.date)} till {str(self.tce.date)}"

    @property
    def unit(self) -> str:
        return str(self._unit)

    @property
    def calendar(self) -> str:
        return str(self._calendar)

    def __repr__(self) -> str:
        output = "DatePeriod:\n"
        for field in ["tcs", "tce", "exclude_rule"]:
            output += "%12s: %s" % (field, getattr(self, field).dt)
            output += "\n"
        return output


class PeriodIterator(object):
    """
    Class that allows to segment a period into subset periods of a given duration. The class then can be used
    as an iterator, but also filtered after initial segmentation
    """

    def __init__(self,
                 base_period: "DatePeriod",
                 segment_duration: str
                 ) -> None:
        """
        Create an iterator over a segment of a base period with a given duration
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
        self.exclude_rule = base_period.exclude_rule

        # Construct the list of periods
        self._segment_list = []
        self._get_segment_list()

    def __iter__(self) -> "PeriodIterator":
        """
        Mandatory iteration init method
        :return:
        """

        self.index = 0
        return self

    def __next__(self) -> "DatePeriod":
        """
        Mandatory iteration handler method

        :return: next element
        """
        index = int(self.index)
        if index > self.n_periods - 1:
            raise StopIteration
        self.index += 1
        return self._segment_list[index]

    def crop_to_period(self, period: "DatePeriod") -> None:
        """
        Will cause all segments to be cropped by the dates of the period according to the following
        rules:
            - segments with partial overlap will be cropped
            - segments with no overlap will be removed
            - segments with full will remain unchanged.

        :param period: dateperiods.DatePeriod

        :return: None
        """

        # Make a new list of segments that will overwrite existing ine
        cropped_segments = []
        for segment in self:
            cropped_segment = segment.intersect(period)
            if cropped_segment is not None:
                cropped_segments.append(cropped_segment)
        # Overwrite the list of segments
        self._segment_list = cropped_segments

    def _get_segment_list(self) -> None:
        """
        Compute the list of segments based on the input parameters. The work is delegated to the respective
        methods for each duraction type. All of these methods have to return a list of DatePeriod objects
        :return:
        """
        funcs = dict(
            P1D=self.get_day_segments,
            ISOWEEK=self.get_isoweek_segments,
            P1M=self.get_month_segments,
            P1Y=self.get_year_segments
        )
        base_tcs, base_tce = self.base_period.tcs.dt, self.base_period.tce.dt
        self._segment_list.extend(funcs[self.segment_duration](base_tcs, base_tce, self.base_period.exclude_rule))

    def filter_month(self, month_nums: List[int]) -> None:
        """
        Removes segments for if the month of both start and end of the time coverage is in a list
        of month that should be removed from the iterator.
        The origin of this filter function comes from the omission of summer month.

        :param month_nums: integer (list/tuple or scalar) of month number (1-12)

        :return: None
        """

        # Make sure the input is always a list
        month_nums = (
            month_nums if isinstance(month_nums, (list, tuple)) else [month_nums]
        )

        # Input validation
        valid_flag = [m in list(range(1, 13)) for m in month_nums]
        if False in valid_flag:
            raise ValueError("Invalid month encountered in {}".format(month_nums))

        # Lambda function for the filtering
        def filter_func(s): return s.tcs.month not in month_nums and s.tce.month not in month_nums

        # Create a new list of segments and overwrite the original one
        filter_segments = [s for s in self if filter_func(s)]
        self._segment_list = filter_segments

    @staticmethod
    def days_list(start_dt: "datetime", end_dt: "datetime") -> List[datetime]:
        """
        Return a list of all days (tuples of year, month, day) of all days between to
        datetimes
        :param start_dt: `datetime.datetime`
        :param end_dt: `datetime.datetime`
        :return: list
        """
        return [
            datetime(d.year, d.month, d.day)
            for d in rrule(DAILY, dtstart=start_dt, until=end_dt)
        ]

    @staticmethod
    def months_list(
            start_dt: "datetime",
            end_dt: "datetime",
            exclude_rule: "ExcludeMonth"
    ) -> List[List[int]]:
        """
        Return a list of all month (tuples of year, month) of all months between to datetimes
        of the specific datetime is not in exclude rule

        :param start_dt: datetime.datetime
        :param end_dt: datetime.datetime
        :param exclude_rule:

        :return: list
        """
        start = datetime(start_dt.year, start_dt.month, 1)
        end = datetime(end_dt.year, end_dt.month, 1)
        return [[d.year, d.month] for d in rrule(MONTHLY, dtstart=start, until=end) if d not in exclude_rule]

    @staticmethod
    def years_list(
            start_dt: "datetime",
            end_dt: "datetime",
    ) -> List[int]:
        """
        Return a list of all month (tuples of year, month) of all months between to datetimes

        NOTE: For yearly iterations, the currently applied monthly exclude rule does not apply.

        :param start_dt: datetime.datetime
        :param end_dt: datetime.datetime

        :return: list
        """
        start = datetime(start_dt.year, 1, 1)
        end = datetime(end_dt.year, 1, 1)
        return [d.year for d in rrule(YEARLY, dtstart=start, until=end)]

    @classmethod
    def get_day_segments(
            cls,
            start_dt: "datetime",
            end_dt: "datetime",
            exclude_rule: "ExcludeMonth"
    ) -> List["DatePeriod"]:
        """
        Return a list of daily DatePeriods between to datetimes

        :param start_dt: datetime.datetime
        :param end_dt: datetime.datetime
        :param exclude_rule: Rule to determine period in exclusion list

        :return: list of day segments
        """
        return [DatePeriod(d, d) for d in cls.days_list(start_dt, end_dt) if d not in exclude_rule]

    @classmethod
    def get_isoweek_segments(
            cls,
            start_dt: "datetime",
            end_dt: "datetime",
            exclude_rule: "ExcludeMonth"
    ) -> List["DatePeriod"]:
        """
        Return a list of isoweek DatePeriods between to datetimes

        :param start_dt: `datetime.datetime`
        :param end_dt: `datetime.datetime`
        :param exclude_rule: Rule to determine period in exclusion list

        :return: list
        """

        # Get the number of weeks
        list_of_days = cls.days_list(start_dt, end_dt)
        n_weeks = np.ceil(float(len(list_of_days)) / 7.).astype(int)

        # Isoweek segments are always Monday and start_dt might not be one
        # -> compute the offset
        start_day = list_of_days[0]
        weekday_offset = start_day.isoweekday() - 1

        segments = []
        for i in np.arange(n_weeks):
            # Compute start and stop date for each week
            d1 = start_dt + relativedelta(days=int(i * 7) - weekday_offset)
            d2 = start_dt + relativedelta(days=int((i + 1) * 7 - 1) - weekday_offset)

            prd = DatePeriod([d1.year, d1.month, d1.day], [d2.year, d2.month, d2.day])

            if prd.center in exclude_rule:
                continue

            # store start and stop day for each week
            segments.append(prd)

        return segments

    @classmethod
    def get_month_segments(
            cls,
            start_dt: "datetime",
            end_dt: "datetime",
            exclude_month: "ExcludeMonth"
    ) -> List["DatePeriod"]:
        """
        Return a list of monthly DatePeriods between to datetimes

        :param start_dt: Start date of Period
        :param end_dt: End date of Period
        :param exclude_month: List of month to exclude from iterator

        :return: list
        """
        return [DatePeriod(m, m) for m in cls.months_list(start_dt, end_dt, exclude_month)]

    @classmethod
    def get_year_segments(
            cls,
            start_dt: "datetime",
            end_dt: "datetime",
            *_   # exclude rule (not used for yearly segments
    ) -> List["DatePeriod"]:
        """
        Return a list of yearly DatePeriods between to datetimes

        :param start_dt: `datetime.datetime`
        :param end_dt: `datetime.datetime`

        :return: list of yearly DatePeriod's
        """
        return [DatePeriod([y], [y]) for y in cls.years_list(start_dt, end_dt)]

    @property
    def valid_segment_duration(self) -> List[str]:
        return [v for v in DateDurationType]

    @property
    def n_periods(self) -> int:
        return len(self._segment_list)

    @property
    def list(self) -> List["DatePeriod"]:
        return list(self._segment_list)

    def __repr__(self) -> str:
        output = "PeriodIterator:\n"

        fields = [
            "tcs",
            "tce"
        ]
        for field in fields:
            output += "%18s: %s" % (field, getattr(self.base_period, field).dt)
            output += "\n"
        fields = [
            "segment_duration",
            "exclude_rule",
            "n_periods"
        ]
        for field in fields:
            output += "%18s: %s" % (field, getattr(self, field))
            output += "\n"

        return output


class DateDefinition(object):
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

    :param date_def: Variable defining the date.
    :param tcs_or_tce: Flag indicating whether date marks beginning of end of
        period definition. Must be one of `tcs`  or `tce` (determines method
        of autocompletion).
    :param unit: `cftime` compliant time unit (default: `seconds since 1970-01-01`).
    :param calendar_name: `cftime` compliant calendar name (default: `standard`).
    """

    def __init__(self,
                 date_def: Union[List[int], str, "datetime", "date"],
                 tcs_or_tce: Literal["tcs", "tce"],
                 unit: Optional[str] = None,
                 calendar_name: Optional[str] = None
                 ) -> None:
        self._date_def = date_def
        if tcs_or_tce in self.valid_tcs_or_tce_values:
            self._tcs_or_tce = tcs_or_tce
        else:
            msg = f"Invalid tce_or_tcs: {tcs_or_tce} -> must be 'tcs' or 'tce'"
            raise ValueError(msg)

        self._unit = unit if unit is not None else "seconds since 1970-01-01"
        self._calendar = calendar_name if calendar_name is not None else "standard"

        # Init Properties
        self._year = None
        self._month = None
        self._day = None
        self._definition_level = None

        # Decode the input date definition and store the result in the
        # main year, month, day class properties
        self._decode_date_def()

    def _decode_date_def(self) -> None:
        """
        Decode the input date definition to this class
        :return:
        """

        # date definition is either a datetime.datetime or datetime.date,
        # -> the year, month, day properties can be simply transferred to this class
        datetime_like = (datetime, date, cftime.DatetimeGregorian, cftime.datetime, cftime.real_datetime)
        if isinstance(self._date_def, datetime_like):
            year, month, day = self._date_def.year, self._date_def.month, self._date_def.day
            definition_level = DateDurationType.P1D

        # date definition is a list or tuple
        # -> the list may contain year, [month], [day] with month and day may be generated
        # based on the tcs_or_tce property
        elif isinstance(self._date_def, (list, tuple)):
            year, month, day, definition_level = self._decode_int_list(self._date_def, self.type)

        if isinstance(self._date_def, str):
            year, month, day, definition_level = self._decode_str(self._date_def, self.type)

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
        self._definition_level = definition_level

    @staticmethod
    def _decode_int_list(int_list: List[int], tcs_or_tce: str) -> Tuple[int, int, int, DateDurationType]:
        """
        Returns a datetime object from an integer date list of type [yyyy, mm, [dd]].
        The datetime object will point to the first microsecond of the day for the
        start time (start_or_stop := "start") or the last microsecond
        """

        # Validate input
        n_entries = len(int_list)
        if n_entries < 1 or n_entries > 3:
            msg = f"Invalid integer date definition: {int_list} -> (year, [month], [day]"
            raise ValueError(msg)

        definition_level_map = {1: DateDurationType.P1Y, 2: DateDurationType.P1M, 3: DateDurationType.P1D}
        definition_level = definition_level_map[n_entries]

        # Autofill integer list if day or month+day are omitted
        # -> in this case the date will be either the beginning or the end of the either monthly or yearly period
        #    (based on the choice of tcs_or_tce)

        # Get the year (mandatory argument)
        year = int_list[0]

        # Get month (either list entry, or Jan for tcs and Dec for tce)
        month_defaults = {"tcs": 1, "tce": 12}
        month = month_defaults[tcs_or_tce] if n_entries == 1 else int_list[1]

        # Get the day
        # NOTE: The construction of the default day might cause an exception if the year, month numbers
        #       are invalid. This will cause a custom exception in the calendar module
        day_defaults = {"tcs": 1, "tce": calendar.monthrange(year, month)[1]}
        day = day_defaults[tcs_or_tce] if n_entries < 3 else int_list[2]

        # All variables (year, month, day) are defined at this point. This must be a valid date for datetime
        try:
            _ = datetime(year, month, day)
        except ValueError as e:
            msg = f"Invalid date: {year}, {month}, {day} []"
            raise ValueError(msg) from e

        # All done, return the values
        return year, month, day, definition_level

    def _decode_str_list(self, date_def_str: str, tcs_or_tce: str) -> Tuple[int, int, int, DateDurationType]:
        """
        Returns a datetime object from a date str of type yyyy[-mm[-dd]].
        The datetime object will point to the first microsecond of the day for the
        start time (start_or_stop := "start") or the last microsecond
        """

        # Validate input with regex (string must match [yyyy[-mm[-dd]]])
        str_pattern = r"^[1-2]\d{3}(-[0-1]\d(-[0-3]\d})?)?$"
        if not re.match(str_pattern, date_def_str):
            msg = f"Invalid string date definition: {date_def_str} -> yyyy[-mm[-dd]]"
            raise ValueError(msg)

        # Split the string into its components
        int_list = [int(v) for v in date_def_str.split("-")]
        return self._decode_int_list(int_list, tcs_or_tce)

    @property
    def isoformat(self) -> str:
        return self.dt.isoformat()

    @property
    def year(self) -> int:
        """
        The year as integer number
        :return: int
        """
        return int(self._year)

    @property
    def month(self) -> int:
        """
        The month as integer number
        :return: int
        """
        return int(self._month)

    @property
    def day(self) -> int:
        """
        The day as integer number
        :return: int
        """
        return int(self._day)

    @property
    def date(self) -> "date":
        """
        The date definition as `datetime.date`
        :return: `datetime.date`
        """
        return date(self.year, self.month, self.day)

    @property
    def dt(self) -> "datetime":
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
    def datenum(self) -> float:
        """
        The date in numerical expression. Values depend on calendar and unit
        :return: float
        """
        return cftime.date2num(self.dt, self.unit, self.calendar)

    @property
    def type(self) -> str:
        return str(self._tcs_or_tce)

    @property
    def is_tcs(self) -> bool:
        """
        Flag if the date definition is marked as the beginning of the time coverage

        :return: bool
        """
        return self.type == "tcs"

    @property
    def is_tce(self) -> bool:
        """
        Flag if the date definition is marked as the end of the time coverage

        :return: bool
        """
        return self.type == "tce"

    @property
    def is_monday(self) -> bool:
        """
        Flag if the current day is a Monday

        :return: bool
        """
        return self.dt.isoweekday() == 1

    @property
    def is_sunday(self) -> bool:
        """
        Flag if the current day is a Sunday
        :return: bool
        """
        return self.dt.isoweekday() == 7

    @property
    def is_first_day_of_month(self) -> bool:
        """
        Flag if the current day is the last day in a month
        :return: bool
        """
        return self.dt.day == 1

    @property
    def is_last_day_of_month(self) -> bool:
        """
        Flag if the current day is the last day in a month

        :return: bool
        """
        next_date = self.dt + relativedelta(days=1)
        return self.dt.month != next_date.month

    @property
    def valid_tcs_or_tce_values(self) -> List[Literal["tcs", "tce"]]:
        """
        The valid tags for time coverage start and time coverage end

        :return: str list
        """
        return ["tcs", "tce"]

    @property
    def unit(self) -> str:
        return str(self._unit)

    @property
    def calendar(self) -> str:
        return str(self._calendar)

    @property
    def definition_level(self) -> DateDurationType:
        return self._definition_level

    def __repr__(self):
        output = "DateDefinition:\n"
        fields = [
            "isoformat",
            "definition_level",
            "type",
            "is_monday",
            "is_sunday",
            "is_first_day_of_month",
            "is_last_day_of_month",
        ]
        for field in fields:
            output += "%24s: %s" % (field, getattr(self, field))
            output += "\n"
        return output


DurationType = Literal["year", "month", "isoweek", "day", "custom"]


class DateDuration(object):
    """
    Container for duration parameters of the period between two dates
    """

    def __init__(self,
                 tcs: "DateDefinition",
                 tce: "DateDefinition"
                 ) -> None:
        """
        Compute the duration between two dates

        :param tcs: DateDefinition
        :param tce: DateDefinition
        """

        # Basic sanity check
        if tce.dt <= tcs.dt:
            raise ValueError(f"End {tcs} <= Start {tce}")

        # Arguments
        self._tcs = tcs
        self._tce = tce

    @property
    def tcs(self) -> "DateDefinition":
        return self._tcs

    @property
    def tce(self) -> "DateDefinition":
        return self._tce

    @property
    def total_seconds(self) -> float:
        """
        The number of seconds
        :return: int
        """
        return (self.tce.dt + relativedelta(microseconds=1) - self.tcs.dt).total_seconds()

    @property
    def total_days(self) -> int:
        """
        Number of days between start and end (1 if both are the same day)
        :return: int
        """
        return (self.tce.dt - self.tcs.dt).days + 1

    @property
    def is_day(self) -> bool:
        """
        Flag if the period is a full month
        :return: bool
        """
        return self.tcs.date == self.tce.date

    @property
    def is_isoweek(self) -> bool:
        """
        Flag if period is a default week (Monday to following Sunday)
        :return:
        """
        return self.tcs.is_monday and self.tce.is_sunday and self.total_days == 7

    @property
    def is_month(self) -> bool:
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
    def is_year(self) -> bool:
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
    def duration(self) -> "Duration":
        """
        Return a `duration.Duration` object
        :return:
        """
        tdelta = relativedelta(
            dt1=self.tce.dt+relativedelta(microseconds=1),
            dt2=self.tcs.dt
        )
        return Duration(
            years=tdelta.years,
            months=tdelta.months,
            days=tdelta.days,
            hours=tdelta.hours,
            minutes=tdelta.minutes,
            seconds=tdelta.seconds
        )

    @property
    def isoformat(self) -> str:
        return duration_isoformat(self.duration)

    @property
    def type(self) -> DurationType:
        """
        Return a classifier that indicates the period duration type
        (e.g. year, month, isoweek, day, custom)

        :return: Name of the period type
        """
        period_fixed_types: List[Tuple[bool, DurationType]] = [
            (self.is_year, "year"),
            (self.is_month, "month"),
            (self.is_isoweek, "isoweek"),
            (self.is_day, "day"),
        ]
        # sourcery skip: use-next
        for condition, period_type in period_fixed_types:
            if condition:
                return period_type
        return "custom"

    def __repr__(self):
        output = "DateDuration:\n"
        fields = [
            "isoformat",
            "type",
            "total_days",
            "is_day",
            "is_isoweek",
            "is_month",
            "is_year"
        ]
        for field in fields:
            output += "%16s: %s" % (field, getattr(self, field))
            output += "\n"
        return output
