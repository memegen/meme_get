import unittest
from unittest import mock
import memesites
from collections import deque


class MemeTest(unittest.TestCase):
    """ Test Class for Meme Class
    Only method that has name starts with test will be run
    """

    def test_init(self):
        """ Test the initialization routine of Meme class
        """
        A = memesites.Meme('1', '2')

        self.assertTrue(A.get_pic_url() == '1')
        self.assertTrue(A.get_time() == '2')
        self.assertTrue(A.get_caption() is None)
        self.assertTrue(A.get_origin() == memesites.Origins.NA)
        self.assertTrue(A.get_tags() == [])

    def test_eq(self):
        """ Test Meme class equality
        """
        A = memesites.Meme('1', '2')
        B = memesites.Meme('1', '3')
        C = memesites.Meme('1', '2')
        D = memesites.Meme('2', '3')
        self.assertTrue(A == A and B == B and C == C and D == D)
        self.assertTrue(A == C)
        self.assertFalse(A == B)
        self.assertFalse(A == D)
        self.assertFalse(B == D)

    def test_ne(self):
        """ Test Meme class __ne__ method
        """
        A = memesites.Meme('1', '2')
        B = memesites.Meme('1', '3')
        C = memesites.Meme('1', '2')
        D = memesites.Meme('2', '3')
        self.assertFalse(A != A and B != B and C != C and D != D)
        self.assertFalse(A != C)
        self.assertTrue(A != B)
        self.assertTrue(A != D)
        self.assertTrue(B != D)

    def test_hash(self):
        """ Test Meme class __hash__ method
        """
        A = memesites.Meme('1', '2')
        B = memesites.Meme('1', '3')
        C = memesites.Meme('1', '2')
        D = memesites.Meme('2', '3')
        self.assertTrue(len(set([A, B, C, D])) == 3)


class MemeSiteTest(unittest.TestCase):
    """ Test the MemeSite class
    """

    @mock.patch('memesites.requests.get', side_effect=lambda x: x)
    def test_clean_meme_pool(self, mock_get):
        """ Test the clean meme pool function with mock requests.get

        Mocked so that the requests package does not actually make
        http requests
        """
        # Test with fake meme pool and no internet connection
        A = memesites.MemeSite("http://www.google.com")
        A._meme_pool = set('abc')
        A.clean_meme_pool()
        self.assertTrue(A._meme_pool == set())

    @mock.patch('memesites.requests.get', side_effect=lambda x: x)
    def test_clean_meme_deque(self, mock_get):
        """ Test the clean meme deque function with mock requests.get
        """
        # Test with fake meme pool and no internet connection
        A = memesites.MemeSite("http://www.google.com")
        A._meme_deque = deque('abc')
        A.clean_meme_deque()
        self.assertTrue(A._meme_deque == deque())

    @mock.patch('memesites.requests.get', side_effect=lambda x: x)
    def test_get_url(self):
        """ Test the get url function

        The url returned by the get_url function should be the same
        as the url passed to the constructor at initialization
        """
        A = memesites.MemeSite("http://www.google.com")
        self.assertTrue("http://www.google.com" == A.get_url())

    @mock.patch('memesites.requests.get', side_effect=lambda x: x)
    def test_get_meme_pool(self):
        """ Test the get_meme_pool function
        """
        # Test with fake meme pool and no internet connection
        A = memesites.MemeSite("http://www.google.com")
        A._meme_deque = deque('abc')
        A.clean_meme_deque()
        self.assertTrue(A._meme_deque == deque())

    def test_cache(self):
        """ Test the _read_cache, and _save_cache functions
        Also test _read_data_tuple, _write_data_tuple and _filename
        """
        pass


class QuickMemeTest(unittest.TestCase):
    """ Unit test the quickmeme.com
    """

    def test_get_memes(self):
        pass


if __name__ == '__main__':
    unittest.main()
