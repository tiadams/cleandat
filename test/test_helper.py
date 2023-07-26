from unittest import TestCase

from src.etl.helper import get_encoding


class Test(TestCase):

    def test_get_encoding(self):
        case1 = '1=m'
        case2 = '1->m'
        case3 = '1 - m'
        case4 = '1 : m'
        case5 = '1= m'
        case6 = '2 -> female'
        case7 = '3 = not specified'
        case8 = '7 R-CHOP'
        self.assertTupleEqual((1, 'm'), get_encoding(case1))
        self.assertTupleEqual((1, 'm'), get_encoding(case2))
        self.assertTupleEqual((1, 'm'), get_encoding(case3))
        self.assertTupleEqual((1, 'm'), get_encoding(case4))
        self.assertTupleEqual((1, 'm'), get_encoding(case5))
        self.assertTupleEqual((2, 'female'), get_encoding(case6))
        self.assertTupleEqual((3, 'not specified'), get_encoding(case7))
        self.assertTupleEqual(None, get_encoding(case8))
