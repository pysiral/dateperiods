# -*- coding: utf-8 -*-

from context import dateperiods

from datetime import datetime
from dateutil.relativedelta import relativedelta

import unittest


class BasicFunctionalityTestSuite(unittest.TestCase):
    """A standard list of test cases """

    def test_date_int_list_len(self):
        self.assertRaises(TypeError, dateperiods.DatePeriod, [])
        self.assertRaises(ValueError, dateperiods.DatePeriod, [], [2018, 4, 1])
        self.assertRaises(ValueError, dateperiods.DatePeriod, None, [2018, 4, 1])
        self.assertRaises(ValueError, dateperiods.DatePeriod, [2018, 4, 1, 1], [2018, 4, 1])

    def test_date_flags(self):
        prd = dateperiods.DatePeriod([2018, 4], [2018, 4])
        self.assertTrue(prd.tcs.is_tcs)
        self.assertFalse(prd.tcs.is_tce)
        self.assertTrue(prd.tce.is_tce)
        self.assertFalse(prd.tce.is_tcs)

    def test_no_tcs_after_tce(self):
        self.assertRaises(ValueError, dateperiods.DatePeriod, [2018, 5, 1], [2018, 4, 1])
        self.assertRaises(ValueError, dateperiods.DatePeriod, datetime(2018, 4, 2), datetime(2018, 4, 1))

    def test_tcs_tce_always_full_days(self):
        tcs_reference_dt = datetime(2018, 4, 1, 0, 0, 0)
        tce_reference_dt = datetime(2018, 5, 1) - relativedelta(microseconds=1)
        prd = dateperiods.DatePeriod([2018, 4], [2018, 4])
        self.assertEqual(prd.tcs.dt, tcs_reference_dt)
        self.assertEqual(prd.tce.dt, tce_reference_dt)
        prd = dateperiods.DatePeriod(datetime(2018, 4, 1), datetime(2018, 4, 30))
        self.assertEqual(prd.tcs.dt, tcs_reference_dt)
        self.assertEqual(prd.tce.dt, tce_reference_dt)

    def test_duration_year(self):
        prd = dateperiods.DatePeriod([2018], [2018])
        duration = prd.duration
        self.assertTrue(duration.is_year)
        self.assertFalse(duration.is_day)
        self.assertFalse(duration.is_isoweek)
        self.assertFalse(duration.is_month)
        self.assertEqual(duration.isoformat, "P1Y")
        self.assertEqual(duration.type, "year")

    def test_duration_month(self):
        prd = dateperiods.DatePeriod([2018, 4], [2018, 4])
        duration = prd.duration
        self.assertTrue(duration.is_month)
        self.assertFalse(duration.is_day)
        self.assertFalse(duration.is_isoweek)
        self.assertFalse(duration.is_year)
        self.assertEqual(duration.isoformat, "P1M")
        self.assertEqual(duration.type, "month")

    def test_duration_isoweek(self):
        prd = dateperiods.DatePeriod([2018, 4, 2], [2018, 4, 8])
        duration = prd.duration
        self.assertTrue(duration.is_isoweek)
        self.assertFalse(duration.is_day)
        self.assertFalse(duration.is_month)
        self.assertFalse(duration.is_year)
        self.assertEqual(duration.isoformat, "P7D")
        self.assertEqual(duration.type, "isoweek")

    def test_duration_day(self):
        prd = dateperiods.DatePeriod([2018, 4, 1], [2018, 4, 1])
        duration = prd.duration
        self.assertTrue(duration.is_day)
        self.assertFalse(duration.is_month)
        self.assertFalse(duration.is_isoweek)
        self.assertFalse(duration.is_year)
        self.assertEqual(duration.isoformat, "P1D")
        self.assertEqual(duration.type, "day")

    def test_duration_custom(self):
        prd = dateperiods.DatePeriod([2018, 4, 1], [2018, 4, 2])
        duration = prd.duration
        self.assertFalse(duration.is_day)
        self.assertFalse(duration.is_month)
        self.assertFalse(duration.is_isoweek)
        self.assertFalse(duration.is_year)
        self.assertEqual(duration.isoformat, "P2D")
        self.assertEqual(duration.type, "custom")

    def test_netcdf_attribute_dict(self):
        prd = dateperiods.DatePeriod([2018, 4, 1], [2018, 4, 1])
        attr_dict = prd.get_netcdf_attributes(zulu=True)
        self.assertTrue("time_coverage_start" in attr_dict)
        self.assertEqual(attr_dict["time_coverage_start"], "20180401T000000Z")
        self.assertTrue("time_coverage_end" in attr_dict)
        self.assertEqual(attr_dict["time_coverage_end"], "20180401T235959Z")
        self.assertTrue("time_coverage_duration" in attr_dict)
        self.assertEqual(attr_dict["time_coverage_duration"], "P1D")
        self.assertTrue("time_coverage_resolution" in attr_dict)
        self.assertEqual(attr_dict["time_coverage_resolution"], "P1D")

    # def test_daily_segmentation(self):
    #     prd = dateperiods.DatePeriod([2018, 4], [2018, 4])
    #     prds = prd.get_period_segments("daily")
    #     self.assertEqual(len(prds), 30)
    #     prds = prd.get_period_segments("daily", exclude_month=[5, 6, 7, 8, 9])
    #     self.assertEqual(len(prds), 30)
    #     self.assertEqual(prds[0].period_type, "daily")
    #
    # def test_default_week_segmentation(self):
    #     prd = dateperiods.DatePeriod([2017, 4], [2017, 10])
    #     prds = prd.get_period_segments("default_week")
    #     self.assertEqual(len(prds), 32)
    #     prds = prd.get_period_segments("default_week", exclude_month=[5, 6, 7, 8, 9])
    #     self.assertEqual(len(prds), 11)
    #     self.assertEqual(prds[0].period_type, "default_week")
    #
    # def test_monthly_segmentation(self):
    #     prd = dateperiods.DatePeriod([2017, 4], [2018, 4])
    #     prds = prd.get_period_segments("monthly")
    #     self.assertEqual(len(prds), 13)
    #     prds = prd.get_period_segments("monthly", exclude_month=[5, 6, 7, 8, 9])
    #     self.assertEqual(len(prds), 8)
    #     self.assertEqual(prds[0].period_type, "monthly")


if __name__ == '__main__':
    unittest.main()
