# dateperiods: Managing periods between dates in python

![Python package](https://github.com/pysiral/dateperiods/workflows/Python%20package/badge.svg)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)
[![Python Version](https://img.shields.io/badge/python-3.10,_3.11,_3.12,_3.13-blue)](https://www.python.org/downloads/)

## About dateperiods

The package `dateperiods` is meant to make iterating over certain periods between two dates easy. 
The main `DatePeriod` class takes two dates into account, the start of the time coverage with a daily granularity, 
but microsecond resolution:


### Basic Usage

The main class of the package is `DatePeriod`. A `DatePeriod` object can be created by providing a start date 
and an end date definition. The definition can either be 

1. a list of integers (year, month, day)
2. a string in ISO 8601 format (YYYY-MM-DD)
3. a `date` object from the standard python `datetime` package.
4. a `datetime` object from the standard python`datetime` package.

E.g., a `DatePeriod` object can be created as follows and all four definitions are equivalent:

```python
from datetime import datetime, date
from src.dateperiods import DatePeriod

DatePeriod([2020, 10, 1], [2021, 4, 30])
DatePeriod("2020-10-01", "2021-04-30")
DatePeriod(date(2020, 10, 1), date(2021, 4, 30))
DatePeriod(datetime(2020, 10, 1), datetime(2021, 4, 30))
```
```
DatePeriod:
         tcs: 2020-10-01 00:00:00
         tce: 2021-04-30 23:59:59.999999
  definition: P1D
    duration: P7M
```
which will yield an object that represents the period from October 1st, 2020 till April 30th, 2021.
(7 months). Auto-completion of input arguments is also possible and the following is equivalent to the above:

```python
dp = DatePeriod([2020, 10], [2021, 4])
```
Output
```
DatePeriod:
         tcs: 2020-10-01 00:00:00
         tce: 2021-04-30 23:59:59.999999
  definition: P1M
    duration: P7M
```

The only difference is that the period definition is now "P1M" (1 month) instead of "P1D" (1 day)
indicating that the start and end dates were auto-completed to the first, respectively last day of the month. 

The second (end date) argument of the `DatePeriod` constructor is optional. If not provided, the period will be
created with a duration of the derived from the definition level of the first argument. E.g.

```python
dp = DatePeriod([2020, 10])
```
```
DatePeriod:
         tcs: 2020-10-01 00:00:00
         tce: 2020-10-31 23:59:59.999999
  definition: P1M
    duration: P1M
```

or 

```python
dp = DatePeriod([2020])
```
```         
DatePeriod:
         tcs: 2020-01-01 00:00:00
         tce: 2020-12-31 23:59:59.999999
  definition: P1Y
    duration: P1Y
```

## Period Properties

The main properties of `DatePeriod` objects are the start date (tcs = time coverage start):

```python
dp.tcs
```
```
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
dp.tce
```
```
DateDefinition:
               isoformat: 2021-04-30T23:59:59.999999
                    type: tce
               is_monday: False
               is_sunday: False
   is_first_day_of_month: False
    is_last_day_of_month: True
```

and the duration between two dates:

```python
dp.duration
```
```
DateDuration:
       isoformat: P7M
      total_days: 212
          is_day: False
      is_isoweek: False
        is_month: False
         is_year: False
```

## Period Segmentation

The period can be segmented into defined a duration type (day, isoweek, month, year):

```python
dp.get_segments("month")
```
Output
```
PeriodIterator:
                     tcs: 2020-10-01 00:00:00
                     tce: 2021-04-30 23:59:59.999999
        segment_duration: month
               n_periods: 7
```

The return value of `get_segments()` is a python iterator with each item is a `DatePeriod` instance for the sub-period: 

```python
[period.label for period in dp.get_segments("month")]
```
Output

```
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
from src.dateperiods import ExcludeMonth
period_exc = DatePeriod([2020, 9, 1], [2021, 5, 31], exclude_rules=ExcludeMonth([5, 9]))
```
will ensure that the month of September 2020 and May 2021, will not be part
of the monthly sub-periods: 

```python
period_exc.get_segments("month")
```
Output

```
PeriodIterator:
                     tcs: 2020-10-01 00:00:00
                     tce: 2021-04-30 23:59:59.999999
        segment_duration: month
               n_periods: 7
```

## Installation

See the [release page](https://github.com/shendric/dateperiods/releases) of this project for the latest version of `dateperiods` and install either from the main branch

`pip install "dateperiods@git+https://github.com/shendric/dateperiods.git`

of for a specific verion

`pip install "dateperiods@git+https://github.com/shendric/dateperiods.git@1.1.0`

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
