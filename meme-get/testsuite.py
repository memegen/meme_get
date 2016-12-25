import unittest
import memesites


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

    def test_clean_meme_pool(self):
        pass

    def test_clean_meme_deque(self):
        pass

    def test_get_url(self):
        pass

    def test_get_meme_pool(self):
        pass

    def test_cache(self):
        """ Test the _read_cache, and _save_cache functions
        Also test _read_data_tuple, _write_data_tuple and _filename
        """
        pass


if __name__ == '__main__':
    unittest.main()
