import os
from unittest import TestCase

import pandas as pd

from clinical_etl_toolbox.cleanup import unify_number_format


class Test(TestCase):

    TEST_DIR_PATH = os.path.dirname(os.path.realpath(__file__))

    df = pd.read_csv(os.path.join(TEST_DIR_PATH, "resources", 'test.csv'))

    def test_unify_number_format(self):
        df_clean = unify_number_format(self.df)
        test = str("10^8").isnumeric()