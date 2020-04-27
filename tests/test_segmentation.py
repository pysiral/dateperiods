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

    def test_segment_lengths_months(self):
        prd = dateperiods.DatePeriod([2018, 3], [2018, 4])
        prds = prd.get_segments("month")
        self.assertEqual(prds.n_periods, 2)


if __name__ == '__main__':
    unittest.main()
