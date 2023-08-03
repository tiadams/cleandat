import os
from unittest import TestCase

import pandas as pd

from cleandat.workflows import clean_date_entries


class Test(TestCase):

    TEST_DIR_PATH = os.path.dirname(os.path.realpath(__file__))

    df = pd.read_csv(os.path.join(TEST_DIR_PATH, "resources", 'test.csv'))

    def test_clean_date_entries(self):
        df_clean = clean_date_entries(self.df)
        self.assertEqual(pd.isna(df_clean['birth_date_year'])[10], True)
        self.assertEqual(pd.isna(df_clean['birth_date_year'])[13], True)
