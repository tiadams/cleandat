import os
from datetime import datetime
from unittest import TestCase

import pandas as pd

from date import identify_date_columns, clean_date_entries


class Test(TestCase):

    TEST_DIR_PATH = os.path.dirname(os.path.realpath(__file__))

    df = pd.read_csv(os.path.join(TEST_DIR_PATH, "resources", 'test.csv'))

    def test_identify_date_columns(self):
        date_columns = identify_date_columns(self.df)
        self.assertListEqual(['birth_date'], date_columns)

    def test_clean_date_entries(self):
        df_cleaned = clean_date_entries(self.df, ['birth_date'])
        self.assertEqual(pd.isna(df_cleaned['birth_date'])[10], True)
        self.assertEqual(df_cleaned['birth_date'][9], datetime(2020, 4, 12, 0, 0))
        self.assertEqual(df_cleaned['birth_date'][11], datetime(2021, 6, 4, 0, 0))
        self.assertEqual(df_cleaned['birth_date'][12], datetime(1990, 2, 2, 0, 0))
        self.assertEqual(df_cleaned['birth_date'][26], datetime(1999, 9, 9, 0, 0))