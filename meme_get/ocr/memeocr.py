from __future__ import print_function
from __future__ import division

from builtins import range
from past.utils import old_div
import random
import json
import sys
import os
import enchant
import pyocr
import pyocr.builders
from PIL import Image, ImageDraw, ImageFont

path = "images/img8.jpg"

# characters to recognize
C = "ABCDEFGHIJKLMNOPQRSTUVWXYZ123456789"

# standard character glyphs
cimgs = []

# original image
IM = None
w, h = 0, 0
PX = None

# display layer
disp = None
draw = None

# threshold layer
thim = None
thpx = None
thdr = None

# character areas
areas = []
badareas = []


def loadimg(path):
    global IM, w, h, PX, disp, draw, thim, thpx, thdr
    # original image
    IM = Image.open(path)
    w, h = IM.size
    PX = IM.load()

    # display layer
    disp = Image.new("RGB", (w, h))
    draw = ImageDraw.Draw(disp)

    # threshold layer
    thim = Image.new("RGB", (w, h))
    thpx = thim.load()
    thdr = ImageDraw.Draw(thim)

def closeimg():
    """ Close all the image
    """
    IM.close()
    disp.close()
    thim.close()

# rgb(255,255,255) to hsv(360,1.0,1.0) conversion
def rgb2hsv(r, g, b):
    R = old_div(r, 255.0)
    G = old_div(g, 255.0)
    B = old_div(b, 255.0)
    cmax = max(R, G, B)
    cmin = min(R, G, B)
    delta = cmax - cmin
    H, S, V = 0, 0, 0
    if delta == 0:
        H = 0
    elif cmax == R:
        H = 60 * ((old_div((G - B), delta)) % 6)
    elif cmax == G:
        H = 60 * (old_div((B - R), delta) + 2)
    elif cmax == B:
        H = 60 * (old_div((R - G), delta) + 4)
    if cmax == 0:
        S = 0
    else:
        S = old_div(delta, cmax)
    V = cmax
    return H, S, V

# find the left cutoff of character glyph


def firstwhitex(im):
    fwx = im.size[0]
    px = im.load()
    for y in range(0, im.size[1]):
        for x in range(0, im.size[0]):
            r, g, b = px[x, y][:3]
            if (r, g, b) == (255, 255, 255):
                if x < fwx:
                    fwx = x
    return fwx

# been there


def visited(x, y, areas):
    for i in range(0, len(areas)):
        if (x, y) in areas[i]:
            return True
    return False

# floodfill from pixel


def flood(x, y, d):
    global areas
    area = []
    seeds = [(x, y)]
    while d > 0 and len(seeds) > 0:

        d -= 1
        if d == 0:
            # print "too large"
            badareas.append(area)
            return []
        x, y = seeds.pop()

        if visited(x, y, areas) or visited(x, y, badareas):
            # print "visited"
            return []

        if (d > 0 and x > 0 and x < w - 1 and y > 0 and y < h - 1):
            if not((x, y) in area):
                r, g, b = thpx[x, y][:3]

                if (r != 0):
                    area.append((x, y))
                    seeds += [(x, y), (x - 1, y), (x, y - 1),
                              (x + 1, y), (x, y + 1)]
    return area


# get all character areas
def getareas():
    for y in list(range(0, int(old_div(h, 4)), 10)) + list(range(int(3 * h / 4), h, 10)):
        print(y, "/", h)
        for x in range(0, w, 5):
            area = flood(x, y, 30000)
            # print area
            if len(area) > 1:
                col = (random.randrange(0, 255), random.randrange(
                    0, 255), random.randrange(0, 255))
                for i in range(0, len(area)):
                    draw.point(list(area[i]), fill=col)
                areas.append(area)

# boundaries of a character


def getbounds(area):
    xmin = area[0][0]
    xmax = area[0][0]
    ymin = area[0][1]
    ymax = area[0][1]
    for i in range(0, len(area)):
        if area[i][0] < xmin:
            xmin = area[i][0]
        if area[i][1] < ymin:
            ymin = area[i][1]
        if area[i][0] > xmax:
            xmax = area[i][0]
        if area[i][1] > ymax:
            ymax = area[i][1]
    return xmin - 1, ymin - 1, xmax + 1, ymax + 1

# draw a boundary


def drawbounds():
    bds = []
    for i in range(0, len(areas)):
        bd = getbounds(areas[i])
        bds.append(bd)
        draw.rectangle(bd, outline=(255, 0, 0))
    return bds


