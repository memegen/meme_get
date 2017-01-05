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
    """ Enum for holding the origins of memes.

    Attributes:
    NA: Not available
    QUICKMEME: Representing quickmeme.com
    """
    NA = 0
    QUICKMEME = 1
    MEMEGENERATOR = 2

    @classmethod
    def string_to_enum(self, s):
        """ Conver string to a Origins Enum object
        Args:
            s (str): The string representing the name of the origin
        """
        if s.lower() == "quickmeme":
            return self.QUICKMEME
        elif s.lower() == "memegenerator":
            return self.MEMEGENERATOR
        else:
            return self.NA


class Meme(object):
    """ A class for representing memes

    This class provides a high-level abstraction for memes.

    Attributes:
        _pic_url (str): A string representing the url of the picture
        _caption (str): A string representing the caption of the meme
        _time (datetime object): The time of creation of the meme
        _origin (Orgins Enum): The origins enum object representing the origin
        _tags (list): A list of string representing the categories of the meme

    """

    def __init__(self, pic_url, time,
                 caption=None, raw_pic_url=None, origin=Origins.NA, tags=[],
                 score=-1):
        """ __init__ method for Meme class

        Args:
            pic_url (str): URL of the meme picture
            time (datetime object): Time of creation
            caption (str): The caption of the meme
            raw_pic_url (str): The url of the picture without caption
            origin (Origins Enum): The origin of the meme (website)
            tags (list): A list of strings representing tags
        """
        self._pic_url = pic_url
        self._caption = caption
        self._time = time
        self._raw_pic_url = raw_pic_url
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
        """ Return the meme's creation time
        """
        return self._time

    def get_raw_pic_url(self):
        """ Return the url of the meme's picture without caption
        """
        return self._raw_pic_url

    def get_origin(self):
        """ Return the origin of the meme
        """
        return self._origin

    def get_tags(self):
        """ Representing a list of tags for the meme
        """
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

    This class should be subclassed. The MemeSite is designed to keep
    all Memes in a cache file, so that even if the Python process is
    terminated, the next time we run the save process, we don't need
    to re-download all the memes from the Internet. The _meme_pool
    and _meme_deque store memes, but the users should not view the memes
    in them as constant, as operations on the object will change the memes
    inside the pool and deque.

    Attributes:
        _url (str): URL for the website hosting memes
        _max_tries (int): Max tries for http requests
        _meme_pool (set): A set containing stored memes
        _meme_deque (deque): A deque containing stored memes
        _last_update (datetime object): The time of last download of memes
        _cache_size (int): Number of memes stored on disk
        _maxcache_day (int): Max day of keeping the cache on disk
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

    def get_memes(self, num_memes):
        """ Return a list of memes
        """
        raise NotImplementedError("Implement in subclasses.")

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

    def _pop_memes(self, n):
        """ Pop number of memes out of the pool
        Return a list of memes
        """
        r = []
        for i in range(n):
            r.append(self._meme_deque.pop())
        return r

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
            file_obj.close()
            return data
        else:
            file_obj.close()
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
        file_obj.close()

    def _cache_expired(self):
        """ Check whether cache has expired. Also return false when cache doesn't exist
        """
        try:
            delta_time = datetime.datetime.now() \
                - self._read_update_time_from_cache()
            result = delta_time > datetime.timedelta(days=self._maxcache_day)

            if result:
                print("Cache has expired.")
            else:
                print("Cache is not expired.")

            return result
        except OSError:
            print("Cache does not exist.")
            return False

    def _no_cache(self):
        """ Check whether cache exists
        """
        fname = self._filename()
        result = os.path.isfile(fname)

        if result:
            print("Cache exists.")
        else:
            print("Cache does not exist.")

        return not result

    def _build_cache(self):
        """ Build cache
        """
        print("Building cache.")
        self._populate(self._cache_size)
        self._save_cache()

    def _populate(self):
        """ Populate the meme pool and deque
        """
        raise NotImplementedError("Implement in subclasses")

    def _read_data_tuple(self, t_data):
        """ Read in a data tuple and replace all the instance variables
        """
        raise NotImplementedError("Implement in subclasses.")

    def _read_update_time_from_cache(self):
        """ Read cache update time from cache file
        """
        raise NotImplementedError("Implement in subclasses.")

    def _write_data_tuple(self):
        """ Write all internal states to a data tuple
        """
        raise NotImplementedError("Implement in subclasses.")

    def _filename(self):
        """ Use SHA1 hashing algorithm to calculate a unique file name
        """
        raise NotImplementedError("Implement in subclasses.")

    def __repr__(self):
        return "Memesite URL:{:s} Pool:{!s} Update Time:{!s}"\
            .format(self._url,
                    self._meme_pool,
                    self._last_update)


class QuickMeme(MemeSite):
    """ The MemeSite subclass that deals with the quickmeme site.

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
        """
        # Check the time difference and whether the
        # cache has been created
        if self._no_cache() or self._cache_expired():
            self._build_cache()
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
                meme = Meme(urls[i], time, caption=texts[i][0],
                            origin=self._origin, tags=[texts[i][-1]])
                self._meme_pool.add(meme)
                self._meme_deque.appendleft(meme)

            result = self._pop_memes(self.num_memes)
            return result

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

        Args:
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

    def _filename(self):
        """ Use SHA1 hashing algorithm to calculate a unique file name
        """
        hashID = hashlib.sha1()
        hashID.update(repr(self._url).encode('utf-8'))

        # Create a file name with hexdecimal representation of the SHA1 hash
        file_name = "cache_{:s}.memecache".format(hashID.hexdigest())
        return file_name

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


