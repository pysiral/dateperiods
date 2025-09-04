# -*- coding: utf-8 -*-

"""
Test the exclude rules
"""

__author__ = "Stefan Hendricks <stefan.hendricks@awi.de>"


import unittest

from context import dateperiods


class ExcludeMonthInputTestSuite(unittest.TestCase):
    """ Testing the segmentation of Periods """

    def test_invalid_input_args(self):
        self.assertRaises(ValueError, dateperiods.ExcludeMonth, 0)
        self.assertRaises(ValueError, dateperiods.ExcludeMonth, 13)
        self.assertRaises(ValueError, dateperiods.ExcludeMonth, [0, 1, 2])
        self.assertRaises(ValueError, dateperiods.ExcludeMonth, ["a"])
        self.assertRaises(ValueError, dateperiods.ExcludeMonth, "a")
        self.assertRaises(ValueError, dateperiods.ExcludeMonth, [None])

    def test_input_args_to_list(self):
        exclude_rule = dateperiods.ExcludeMonth(1)
        self.assertTrue(exclude_rule.months == [1])

    def test_input_args_sort(self):
        test_list = [7, 6]
        exclude_rule = dateperiods.ExcludeMonth(test_list)
        self.assertTrue(exclude_rule.months == sorted(test_list))

    def test_correct_instance(self):
        test_list = [7, 6]
        exclude_rule = dateperiods.ExcludeMonth(test_list)
        period = dateperiods.DatePeriod([2023, 10], exclude_rule=exclude_rule)
        self.assertTrue(period.exclude_rule == exclude_rule)

    def test_correct_default_value(self):
        period = dateperiods.DatePeriod([2023, 10])
        self.assertIsInstance(period.exclude_rule, dateperiods.ExcludeRuleNotSet)


class ExcludeMonthApplyTestSuite(unittest.TestCase):
    """ Testing the segmentation of Periods """

    def test_monthly_periods(self):
        exclude_rule = dateperiods.ExcludeMonth([5, 6, 7, 8, 9])
        period = dateperiods.DatePeriod([2023, 10], [2024, 10], exclude_rule=exclude_rule)
        segments = period.get_segments("month")
        months = [segment.center.month for segment in segments]
        self.assertTrue(months == [10, 11, 12, 1, 2, 3, 4, 10])

    def test_daily_periods(self):
        exclude_rule = dateperiods.ExcludeMonth([5, 6, 7, 8, 9])
        period = dateperiods.DatePeriod([2024, 4, 16], [2024, 10, 15], exclude_rule=exclude_rule)
        segments = period.get_segments("day")
        self.assertTrue(segments.n_periods == 30)

    def test_isoweekly_periods(self):
        exclude_rule = dateperiods.ExcludeMonth([5, 6, 7, 8, 9])
        period = dateperiods.DatePeriod([2024, 4, 15], [2024, 10, 13], exclude_rule=exclude_rule)
        segments = period.get_segments("isoweek")
        print(segments)
        self.assertTrue(segments.n_periods == 4)


if __name__ == '__main__':
    unittest.main()
