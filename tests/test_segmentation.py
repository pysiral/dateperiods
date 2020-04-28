# -*- coding: utf-8 -*-

from context import dateperiods

from datetime import datetime
from dateutil.relativedelta import relativedelta

import unittest


class SegmentationFunctionalityTestSuite(unittest.TestCase):
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
        prd = dateperiods.DatePeriod([2018, 4], [2018, 4])
        segments = prd.get_segments("day")
        self.assertEqual(segments.n_periods, 30)
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


if __name__ == '__main__':
    unittest.main()
