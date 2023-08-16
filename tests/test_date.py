import os
from datetime import datetime
from unittest import TestCase

import pandas as pd

from cleandat.date import identify_date_columns, normalize_date_entries, decompose_date_entries, \
    create_durational_column


class Test(TestCase):

    TEST_DIR_PATH = os.path.dirname(os.path.realpath(__file__))

    df = pd.read_csv(os.path.join(TEST_DIR_PATH, "resources", 'test.csv'))

    def test_identify_date_columns(self):
        date_columns = identify_date_columns(self.df.copy())
        self.assertEqual(len(date_columns), 1)
        self.assertEqual(date_columns[0], 'birth_date')

    def test_clean_date_entries(self):
        df_cleaned = normalize_date_entries(self.df.copy(), ['birth_date'])
        self.assertEqual(pd.isna(df_cleaned['birth_date'])[10], True)
        self.assertEqual(df_cleaned['birth_date'][9], datetime(2020, 4, 12, 0, 0))
        self.assertEqual(df_cleaned['birth_date'][11], datetime(2021, 6, 4, 0, 0))
        self.assertEqual(df_cleaned['birth_date'][12], datetime(1990, 2, 2, 0, 0))
        self.assertEqual(df_cleaned['birth_date'][26], datetime(1999, 9, 9, 0, 0))

    def test_decompose_date_entries(self):
        df_dates_clean = pd.read_csv(os.path.join(os.path.dirname(os.path.realpath(__file__)), "resources",
                                                  'test_dates_cleaned.csv'))
        df_decomposed = decompose_date_entries(df_dates_clean, ['birth_date'])
        self.assertEqual(df_decomposed['birth_date_year'][9], 2020)
        self.assertEqual(df_decomposed['birth_date_month'][9], 4)
        self.assertEqual(df_decomposed['birth_date_day'][9], 12)
        self.assertEqual(df_decomposed['birth_date_year'][11], 2021)
        self.assertEqual(df_decomposed['birth_date_month'][11], 6)
        self.assertEqual(df_decomposed['birth_date_day'][11], 4)
        self.assertEqual(df_decomposed['birth_date_year'][12], 1990)
        self.assertEqual(df_decomposed['birth_date_month'][12], 2)
        self.assertEqual(df_decomposed['birth_date_day'][12], 2)
        self.assertEqual(df_decomposed['birth_date_year'][26], 1999)
        self.assertEqual(df_decomposed['birth_date_month'][26], 9)
        self.assertEqual(df_decomposed['birth_date_day'][26], 9)