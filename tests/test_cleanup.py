import os
from unittest import TestCase

import numpy as np
import pandas as pd

from clinical_etl_toolbox.cleanup import unify_number_format


class Test(TestCase):

    TEST_DIR_PATH = os.path.dirname(os.path.realpath(__file__))

    df = pd.read_csv(os.path.join(TEST_DIR_PATH, "resources", 'test.csv'))

    def test_unify_number_format(self):
        df_clean = unify_number_format(self.df)
        self.assertEqual(1500000, np.average(df_clean['cell_count'][9:16]))