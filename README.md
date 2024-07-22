# dateperiods: Periods between dates in python

![Python package](https://github.com/pysiral/dateperiods/workflows/Python%20package/badge.svg)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)
[![Python Version](https://img.shields.io/badge/python-3.7,_3.8,_3.9,_3.10,_3.11,_3.12-blue)](https://www.python.org/downloads/)

## About dateperiods

The package `dateperiods` is meant to make iterating over certain periods between two dates easy. The main `DatePeriod` class takes two dates into account, the start of the time coverage with a daily granularity, but microsecond resolution:


### Basic Usage

```python
>>> from dateperiods import DatePeriod
>>> DatePeriod([2020, 10, 1], [2021, 4, 30])
DatePeriod:
         tcs: 2020-10-01 00:00:00
         tce: 2021-04-30 23:59:59.999999
```

but auto-completion of input arguments is also possible. E.g., the statement above is equivalent to: 

```python
>>> dp = DatePeriod([2020, 10], [2021, 4])
DatePeriod:
         tcs: 2020-10-01 00:00:00
         tce: 2021-04-30 23:59:59.999999
```

The main properties of `DatePeriod` objects are the start date (tcs = time coverage start):

```
>>> dp.tcs
DateDefinition:
               isoformat: 2020-10-01T00:00:00
                    type: tcs
               is_monday: False
               is_sunday: False
   is_first_day_of_month: True
    is_last_day_of_month: False
```

the end date (tce = time coverage end):

```
>>> dp.tce
DateDefinition:
               isoformat: 2021-04-30T23:59:59.999999
                    type: tce
               is_monday: False
               is_sunday: False
   is_first_day_of_month: False
    is_last_day_of_month: True
```

and the duration between two dates:

```
>>> dp.tce
DateDuration:
       isoformat: P7M
            type: custom
      total_days: 212
          is_day: False
      is_isoweek: False
        is_month: False
         is_year: False
```

The period can be segmented into defined a duration type (day, isoweek, month, year):

```python
>>> dp.get_segments("month")
PeriodIterator:
                     tcs: 2020-10-01 00:00:00
                     tce: 2021-04-30 23:59:59.999999
        segment_duration: month
               n_periods: 7
```

The return value of `get_segments()` is a python iterator with each item is a `DatePeriod` instance for the sub-period: 

```python
>>> [period.label for period in dp.get_segments("month")]
['2020-10-01 00:00:00 till 2020-10-31 23:59:59.999999',
 '2020-11-01 00:00:00 till 2020-11-30 23:59:59.999999',
 '2020-12-01 00:00:00 till 2020-12-31 23:59:59.999999',
 '2021-01-01 00:00:00 till 2021-01-31 23:59:59.999999',
 '2021-02-01 00:00:00 till 2021-02-28 23:59:59.999999',
 '2021-03-01 00:00:00 till 2021-03-31 23:59:59.999999',
 '2021-04-01 00:00:00 till 2021-04-30 23:59:59.999999']
```

### Exclusion Rules

A `DatePeriod` can be defined with rules that define if segments should be 
excluded from the `PeriodIterator`. E.g. 

```python
>>> from dateperiods import ExcludeMonth
>>> period_exc = DatePeriod([2020, 9, 1], [2021, 5, 31], exclude_rules=ExcludeMonth([5, 9]))
```
will ensure that the month of September 2020 and May 2021, will not be part
of the monthly sub-periods: 

```python
>>> period_exc.get_segments("month")
PeriodIterator:
                     tcs: 2020-10-01 00:00:00
                     tce: 2021-04-30 23:59:59.999999
        segment_duration: month
               n_periods: 7
```

## Installation

See the [release page](https://github.com/shendric/dateperiods/releases) of this project for the latest version of `dateperiods` and install either from the main branch

`pip install "git+https://github.com/shendric/dateperiods.git`

of for a specific verion

`pip install "git+https://github.com/shendric/dateperiods.git@1.1.0`

## Copyright Statements

### isodate

This project uses isodate (https://github.com/gweis/isodate)

Copyright (c) 2021, Hugo van Kemenade and contributors

Copyright (c) 2009-2018, Gerhard Weis and contributors

Copyright (c) 2009, Gerhard Weis

## Roadmap

- [ ] Add merge (`+`) operator for `DatePeriods`
- [ ] Add option to `DatePeriods.get_segments` to ensure sub-periods are fully within base period
- [ ] Add custom segments lengths using `dateutil-rrulestr()` (e.g. `RRULE:FREQ=DAILY;INTERVAL=14` for two week periods)
