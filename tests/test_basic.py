# -*- coding: utf-8 -*-

import unittest
from datetime import datetime, date

from context import dateperiods
from dateutil.relativedelta import relativedelta


class BasicFunctionalityTestSuite(unittest.TestCase):
    """A standard list of test cases """

    def test_input_int_len(self):
        self.assertRaises(ValueError, dateperiods.DatePeriod, [])
        self.assertRaises(ValueError, dateperiods.DatePeriod, [], [2018, 4, 1])
        self.assertRaises(ValueError, dateperiods.DatePeriod, None, [2018, 4, 1])
        self.assertRaises(ValueError, dateperiods.DatePeriod, [2018, 4, 1, 1], [2018, 4, 1])

    def test_input_str(self):
        self.assertRaises(ValueError, dateperiods.DatePeriod, "a")
        self.assertRaises(ValueError, dateperiods.DatePeriod, "2O18")           # <- that is a letter O, not a zero
        self.assertRaises(ValueError, dateperiods.DatePeriod, "3018")           # year out of range (999 < year < 3000)
        self.assertRaises(ValueError, dateperiods.DatePeriod, "2018-13")        # month out of range
        self.assertRaises(ValueError, dateperiods.DatePeriod, "2018-00")        # month out of range
        self.assertRaises(ValueError, dateperiods.DatePeriod, "2018-04-31")     # day out of range
        self.assertRaises(ValueError, dateperiods.DatePeriod, "2018-04-30T12:00:00")  # not a date
        self.assertRaises(ValueError, dateperiods.DatePeriod, "2018-")          # month missing
        self.assertRaises(ValueError, dateperiods.DatePeriod, "2018-04-")       # day missing

    def test_equal_results_all_input_types(self):
        different_input_types = [
            dateperiods.DatePeriod([2018, 4]),
            dateperiods.DatePeriod([2018, 4], [2018, 4]),
            dateperiods.DatePeriod("2018-04"),
            dateperiods.DatePeriod("2018-04", "2018-04"),
            dateperiods.DatePeriod("2018-04-01", "2018-04-30"),
            dateperiods.DatePeriod(date(2018, 4, 1), date(2018, 4, 30)),
            dateperiods.DatePeriod(datetime(2018, 4, 1), datetime(2018, 4, 30)),
        ]
        start_dates = [prd.tcs.date for prd in different_input_types]
        end_dates = [prd.tce.date for prd in different_input_types]
        self.assertEqual(len(set(start_dates)), 1)
        self.assertEqual(len(set(end_dates)), 1)

    def test_definition_level(self):
        self.assertEqual("P1Y", dateperiods.DatePeriod("2018").definition_level.value)
        self.assertEqual("P1M", dateperiods.DatePeriod("2018-04").definition_level.value)
        self.assertEqual("P1D", dateperiods.DatePeriod("2018-04-01").definition_level.value)
        self.assertEqual("P1Y", dateperiods.DatePeriod([2018]).definition_level.value)
        self.assertEqual("P1M", dateperiods.DatePeriod([2018, 4]).definition_level.value)
        self.assertEqual("P1D", dateperiods.DatePeriod([2018, 4, 1]).definition_level.value)
        self.assertEqual("P1D", dateperiods.DatePeriod(date(2018, 4, 1)).definition_level.value)

        self.assertEqual("P1M", dateperiods.DatePeriod("2018", "2018-04").definition_level.value)
        self.assertEqual("P1D", dateperiods.DatePeriod("2018", "2018-04-01").definition_level.value)
        self.assertEqual("P1D", dateperiods.DatePeriod("2018-04", "2018-04-01").definition_level.value)

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
        tcs_reference_dt = datetime(2018, 4, 1)
        tce_reference_dt = datetime(2018, 5, 1) - relativedelta(microseconds=1)
        prd = dateperiods.DatePeriod([2018, 4], [2018, 4])
        self.assertEqual(prd.tcs.dt, tcs_reference_dt)
        self.assertEqual(prd.tce.dt, tce_reference_dt)
        prd = dateperiods.DatePeriod(datetime(2018, 4, 1), datetime(2018, 4, 30))
        self.assertEqual(prd.tcs.dt, tcs_reference_dt)
        self.assertEqual(prd.tce.dt, tce_reference_dt)

    def test_netcdf_attribute_dict(self):
        prd = dateperiods.DatePeriod([2018, 4, 1], [2018, 4, 1])
        attr_dict = prd.get_netcdf_attributes()
        self.assertTrue("time_coverage_start" in attr_dict)
        self.assertEqual(attr_dict["time_coverage_start"], "20180401T000000Z")
        self.assertTrue("time_coverage_end" in attr_dict)
        self.assertEqual(attr_dict["time_coverage_end"], "20180401T235959Z")
        self.assertTrue("time_coverage_duration" in attr_dict)
        self.assertEqual(attr_dict["time_coverage_duration"], "P1D")
        self.assertTrue("time_coverage_resolution" in attr_dict)
        self.assertEqual(attr_dict["time_coverage_resolution"], "P1D")


