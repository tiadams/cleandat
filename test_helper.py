from unittest import TestCase

from helper import get_encoding


class Test(TestCase):

    def test_get_encoding(self):
        case1 = '1=m'
        case2 = '1->m'
        case3 = '1 - m'
        case4 = '1 : m'
        case5 = '1= m'
        self.assertTupleEqual(('1', 'm'), get_encoding(case1))
        self.assertTupleEqual(('1', 'm'), get_encoding(case2))
        self.assertTupleEqual(('1', 'm'), get_encoding(case3))
        self.assertTupleEqual(('1', 'm'), get_encoding(case4))
        self.assertTupleEqual(('1', 'm'), get_encoding(case5))
