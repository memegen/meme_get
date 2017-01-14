meme_get
==========


meme_get is a library that provides a high-level abstraction for extracting memes from popular online websites. Currently, we support extracting memes from:

* `quickmeme.com <http://www.quickmeme.com/>`_
* `memegenerator.net <https://memegenerator.net/>`_
* `Memes subreddit <https://www.reddit.com/r/memes/>`_ from Reddit.

Here is a short example::

    >>> a = RedditMemes()
    >>> meme_list = a.get_memes(100)
    >>> for meme in meme_list:
    >>>     print(meme.get_title())
    

Quick Start
------------

To install ``meme_get``, you can use pip::

    pip install meme_get
    

Documentation
--------------

The API and documentation are hosted on `http://meme-get.readthedocs.io/en/latest/ <http://meme-get.readthedocs.io/en/latest/>`_