class MemeGenerator(MemeSite):
    """ This class represents the memegenerator.net website
    """

    def __init__(self, cache_size=500, maxcache_day=1,
                 popular_type="Daily", timeout=20):
        """ The __init__ method for MemeGenerator class

        Args:
            cache_size (int): Number of memes stored as cache
            maxcache_day (int): Number of days until the cache expires
        """
        super(MemeGenerator, self).__init__(
            "http://www.memegenerator.net", cache_size, maxcache_day)
        self._origin = Origins.MEMEGENERATOR
        self._api = "http://version1.api.memegenerator.net/"
        self._method_entry = "Instances_Select_ByPopular"

        if popular_type == "Daily":
            self._popular_days = 1
        elif popular_type == "Weekly":
            self._popular_days = 7
        elif popular_type == "Monthly":
            self._popular_days = 30
        else:
            raise ValueError(
                "Wrong popular type. Supported: Daily, Weekly, Monthly")

        self._timeout = timeout
        self._origin = Origins.MEMEGENERATOR
        self._posts_per_page = 15
        if self._no_cache() or self._cache_expired():
            self._build_cache()

    def get_memes(self, num_memes):
        """ Get a number of memes from memegenerator.net
        """

        if self._no_cache() or self._cache_expired():
            self._build_cache()
        else:
            self._update_with_cache()

        if self._cache_size >= num_memes:
            return self._pop_memes(num_memes)
        else:
            result = self._pop_memes(self._cache_size)

            pnum = math.ceil(num_memes / self._posts_per_page)
            print("Last page: ", pnum)
            first_pnum = math.ceil(self._cache_size / self._posts_per_page)
            additional_memes = []

            # Get all the additional memes
            for i in range(first_pnum, pnum + 1):
                additional_memes = additional_memes + self._get_memes_helper(i)

            pre_index = self._cache_size % self._posts_per_page
            waste = self._posts_per_page * pnum - num_memes

            additional_memes = additional_memes[
                pre_index:len(additional_memes) - waste]

            result = result + additional_memes
            return result

    def _populate(self, num):
        """ Populate the meme pool and deque
        """
        max_page = math.ceil(num / self._posts_per_page)
        for i in range(1, max_page + 1):
            if i != max_page:
                self._memes_on_page(i, self._posts_per_page)
            else:
                self._memes_on_page(i, num % self._posts_per_page)

    def _get_memes_helper(self, page_num):
        """ Helper function for the get_memes() function

        Return a list of memes on the specified page given. This function
        uses the API of the memegenerator.net
        """
        url = self._api + self._method_entry
        payload = {"languageCode": "en",
                   "pageIndex": page_num, "days": self._popular_days}
        r = requests.get(url, params=payload, timeout=self._timeout)

        try:
            json_memes = r.json()
        except ValueError as err:  # cannot decode json
            sys.stderr.write("ERROR: {} \n".format(str(err)))

        cmemes = json_memes["result"]
        meme_list = []

        for x in cmemes:

            instance_image_url = ""
            try:
                instance_image_url = x["instanceImageUrl"]
            except KeyError:
                pass

            ccaption = x["text0"]
            try:
                extra = " --- " + x["text1"]
                ccaption += extra
            except TypeError:  # Returned json sometimes doesn't have text1
                pass

            imageUrl = ""
            try:
                imageUrl = x["imageUrl"]
            except KeyError:
                pass

            ctags = []
            try:
                ctags += [x["urlName"]]
            except KeyError:
                pass

            cscore = -1
            try:
                cscore = x["totalVotesScore"]
            except KeyError:
                pass

            cmeme = Meme(instance_image_url,
                         datetime.datetime.now(),
                         caption=ccaption,
                         raw_pic_url=imageUrl,
                         origin=self._origin,
                         tags=ctags,
                         score=cscore)
            meme_list.append(cmeme)

        return meme_list

    def _memes_on_page(self, page_num, n):
        """ Get num memes on page

        memegenerator.net has a convenient api that allows us to get memes
        in JSON format.
        API Documentation: http://version1.api.memegenerator.net/
        """

        if n > self._posts_per_page:
            return None

        # Use the helper function to get a list of memes on the page
        meme_list = self._get_memes_helper(page_num)

        for i in range(n):
            self._meme_pool.add(meme_list[i])
            self._meme_deque.appendleft(meme_list[i])

    def _filename(self):
        """ Override superclass _filename method

        The reason why we need to override is because for the
        memegenerator.net website, it ranks memes in different
        days duration: most popular in 1 day, 1 week and 1 month

        We want to have different caches for each case.
        """
        hashID = hashlib.sha1()
        hashID.update(repr(self._url).encode('utf-8'))
        hashID.update(repr(self._popular_days).encode('utf-8'))
        # Create a file name with hexdecimal representation of the SHA1
        # hash
        file_name = "cache_{:s}.memecache".format(hashID.hexdigest())
        return file_name

    def _write_data_tuple(self):
        """ Write all internal states to a data tuple
        """
        data = (self._url, self._max_tries, self._meme_pool,
                self._meme_deque, self._last_update, self._cache_size,
                self._maxcache_day, self._popular_days)
        return data

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
        self._popular_days = t_data[7]

    def _read_update_time_from_cache(self):
        """ Read cache update time from cache file
        """
        dtuple = self._read_cache()

        return dtuple[4]
