""" OCR Comparison Module
"""

from __future__ import print_function
from __future__ import division
from builtins import range
from past.utils import old_div
import os

wl_path = os.path.join(os.path.dirname(__file__),"dict/linuxwords.txt")
wl = open(wl_path, "r").read().upper().split("\n")

def ocr(path):
    """ DIY OCR from scratch
    """
    from .memeocr import rawocr
    import meme_get.ocr.parse as parse
    parse.bds, parse.ccr = rawocr(path)
    return parse.guesscaption()


def ocrTesseract(path, thres=True, cfg="urban"):
    """ Tesseract OCR
    """
    from .memeocr import tesseract_ocr
    return tesseract_ocr(path, thres=thres, cfg=cfg)


def evalresult(t):
    """ Evaluate the quality of an ocr result
    """
    puncs = ".,!?"
    t = t.replace("\n", " ")
    for p in puncs:
        t = t.replace(p, " " + p)
    t = t.split(" ")
    score = 0.0
    for i in range(0, len(t)):
        if t[i] in wl:
            score += 1.0
    print(old_div(score, len(t)))
    return old_div(score, len(t))

def ocrcomp(path, *args):
    """ Sort a list of ocr functions by their quality
    """
    results = []
    for f in args:
        results.append((f, f(path)))
    return sorted(results, key=lambda x: evalresult(x[1]), reverse=True)