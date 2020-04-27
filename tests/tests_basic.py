
from context import dateperiods

from datetime import datetime
from dateutil.relativedelta import relativedelta

import unittest


class BasicFunctionalityTestSuite(unittest.TestCase):
    """A standard list of test cases."""

    def test_date_int_list_len(self):
        self.assertRaises(ValueError, dateperiods.DatePeriod, [2018], [2018, 4, 1])
        self.assertRaises(ValueError, dateperiods.DatePeriod, [2018, 4, 1, 1], [2018, 4, 1])

    def test_no_tcs_after_tce(self):
        self.assertRaises(ValueError, dateperiods.DatePeriod, [2018, 5, 1], [2018, 4, 1])
        self.assertRaises(ValueError, dateperiods.DatePeriod, datetime(2018, 4, 2), datetime(2018, 4, 1))

    def test_tcs_tce_always_full_days(self):
        tcs_reference_dt = datetime(2018, 4, 1, 0, 0, 0)
        tce_reference_dt = datetime(2018, 5, 1) - relativedelta(microseconds=1)
        prd = dateperiods.DatePeriod([2018, 4], [2018, 4])
        self.assertEqual(prd.tcs, tcs_reference_dt)
        self.assertEqual(prd.tce, tce_reference_dt)
        prd = dateperiods.DatePeriod(datetime(2018, 4, 1), datetime(2018, 4, 30))
        self.assertEqual(prd.tcs, tcs_reference_dt)
        self.assertEqual(prd.tce, tce_reference_dt)

    def test_period_type_detection_daily(self):
        prd = dateperiods.DatePeriod([2018, 4, 1], [2018, 4, 1])
        self.assertEqual(prd.period_type, "daily")
        prd = dateperiods.DatePeriod(datetime(2018, 4, 1), datetime(2018, 4, 1))
        self.assertEqual(prd.period_type, "daily")

    def test_period_type_detection_default_week(self):
        prd = dateperiods.DatePeriod([2018, 4, 2], [2018, 4, 8])
        self.assertEqual(prd.period_type, "default_week")
        prd = dateperiods.DatePeriod(datetime(2018, 4, 2), datetime(2018, 4, 8))
        self.assertEqual(prd.period_type, "default_week")

    def test_period_type_detection_monthly(self):
        prd = dateperiods.DatePeriod([2018, 4], [2018, 4])
        self.assertEqual(prd.period_type, "monthly")
        prd = dateperiods.DatePeriod(datetime(2018, 4, 1), datetime(2018, 4, 30))
        self.assertEqual(prd.period_type, "monthly")

    def test_daily_segmentation(self):
        prd = dateperiods.DatePeriod([2018, 4], [2018, 4])
        prds = prd.get_period_segments("daily")
        self.assertEqual(len(prds), 30)
        prds = prd.get_period_segments("daily", exclude_month=[5, 6, 7, 8, 9])
        self.assertEqual(len(prds), 30)
        self.assertEqual(prds[0].period_type, "daily")

    def test_default_week_segmentation(self):
        prd = dateperiods.DatePeriod([2017, 4], [2017, 10])
        prds = prd.get_period_segments("default_week")
        self.assertEqual(len(prds), 32)
        prds = prd.get_period_segments("default_week", exclude_month=[5, 6, 7, 8, 9])
        self.assertEqual(len(prds), 11)
        self.assertEqual(prds[0].period_type, "default_week")

    def test_monthly_segmentation(self):
        prd = dateperiods.DatePeriod([2017, 4], [2018, 4])
        prds = prd.get_period_segments("monthly")
        self.assertEqual(len(prds), 13)
        prds = prd.get_period_segments("monthly", exclude_month=[5, 6, 7, 8, 9])
        self.assertEqual(len(prds), 8)
        self.assertEqual(prds[0].period_type, "monthly")

    def test_duration_str(self):
        prd = dateperiods.DatePeriod([2018, 4, 1], [2018, 4, 1])
        self.assertEqual(prd.duration_isoformat, "P1D")
        prd = dateperiods.DatePeriod([2018, 4], [2018, 4])
        self.assertEqual(prd.duration_isoformat, "P1M")


if __name__ == '__main__':
    unittest.main()
