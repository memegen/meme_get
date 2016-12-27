# Classes related to getting memes from sites
# Currently support: quickmeme.com
import requests
import sys
import bs4
import datetime
import pickle
import hashlib
import math
import os.path
from enum import Enum
from collections import deque


class Origins(Enum):
    NA = 0
    QUICKMEME = 1

    @classmethod
    def string_to_enum(self, str):
        if str.lower() == "quickmeme":
            return self.QUICKMEME
        else:
            return self.NA


class Meme(object):
    """ A class for storing memes
    """

    def __init__(self, pic_url, time,
                 caption=None, origin=Origins.NA, tags=[]):
        self._pic_url = pic_url
        self._caption = caption
        self._time = time
        self._origin = Origins.NA
        self._tags = tags

    def get_pic_url(self):
        """ Get url to the picture
        """
        return self._pic_url

    def get_caption(self):
        """ Get caption of the meme
        """
        return self._caption

    def get_time(self):
        return self._time

    def get_origin(self):
        return self._origin

    def get_tags(self):
        return self._tags

    def __hash__(self):
        """ Two memes are the same if they have the same urls and the same capture time
        """
        return hash((self._pic_url, self._time))

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return (self._pic_url == other._pic_url
                    and self._time == other._time)
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return not self == other
        return NotImplemented

    def __repr__(self):
        return "Meme URL:{:s} Time:{!s} Caption:{!s} Origin:{!s} Tags:{!s}"\
            .format(self._pic_url,
                    self._time,
                    self._caption,
                    self._origin,
                    self._tags)


class MemeSite(object):
    """ A base class for any sites with respect to memes
    For each site class, the meme posts are stored in the following format:

    All the memes are stored in sets
    For each meme: it has the following properties:
    - picture url
    - caption,
    - time captured.
    - origin
    """

    def __init__(self, url, cache_size=500, maxcache_day=1):
        self._url = url
        self._max_tries = 10
        self._meme_pool = set()
        self._meme_deque = deque()
        self._last_update = datetime.datetime.now()
        self._cache_size = cache_size
        self._maxcache_day = maxcache_day

        try:
            self._main_page = requests.get(url)
        except Exception as err:
            sys.stderr.write("ERROR: {} \n".format(str(err)))

    def clean_meme_pool(self):
        """ Empty the meme pool
        """
        self._meme_pool = set()

    def clean_meme_deque(self):
        """ Empty the meme deque
        """
        self._meme_deque.clear()

    def get_url(self):
        """ Return the base url
        """
        return self._url

    def get_meme_pool(self):
        """ Return a set of memes
        """
        return self._meme_pool

    def get_meme_num(self):
        """ Return the number of memes we have
        """
        return len(self._meme_deque)

    def get_unique_meme_num(self):
        """ Return the number of unique memes we have
        """
        return len(self._meme_pool)

    def _read_cache(self):
        """ Read the saved cache file (no side effects)
        Read a tuple containing the data
        """
        fname = self._filename()

        if os.path.isfile(fname):
            # Read the file in using Pickle
            file_obj = open(fname, 'rb')
            data = pickle.load(file_obj)
            # print(data)
            # self._read_data_tuple(data)
            return data
        else:
            raise OSError("No cache exists.")

    def _update_with_cache(self):
        """ Update self states with cache
        """
        data = self._read_cache()
        self._read_data_tuple(data)

    def _save_cache(self):
        """ Save the class to cache files

        We put all the variables into a tuple, and then save that tuple
        using pickle.
        """
        # Store all the variables into a tuple
        # Save the data to a file with a unique name
        file_obj = open(self._filename(), 'wb')
        pickle.dump(self._write_data_tuple(), file_obj)

    def _read_data_tuple(self, t_data):
        """ Read in a data tuple and replace all the instance variables
        """
        self._url = t_data[0]
        self._max_tries = t_data[1]
        self._meme_pool = t_data[2]
        self._meme_deque = t_data[3]
        self._last_update = t_data[4]
        self._cache_size = t_data[5]
        self._maxcache_day = t_data[6]

    def _read_update_time_from_cache(self):
        """ Read cache update time from cache file
        """
        dtuple = self._read_cache()

        return dtuple[4]

    def _write_data_tuple(self):
        """ Write all internal states to a data tuple
        """
        data = (self._url, self._max_tries, self._meme_pool,
                self._meme_deque, self._last_update, self._cache_size,
                self._maxcache_day)
        return data

    def _filename(self):
        """ Use SHA1 hashing algorithm to calculate a unique file name
        """
        hashID = hashlib.sha1()
        hashID.update(repr(self._url).encode('utf-8'))

        # Create a file name with hexdecimal representation of the SHA1 hash
        file_name = "cache_{:s}".format(hashID.hexdigest())
        return file_name

    def __repr__(self):
        return "Memesite URL:{:s} Pool:{!s} Update Time:{!s}"\
            .format(self._url,
                    self._meme_pool,
                    self._last_update)