# OCR
def checkchars():
    scoreboard = []
    for i in range(0, len(areas)):
        print(i, "/", len(areas))
        bd = getbounds(areas[i])
        scores = []
        
        print(len(cimgs))

        for j in range(0, len(cimgs)):
            score = 0
            px = cimgs[j].load()
            score = 0
            sc = old_div((1.0 * (bd[3] - bd[1])), 100.0)
            for x in range(0, cimgs[j].size[0]):
                for y in range(0, cimgs[j].size[1]):
                    xp = min(int(x * sc + bd[0]), w - 1)
                    yp = min(int(y * sc + bd[1]), h - 1)

                    r1, g1, b1 = px[x, y][:3]
                    r2, g2, b2 = thpx[xp, yp][:3]

                    if (xp < bd[2]):
                        if (r1 == r2):
                            score += 1
                        else:
                            score -= 1
                    else:
                        if (r1 == 0):
                            score += 0
                        else:
                            score -= 1
            scores.append((C[j], old_div(int(score * 10), 10.0)))
        scoreboard.append(normalize(scores))
        draw.text((bd[0], bd[1] - 5), normalize(scores)[0][0], (0, 255, 255))
    return scoreboard


# normalize scores to 0.0-1.0
def normalize(scores):
    scores = sorted(scores, key=lambda x: x[1], reverse=True)

    ns = sorted(scores, key=lambda x: x[1], reverse=True)

    for i in range(0, len(scores)):

        if scores[i][1] <= 0 or scores[0][1] == 0:
            ns[i] = (scores[i][0], 0)
        else:
            n = old_div((scores[i][1] * 1.0), scores[0][1])
            ns[i] = (scores[i][0], old_div(int(n * 1000), 1000.0))

    return ns

# print OCR result


def showresult(scoreboard):
    for i in range(0, len(scoreboard)):
        print("".join([s[0] for s in scoreboard[i]]))

# make character glyphs


def makeglyphs():

    for i in range(0, len(C)):
        im = Image.new("RGB", (100, 110))
        dr = ImageDraw.Draw(im)
        font = ImageFont.truetype(os.path.join(os.path.dirname(__file__),"fonts/Impact.ttf"), 124)
        dr.text((0, -25), C[i], (255, 255, 255), font=font)

        fwx = firstwhitex(im)

        im = Image.new("RGB", (100, 110))
        dr = ImageDraw.Draw(im)
        font = ImageFont.truetype(os.path.join(os.path.dirname(__file__),"fonts/Impact.ttf"), 124)
        dr.text((-fwx, -26), C[i], (255, 255, 255), font=font)

        cimgs.append(im)

# make threshold image


def thresh():
    for x in range(0, w):
        for y in range(0, h):
            r, g, b = PX[x, y][:3]
            hsv = rgb2hsv(r, g, b)
            if (hsv[2] > 0.9)and hsv[1] < 0.1:
                thdr.point([x, y], fill=(255, 255, 255))
            else:
                thdr.point([x, y], fill=(0, 0, 0))

# returns possible characters and bounds in an image


def rawocr(path):
    global cimgs
    print("Starting ocr for {}".format(str(path)))
    # Clear glyphs
    cimgs = []

    loadimg(path)
    print("p0: ", len(cimgs))
    makeglyphs()

    print("p1: ", len(cimgs))
    thresh()
    # thim.show()
    getareas()
    bds = drawbounds()

    # disp.show()
    print("p2: ", len(cimgs))

    ccr = checkchars()
    showresult(ccr)
    # disp.show()
    closeimg()
    print("Finish OCR.")
    return bds, ccr


def tesseract_ocr_helper(base_image, config="Default"):
    """ A wrapper for using tesseract to do OCR
    """
    tools = pyocr.get_available_tools()
    if len(tools) == 0:
        print("No OCR tool found")
        sys.exit(1)

    # The tools are returned in the recommended order of usage
    tool = tools[0]
    print("Will use tool '%s'" % (tool.get_name()))

    langs = tool.get_available_languages()
    print("Available languages: %s" % ", ".join(langs))
    lang = langs[0]
    print("Will use lang '%s'" % (lang))

    custom_builder = pyocr.builders.TextBuilder()
    if config != "Default":
        custom_builder.tesseract_configs = [config]

    txt = tool.image_to_string(
        base_image,
        lang=lang,
        builder=custom_builder
    )

    # Spell correct
    dict_path = os.path.join(os.path.dirname(__file__),"dict/urban_dict.txt")
    d = enchant.DictWithPWL("en_US", dict_path)
    txtA = txt.replace('\n', ' \n ')
    A = txtA.split(" ")
    B = []

    for x in A:
        if (x != '\n' and len(x) != 0
                and d.check(x) is False
                and len(d.suggest(x)) != 0):
            B.append(d.suggest(x)[0])
        else:
            B.append(x)

    return " ".join(B)


def tesseract_ocr(path, thres=False, cfg="Default"):
    """ Wrapper for tesseract OCR
    """
    loadimg(path)
    if thres:
        thresh()
        result = tesseract_ocr_helper(thim, config=cfg)
        return result
    else:
        result = tesseract_ocr_helper(IM, config=cfg)
        return result


if __name__ == "__main__":
    bds, ccr = rawocr(path)

    js = json.dumps([bds, ccr])
    fo = open("data/" + path.split("/")[-1].split(".")[0] + ".json", "w")
    fo.write(js)