class DurationFunctionalityTestSuite(unittest.TestCase):
    """A standard list of test cases """

    def test_duration_year(self):
        prd = dateperiods.DatePeriod([2018], [2018])
        duration = prd.duration
        self.assertTrue(duration.is_year)
        self.assertFalse(duration.is_day)
        self.assertFalse(duration.is_isoweek)
        self.assertFalse(duration.is_month)
        self.assertEqual("P1Y", duration.isoformat)

    def test_duration_years(self):
        prd = dateperiods.DatePeriod([2018, 10], [2020, 9])
        duration = prd.duration
        self.assertFalse(duration.is_month)
        self.assertFalse(duration.is_day)
        self.assertFalse(duration.is_isoweek)
        self.assertFalse(duration.is_year)
        self.assertEqual("P2Y", duration.isoformat)

    def test_duration_month(self):
        prd = dateperiods.DatePeriod([2018, 4], [2018, 4])
        duration = prd.duration
        self.assertTrue(duration.is_month)
        self.assertFalse(duration.is_day)
        self.assertFalse(duration.is_isoweek)
        self.assertFalse(duration.is_year)
        self.assertEqual("P1M", duration.isoformat)

    def test_duration_months(self):
        prd = dateperiods.DatePeriod([2018, 10], [2019, 4])
        duration = prd.duration
        self.assertFalse(duration.is_month)
        self.assertFalse(duration.is_day)
        self.assertFalse(duration.is_isoweek)
        self.assertFalse(duration.is_year)
        self.assertEqual("P7M", duration.isoformat)

    def test_duration_isoweek(self):
        prd = dateperiods.DatePeriod([2018, 4, 2], [2018, 4, 8])
        duration = prd.duration
        self.assertTrue(duration.is_isoweek)
        self.assertFalse(duration.is_day)
        self.assertFalse(duration.is_month)
        self.assertFalse(duration.is_year)
        self.assertEqual("P7D", duration.isoformat, )

    def test_duration_day(self):
        prd = dateperiods.DatePeriod([2018, 4, 1], [2018, 4, 1])
        duration = prd.duration
        self.assertTrue(duration.is_day)
        self.assertFalse(duration.is_month)
        self.assertFalse(duration.is_isoweek)
        self.assertFalse(duration.is_year)
        self.assertEqual("P1D", duration.isoformat)

    def test_duration_custom(self):
        prd = dateperiods.DatePeriod([2018, 4, 1], [2018, 4, 2])
        duration = prd.duration
        self.assertFalse(duration.is_day)
        self.assertFalse(duration.is_month)
        self.assertFalse(duration.is_isoweek)
        self.assertFalse(duration.is_year)
        self.assertEqual("P2D", duration.isoformat)


