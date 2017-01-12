from __future__ import print_function
from __future__ import division
from builtins import range
from past.utils import old_div
import json

wl = open("dict/linuxwords.txt", "r").read().upper().split("\n")

# mock ocr functions:

# diy raw ocr from data without auto-correct


def ocr0(path):
    import parse
    parse.path = path
    fi = open("data/" + path.split("/")[-1].split(".")[0] + ".json", "r")
    js = json.loads(fi.read())
    parse.bds = js[0]
    parse.ccr = js[1]
    return parse.guesscaption(simple=True)


def ocr(path):
    """ DIY OCR from scratch
    """
    import memeocr as mo
    import parse
    parse.bds, parse.ccr = mo.rawocr(path)
    return parse.guesscaption()


def ocr1(path):
    """ DIY OCR from data
    """
    import parse
    parse.path = path
    fi = open("data/" + path.split("/")[-1].split(".")[0] + ".json", "r")
    js = json.loads(fi.read())
    parse.bds = js[0]
    parse.ccr = js[1]
    return parse.guesscaption()


def ocrTesseract(path, thres=True, cfg="urban"):
    """ Tesseract OCR
    """
    import memeocr as mo
    return mo.tesseract_ocr(path, thres=thres, cfg=cfg)


# evaluate the quality of an ocr result
def evalresult(t):
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

if __name__ == "__main__":
    # print ocr1("images/img11.jpg")

    print(ocrcomp("images/img6.jpg", ocr0, ocrTesseract))
