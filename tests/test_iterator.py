# -*- coding: utf-8 -*-

import unittest
from datetime import date

from context import dateperiods


class IteratorBasicFunctionalityTestSuite(unittest.TestCase):
    """ Testing the segmentation of Periods """

    def test_input_args(self):
        prd = dateperiods.DatePeriod([2018, 4], [2018, 4])
        self.assertRaises(TypeError, prd.get_segments)
        self.assertRaises(ValueError, prd.get_segments, None)
        self.assertRaises(ValueError, prd.get_segments, "a")
        self.assertRaises(ValueError, prd.get_segments, 1)

    def test_segment_iterator(self):
        prd = dateperiods.DatePeriod([2018, 4], [2018, 4])
        segments = prd.get_segments("day")
        for segment in segments:
            self.assertIsInstance(segment, dateperiods.DatePeriod)

    def test_segment_lengths_days(self):
        prd = dateperiods.DatePeriod([2018, 4], [2018, 5])
        segments = prd.get_segments("day")
        self.assertEqual(segments.n_periods, 61)
        for segment in segments:
            self.assertEqual(segment.tcs.date, segment.tce.date)

    def test_segment_lengths_isoweeks(self):
        prd = dateperiods.DatePeriod([2018, 4], [2018, 4])
        segments = prd.get_segments("isoweek")
        self.assertEqual(segments.n_periods, 5)
        for segment in segments:
            self.assertTrue(segment.tcs.is_monday)
            self.assertTrue(segment.tce.is_sunday)

    def test_segment_lengths_months(self):
        prd = dateperiods.DatePeriod([2018, 3], [2018, 4])
        segments = prd.get_segments("month")
        self.assertEqual(segments.n_periods, 2)
        for segment in segments:
            self.assertEqual(segment.tcs.dt.day, 1)
            self.assertTrue(segment.tce.is_last_day_of_month)

    def test_segment_lengths_years(self):
        prd = dateperiods.DatePeriod([2018, 3], [2019, 4])
        segments = prd.get_segments("year")
        self.assertEqual(segments.n_periods, 2)
        for segment in segments:
            self.assertEqual(segment.tcs.day, 1)
            self.assertEqual(segment.tcs.month, 1)
            self.assertEqual(segment.tce.day, 31)
            self.assertEqual(segment.tce.month, 12)


class IteratorCroppingFunctionalityTestSuite(unittest.TestCase):
    """ Testing the segmentation of Periods """

    def test_input_args(self):
        prd = dateperiods.DatePeriod([2018, 4, 15], [2018, 5, 15])
        self.assertIsInstance(prd.get_segments("month", crop_to_period=True), dateperiods.PeriodIterator)
        self.assertIsInstance(prd.get_segments("month", crop_to_period=False), dateperiods.PeriodIterator)
        self.assertRaises(ValueError, prd.get_segments, "monthly", crop_to_period=1)
        self.assertRaises(ValueError, prd.get_segments, "monthly", crop_to_period="a")
        self.assertRaises(ValueError, prd.get_segments, "monthly", crop_to_period=None)

    def test_cropped_segment_type_daily(self):
        prd = dateperiods.DatePeriod([2018, 4, 15], [2018, 5, 15])
        segments = prd.get_segments("day", crop_to_period=True)
        self.assertEqual(segments.n_periods, 31)

    def test_cropped_segment_type_monthly(self):
        prd = dateperiods.DatePeriod([2018, 4, 15], [2018, 5, 15])
        segments = prd.get_segments("month", crop_to_period=True)
        self.assertEqual(segments.n_periods, 2)
        # Test first segment (should be Apr 15 -> Apr. 30)
        first_segment = segments.list[0]
        self.assertEqual(first_segment.tcs.date, date(2018, 4, 15))
        self.assertEqual(first_segment.tce.date, date(2018, 4, 30))
        # Test second segment (should be May 1 -> May 15)
        second_segment = segments.list[1]
        self.assertEqual(second_segment.tcs.date, date(2018, 5, 1))
        self.assertEqual(second_segment.tce.date, date(2018, 5, 15))

    def test_cropped_segment_type_yearly(self):
        prd = dateperiods.DatePeriod([2018, 4, 15], [2019, 5, 15])
        segments = prd.get_segments("year", crop_to_period=True)
        self.assertEqual(segments.n_periods, 2)
        # Test first segment (should be Apr 15 -> Apr. 30)
        first_segment = segments.list[0]
        self.assertEqual(first_segment.tcs.date, date(2018, 4, 15))
        self.assertEqual(first_segment.tce.date, date(2018, 12, 31))
        # Test second segment (should be May 1 -> May 15)
        second_segment = segments.list[1]
        self.assertEqual(second_segment.tcs.date, date(2019, 1, 1))
        self.assertEqual(second_segment.tce.date, date(2019, 5, 15))


class IteratorMonthFilterFunctionalityTestSuite(unittest.TestCase):
    """ Testing the segmentation of Periods """

    def test_input_args(self):
        prd = dateperiods.DatePeriod([2010], [2010])
        segments = prd.get_segments("month")
        self.assertRaises(TypeError, segments.filter_month)
        self.assertRaises(ValueError, segments.filter_month, "monthly")
        self.assertRaises(ValueError, segments.filter_month, ["monthly"])
        self.assertRaises(ValueError, segments.filter_month, 0)
        self.assertRaises(ValueError, segments.filter_month, 13)

    def test_month_filter_daily_duration(self):
        prd = dateperiods.DatePeriod([2011], [2011])
        segments = prd.get_segments("day")
        months_to_exclude = [5, 6, 7, 8, 9]
        segments.filter_month(months_to_exclude)
        # 2011 is not a leap year, month May through Sep are 153 days
        # -> 365 - 153 = 212
        self.assertEqual(segments.n_periods, 212)

        # Do that again, but with a leap year
        prd = dateperiods.DatePeriod([2020], [2020])
        segments = prd.get_segments("day")
        months_to_exclude = [5, 6, 7, 8, 9]
        segments.filter_month(months_to_exclude)
        # 2011 is not a leap year, month May through Sep are 153 days
        # -> 366 - 153 = 213
        self.assertEqual(segments.n_periods, 213)

    def test_month_filter_isoweekly_duration(self):
        prd = dateperiods.DatePeriod([2010], [2010])
        segments = prd.get_segments("isoweek")
        months_to_exclude = [5, 6, 7, 8, 9]
        segments.filter_month(months_to_exclude)
        self.assertEqual(segments.n_periods, 30)

    def test_month_filter_monthly_duration(self):
        prd = dateperiods.DatePeriod([2010], [2010])
        segments = prd.get_segments("month")
        months_to_exclude = [5, 6, 7, 8, 9]
        segments.filter_month(months_to_exclude)
        self.assertEqual(segments.n_periods, 7)

    def test_month_filter_yearly_duration(self):
        prd = dateperiods.DatePeriod([2010], [2011])
        segments = prd.get_segments("year")
        months_to_exclude = [5, 6, 7, 8, 9]
        # filtering should not do anything
        segments.filter_month(months_to_exclude)
        self.assertEqual(segments.n_periods, 2)

    def test_month_filter_empty_result(self):
        prd = dateperiods.DatePeriod([2010, 6], [2010, 8])
        segments = prd.get_segments("month")
        months_to_exclude = [5, 6, 7, 8, 9]
        # filtering should not do anything
        segments.filter_month(months_to_exclude)
        self.assertEqual(segments.n_periods, 0)


if __name__ == '__main__':
    unittest.main()
