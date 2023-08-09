import os
from unittest import TestCase

import pandas as pd

from cleandat.pipeline import TransformationPipeline
from cleandat.date import normalize_date_entries


class Test(TestCase):

    TEST_DIR_PATH = os.path.dirname(os.path.realpath(__file__))

    df = pd.read_csv(os.path.join(TEST_DIR_PATH, "resources", 'test.csv'))

    def test_pipeline_unknown_function(self):
        pipeline = TransformationPipeline(self.df)
        pipeline.add_task(normalize_date_entries, ['birth_date'])
        pipeline.run()
        pipeline.print_changelog()