import os
from unittest import TestCase

import pandas as pd

from cleandat.encoding import get_encoding, identify_descriptive_header_cells, \
    identify_descriptive_header_rows, get_column_encoding_schemes, encode_dataframe


class Test(TestCase):

    TEST_DIR_PATH = os.path.dirname(os.path.realpath(__file__))

    df = pd.read_csv(os.path.join(TEST_DIR_PATH, "resources", 'test.csv'))

    def test_get_encoding_return_encoding(self):
        case1 = '1=m'
        case2 = '1->m'
        case3 = '1 - m'
        case4 = '1 : m'
        case5 = '1= m'
        case6 = '2 -> female'
        case7 = '3 = not specified'
        self.assertTupleEqual(('m', 1), get_encoding(case1))
        self.assertTupleEqual(('m', 1), get_encoding(case2))
        self.assertTupleEqual(('m', 1), get_encoding(case3))
        self.assertTupleEqual(('m', 1), get_encoding(case4))
        self.assertTupleEqual(('m', 1), get_encoding(case5))
        self.assertTupleEqual(('female', 2), get_encoding(case6))
        self.assertTupleEqual(('not specified', 3), get_encoding(case7))

    def test_get_encoding_reverse_order(self):
        case1 = "m:1"
        self.assertTupleEqual(('m', 1), get_encoding(case1))

    def test_get_encoding_return_none(self):
        case1 = '7 R-CHOP'
        case2 = '1'
        self.assertEqual(None, get_encoding(case1))
        self.assertEqual(None, get_encoding(case2))

    def test_identify_descriptive_header_cells(self):
        headers_bool = identify_descriptive_header_cells(self.df)
        self.assertEqual(headers_bool['sex'][:1].all(), True)
        self.assertEqual(pd.isnull(headers_bool['sex'][2:8]).all(), True)
        self.assertEqual(headers_bool['sex'][9:16].all(), False)
        self.assertEqual(pd.isnull(headers_bool['sex'][17]), True)
        self.assertEqual(headers_bool['sex'][18:28].all(), False)
        self.assertEqual(headers_bool['categories'][0:3].all(), True)

    def test_identify_descriptive_header_rows(self):
        header_rows = identify_descriptive_header_rows(self.df)
        self.assertEqual(len(header_rows), 3)
        self.assertEqual(header_rows, [0, 1, 2])

    def test_get_column_encoding_schemes(self):
        schemes = get_column_encoding_schemes(self.df)
        # TODO: this includes a false positive at pos 3
        self.assertEqual(3, len(schemes))
        self.assertEqual(2, len(schemes['sex']))
        self.assertEqual(3, len(schemes['categories']))

    def test_encode_dataframe(self):
        encoding_scheme = {'sex': {'m': 1, 'f': 2}, 'categories': {'foo': 1, 'bar': 2, 'foobar': 3}}
        df_encoded = encode_dataframe(self.df, encoding_scheme)
        self.assertEqual(1, (df_encoded['sex'][27]))
        self.assertEqual(1, (df_encoded['sex'][28]))
        self.assertEqual(2, df_encoded['categories'][17])
        self.assertEqual(1, df_encoded['categories'][27])
        self.assertEqual(3, df_encoded['categories'][15])