class QuickMeme(MemeSite):
    """ The class that deals with the quickmeme site.

    Remarks:
    quickmeme.com uses an infinite scrolling homepage.
    Fortunately, we can also access the later pages by
    just going to the url:

    www.quickmeme.com/page/i/, where i is the page number
    each page contains 10 user posts; each post consists
    of an image and an alternative text
    """

    def __init__(self, cache_size=500, maxcache_day=1):
        super(QuickMeme, self).__init__(
            "http://www.quickmeme.com/", cache_size, maxcache_day)
        self._posts_per_page = 10
        self._origin = Origins.QUICKMEME

        if self._no_cache() or self._cache_expired():
            self._build_cache()

    def get_memes(self, num_memes):
        """
        Get a number of memes from Quickmeme.com

        1) Check the last update time. Find time difference
        """
        # Check the time difference
        if self._no_cache() or self._cache_expired():
            self._build_cache(self.cache_size)
        else:
            # Read in saved memes
            self._update_with_cache()

        # Check whether we have enough memes
        if self._cache_size >= num_memes:
            return self._pop_memes(num_memes)
        else:
            # Find the page number of the last page
            pnum = math.ceil(num_memes / self._posts_per_page)

            curl = self._url + "page/{:d}/".format(pnum)
            cpage = requests.get(curl)
            csoup = bs4.BeautifulSoup(cpage.text, 'html.parser')
            # Extract posts from current page
            meme_posts = csoup.find_all(
                class_="post-image", limit=num_memes % self._posts_per_page)

            # Extract captions and picture urls from posts
            texts = [str(x['alt']).rpartition("  ") for x in meme_posts]
            urls = [str(x['src']) for x in meme_posts]

            # Get the additional memes
            # Start from the meme after the last one in cache
            for i in range(self._cache_size % self._posts_per_page,
                           len(meme_posts)):
                time = datetime.datetime.now()
                meme = Meme(urls[i], time, texts[i][0],
                            self._origin, [texts[i][-1]])
                self._meme_pool.add(meme)
                self._meme_deque.appendleft(meme)

            result = self._pop_memes(self._cache_size)
            return result

    def _pop_memes(self, n):
        """ Pop number of memes out of the pool
        Return a list of memes
        """
        r = []
        for i in range(n):
            r.append(self._meme_deque.pop())
        return r

    def _cache_expired(self):
        """ Check whether cache has expired. Also return false when cache doesn't exist
        """
        try:
            delta_time = datetime.datetime.now() \
                - self._read_update_time_from_cache()
            return delta_time > datetime.timedelta(days=self.maxcache_day)
        except OSError:
            return False

    def _no_cache(self):
        """ Check whether cache exists
        """
        fname = self._filename()
        return os.path.isfile(fname)

    def _build_cache(self):
        """ Build cache
        """
        self._populate(self._cache_size)
        self._save_cache()

    def _populate(self, num):
        """ Populate the meme pool and deques
        """
        # Each page on quickmeme contains 10 meme posts
        # So the number of pages to crawl is:
        # num_memes / posts_per_page + mod ( num_memes, posts_per_page)
        max_page = math.ceil(num / self._posts_per_page)
        for i in range(1, max_page + 1):
            if i != max_page:
                self._memes_on_page(i, self._posts_per_page)
            else:
                self._memes_on_page(i, num % self._posts_per_page)

        # Current date and time
        self._last_update = datetime.datetime.now()

    def _memes_on_page(self, page_num, n):
        """Get n memes from page_num page

        Remarks:
        For the meme deque, we put memes in from the left side.
        If we want to retrieve memes from the most popular to the least,
        we pop from the right side (FIFO). If we want to retrieve memes
        the other way around, we pop from the left side (FILO).

        We also use set so that we can keep a unique collection of memes.

        Keyword Arguments:
        page_num -- the number of page we would like to retrieve
        n -- the number of memes we would like to retrieve from that page
        """
        if n > self._posts_per_page:
            return None

        curl = self._url + "page/{:d}/".format(page_num)
        cpage = requests.get(curl)
        csoup = bs4.BeautifulSoup(cpage.text, 'html.parser')
        # Extract posts from current page
        meme_posts = csoup.find_all(class_="post-image", limit=n)

        # Extract captions and picture urls from posts
        texts = [str(x['alt']).rpartition("  ") for x in meme_posts]
        urls = [str(x['src']) for x in meme_posts]

        # Populate the _meme_pool
        for i in range(len(meme_posts)):
            time = datetime.datetime.now()
            meme = Meme(urls[i], time, texts[i][0],
                        self._origin, [texts[i][-1]])
            self._meme_pool.add(meme)
            self._meme_deque.appendleft(meme)