class OverlapFunctionalityTestSuite(unittest.TestCase):
    """A standard list of test cases """

    def test_input_args(self):
        prd = dateperiods.DatePeriod([2018, 4], [2018, 4])
        self.assertRaises(TypeError, prd.has_overlap)
        self.assertRaises(ValueError, prd.has_overlap, 1)
        self.assertRaises(ValueError, prd.has_overlap, None)
        self.assertRaises(ValueError, prd.has_overlap, [])

    def test_full_overlap(self):
        prd = dateperiods.DatePeriod([2018, 4], [2018, 4])
        self.assertTrue(prd.has_overlap(dateperiods.DatePeriod([2018, 4], [2018, 4])))
        self.assertTrue(prd.has_overlap(dateperiods.DatePeriod([2018, 3], [2018, 4])))
        self.assertTrue(prd.has_overlap(dateperiods.DatePeriod([2018, 4], [2018, 5])))
        self.assertTrue(prd.has_overlap(dateperiods.DatePeriod([2018, 3], [2018, 5])))

    def test_partial_overlap(self):
        prd = dateperiods.DatePeriod([2018, 4, 15], [2018, 5, 15])
        self.assertTrue(prd.has_overlap(dateperiods.DatePeriod([2018, 4], [2018, 4])))
        self.assertTrue(prd.has_overlap(dateperiods.DatePeriod([2018, 5], [2018, 5])))
        self.assertTrue(prd.has_overlap(dateperiods.DatePeriod([2018, 4], [2018, 4, 15])))
        self.assertTrue(prd.has_overlap(dateperiods.DatePeriod([2018, 5, 15], [2018, 5])))
        self.assertTrue(prd.has_overlap(dateperiods.DatePeriod([2018, 4, 16], [2018, 4])))

    def test_no_overlap(self):
        prd = dateperiods.DatePeriod([2018, 4, 15], [2018, 5, 15])
        self.assertFalse(prd.has_overlap(dateperiods.DatePeriod([2018, 4], [2018, 4, 14])))
        self.assertFalse(prd.has_overlap(dateperiods.DatePeriod([2018, 5, 16], [2018, 5])))


class IntersectionFunctionalityTestSuite(unittest.TestCase):
    """A standard list of test cases """

    def test_input_args(self):
        prd = dateperiods.DatePeriod([2018, 4], [2018, 4])
        self.assertRaises(TypeError, prd.intersect)
        self.assertRaises(ValueError, prd.intersect, 1)
        self.assertRaises(ValueError, prd.intersect, None)
        self.assertRaises(ValueError, prd.intersect, [])

    def test_full_intersection(self):
        prd = dateperiods.DatePeriod([2018, 4], [2018, 4])
        prd_intersect = dateperiods.DatePeriod([2018, 2], [2018, 5])
        result = prd.intersect(prd_intersect)
        self.assertEqual(result.tcs.date, prd.tcs.date)
        self.assertEqual(result.tce.date, prd.tce.date)

    def test_partial_intersection(self):
        prd = dateperiods.DatePeriod([2018, 4], [2018, 4])
        # Test 1: period start earlier
        prd_intersect = dateperiods.DatePeriod([2018, 4, 15], [2018, 5])
        result = prd.intersect(prd_intersect)
        self.assertEqual(result.tcs.date, prd_intersect.tcs.date)
        self.assertEqual(result.tce.date, prd.tce.date)
        # Test 2: period ends later
        prd_intersect = dateperiods.DatePeriod([2018, 3], [2018, 4, 15])
        result = prd.intersect(prd_intersect)
        self.assertEqual(result.tcs.date, prd.tcs.date)
        self.assertEqual(result.tce.date, prd_intersect.tce.date)

    def test_empty_intersection(self):
        prd = dateperiods.DatePeriod([2018, 4], [2018, 4])
        prd_intersect = dateperiods.DatePeriod([2018, 3], [2018, 3])
        self.assertIsNone(prd.intersect(prd_intersect))
        prd_intersect = dateperiods.DatePeriod([2018, 5], [2018, 5])
        self.assertIsNone(prd.intersect(prd_intersect))


if __name__ == '__main__':
    unittest.main()
