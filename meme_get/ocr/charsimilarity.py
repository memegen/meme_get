from __future__ import print_function
#pylint: disable=C0103

from builtins import range
from PIL import Image, ImageDraw, ImageFont
import memeocr as mo
import json


def charsim():
    result = {}
    cimgs = mo.cimgs
    C = mo.C

    for i in range(0, len(cimgs)):
        print(C[i])
        scores = []
        px1 = cimgs[i].load()
        for j in range(0, len(cimgs)):
            if i != j:
                score = 0
                px2 = cimgs[j].load()
                for x in range(0, cimgs[i].size[0]):
                    for y in range(0, cimgs[i].size[1]):
                        if x >= cimgs[j].size[0] or y >= cimgs[j].size[1]:
                            score -= 1
                        if px1[x, y][:3] == px2[x, y][:3]:
                            score += 1
                        else:
                            score -= 1
                scores.append((C[j], score))
        ns = mo.normalize(scores)
        result[C[i]] = {}
        for n in ns:
            result[C[i]][n[0]] = n[1]

    return result

if __name__ == "__main__":
    mo.makeglyphs()
    js = json.dumps(charsim(), sort_keys=True)
    f1 = open("similarity.json", "w")
    f1.write(js)
