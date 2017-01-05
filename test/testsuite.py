import unittest
from unittest import mock
from meme_get import memesites
from collections import deque
import json
import datetime


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

    @mock.patch('meme_get.memesites.requests.get', side_effect=lambda x: x)
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

    @mock.patch('meme_get.memesites.requests.get', side_effect=lambda x: x)
    def test_clean_meme_deque(self, mock_get):
        """ Test the clean meme deque function with mock requests.get
        """
        # Test with fake meme pool and no internet connection
        A = memesites.MemeSite("http://www.google.com")
        A._meme_deque = deque('abc')
        A.clean_meme_deque()
        self.assertTrue(A._meme_deque == deque())

    @mock.patch('meme_get.memesites.requests.get', side_effect=lambda x: x)
    def test_get_url(self, mock_get):
        """ Test the get url function

        The url returned by the get_url function should be the same
        as the url passed to the constructor at initialization
        """
        A = memesites.MemeSite("http://www.google.com")
        self.assertTrue("http://www.google.com" == A.get_url())

    @mock.patch('meme_get.memesites.requests.get', side_effect=lambda x: x)
    def test_get_meme_pool(self, mock_get):
        """ Test the get_meme_pool function
        """
        # Test with fake meme pool and no internet connection
        A = memesites.MemeSite("http://www.google.com")
        A._meme_pool = set('abc')

        self.assertTrue(A.get_meme_pool() == set('abc'))

    @mock.patch('meme_get.memesites.requests.get', side_effect=lambda x: x)
    def test_get_meme_num(self, mock_get):
        """ Test the get_meme_num function
        """
        A = memesites.MemeSite("1")
        A._meme_deque = deque('abc')
        self.assertTrue(A.get_meme_num() == 3)


class QuickMemeTest(unittest.TestCase):
    """ Unit test the quickmeme.com
    """

    def test_get_memes(self):
        pass


def mock_requests_get(*args, **kwargs):
    """ Mock requests.get() function for testing meme parsing functions.
    """
    class MockResponse(object):

        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):

            return self.json_data

    print(args)
    url = args[0]
    target_url = "http://version1.api.memegenerator.net/" \
                 "Instances_Select_ByPopular"

    with open('./test/memegenerator_sample.json') as data_file:
        mock_json_1 = json.load(data_file)

    print("Using mock requests get method.")
    print("URL: ", url)
    print("Target URL: ", target_url)

    if url == target_url:
        return MockResponse(mock_json_1, 200)
    else:
        return MockResponse('This is a mocking function.', 200)


def mock_get_memes(*args, **kwargs):
    """ Mock function for the get_memes function

    Create a phony list of Memes
    """
    a = []
    for i in range(args[0]):
        a.append(memesites.Meme(i, datetime.datetime.now(),
                                caption=str(i),
                                raw_pic_url=str(i),
                                origin=memesites.Origins.NA,
                                tags=[],
                                score=i))
    return a


class MemeGeneratorSiteTest(unittest.TestCase):
    """ Unit test the memegenerator.net
    """

    def test_get_memes(self):
        """ Test the get_memes() function of the MemeGenerator class
        """
        A = memesites.MemeGenerator()

        # Small prime number
        resultA_1 = A.get_memes(31)
        resultA_2 = A.get_memes(31)

        self.assertTrue(len(resultA_1) == 31)
        self.assertTrue(resultA_1 == resultA_2)

        # Size equals to cache size
        resultB_1 = A.get_memes(500)
        resultB_2 = A.get_memes(500)

        self.assertTrue(len(resultB_1) == 500)
        self.assertTrue(resultB_1 == resultB_2)

        # Size greater than cache size
        # This test runs longer
        resultC_1 = A.get_memes(510)
        resultC_2 = A.get_memes(510)

        # We need to do this because the uncached memes will have
        # Different creation times
        resultC_1 = [x.get_pic_url() for x in resultC_1]
        resultC_2 = [x.get_pic_url() for x in resultC_2]

        self.assertTrue(len(resultC_1) == 510)
        self.assertTrue(resultC_1 == resultC_2)

    @mock.patch('meme_get.memesites.requests.get',
                side_effect=mock_requests_get)
    def test_memes_on_page(self, mock_get):
        """ Testing the _memes_on_page() function of the MemeGenerator class
        """

        print("P1")
        A = memesites.MemeGenerator()
        # This the function call that will use the mock function
        A._memes_on_page(1, 10)
        self.assertTrue(len(A._meme_deque) == 10)

        # Open the json data file and see whether json data
        # was correctly interpreted
        with open('./test/memegenerator_sample.json') as data_file:
            json_data = json.load(data_file)

        control = json_data["result"]
        experiment = A._meme_deque

        # See whether the memes in the deque has the same data as the json file
        # and in the same sequence
        for x in control:
            try:
                a = experiment.pop()
                self.assertTrue(a.get_pic_url() == x["instanceImageUrl"])
                self.assertTrue(x["text0"] in a.get_caption())
            except IndexError:  # deque is already empty
                pass

    @mock.patch('meme_get.memesites.MemeGenerator.get_memes',
                side_effect=mock_get_memes)
    def test_get_captions(self, mock_get):
        """ Testing function for get_captions() functions on MemeGenerator class
        """
        A = memesites.MemeGenerator()

        a = A.get_captions(10)

        # Check whether the returned captions list is
        # consistent with the Memes fed into the class
        for i in range(len(a)):
            self.assertTrue(a[i] == str(i))


if __name__ == '__main__':
    unittest.main()
