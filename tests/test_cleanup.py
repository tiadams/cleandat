import os
from unittest import TestCase

import numpy as np
import pandas as pd

from cleandat.cleanup import unify_number_format, clean_unknown_entries, \
    remove_entries_with_inconsistent_datatypes


class Test(TestCase):

    TEST_DIR_PATH = os.path.dirname(os.path.realpath(__file__))

    df = pd.read_csv(os.path.join(TEST_DIR_PATH, "resources", 'test.csv'))

    def test_unify_number_format(self):
        df_clean = unify_number_format(self.df)
        self.assertEqual(1500000, np.average(df_clean['cell_count'][9:16]))
        self.assertEqual(120000000, df_clean['cell_count'][17])

    def test_clean_unknown_entries(self):
        df_clean = clean_unknown_entries(self.df)
        self.assertEqual(pd.isna(df_clean['birth_date'])[13], True)
        self.assertEqual(pd.isna(df_clean['birth_date'])[23], True)
        self.assertEqual(pd.isna(df_clean['birth_date'])[24], True)
        self.assertEqual(pd.isna(df_clean['freetext'])[22], True)
        self.assertEqual(pd.isna(df_clean['freetext'])[27], True)

    def test_remove_entries_with_inconsistent_datatypes(self):
        df_clean = remove_entries_with_inconsistent_datatypes(self.df, threshold=0.5)
        self.assertEqual(pd.isna(df_clean['sex'])[19], True)