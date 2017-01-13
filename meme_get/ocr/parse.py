from __future__ import print_function
from __future__ import division
from builtins import range
from past.utils import old_div
import json
import itertools
import meme_get.ocr.util as util
import warnings
import os


# loads raw ocr data
#path = "images/img5.jpg"
# fi = open("data/" + path.split("/")[-1].split(".")[0] + ".json", "r")
#js = json.loads(fi.read())
bds = None
ccr = None
#bds = js[0]
#ccr = js[1]

# dictionary
#wl = open("dict/linuxwords.txt", "r").read().upper().split("\n")

wl_path = os.path.join(os.path.dirname(__file__),"dict/linuxwords.txt")
wl = open(wl_path, "r").read().upper().split("\n")


# format raw ocr data
def guessformat():
    result = ""
    lines = []
    for i in range(0, len(bds)):
        found = 0
        for j in range(0, len(lines)):
            if len(lines[j]) > 0:
                if abs(bds[i][1] - old_div(sum([bds[l][1] for l in lines[j]]), len(lines[j]))) < 5:
                    lines[j].append(i)
                    found = 1
                    break
        if found == 0:
            lines.append([i])

    for i in range(0, len(lines)):
        lines[i] = sorted(lines[i], key=lambda x: bds[x][0])
    lines = sorted(lines, key=lambda x: bds[x[0]][1])

    for j in range(0, len(lines)):
        l = lines[j]
        nl = []
        for i in range(0, len(l)):
            nl.append(l[i])
            if i < len(l) - 1:
                if bds[l[i + 1]][0] - bds[l[i]][2] > 0.3 * sum([bds[k][2] - bds[k][0] for k in l]) / len(l):
                    nl.append(" ")
            if bds[l[i]][3] - bds[l[i]][1] < 0.5 * sum([bds[k][3] - bds[k][1] for k in l]) / len(l):
                nl.pop()
                nl.append("'")
            elif bds[l[i]][3] - bds[l[i]][1] < 0.9 * sum([bds[k][3] - bds[k][1] for k in l]) / len(l):
                nl.pop()
                if ccr[l[i]][0][0] == "I" or ccr[l[i]][0][0] == "J":
                    nl.append("!")
                else:
                    nl.append("?")
        lines[j] = nl

    return lines


# guess a line of text
def guessline(line, simple=False):
    words = [[]]
    for i in line:
        if i == " ":
            words.append([])
        elif i == "?" or i == "!":
            words.append(i)
        else:
            if type(words[-1]) == list:
                words[-1].append(i)
            else:
                words.append([i])
    for i in range(0, len(words)):
        if type(words[i]) == list:
            words[i] = guessword(words[i], simple)
    return " ".join(words)

# sort possible corrections


def sortchange(word):
    changes = []
    for w in word:
        if type(w) == int:
            for i in range(1, len(ccr[w])):
                changes.append((w, ccr[w][i]))

    changes = sorted(changes, key=lambda x: x[1][1])
    return changes


# guess a word
def guessword(w, simple=False):
    word = w[:]
    changes = {}
    pot = sortchange(word)

    guess = ""
    for i in range(0, len(word)):
        if type(word[i]) == int:
            word[i] = (word[i], ccr[word[i]][0][0])
        else:
            word[i] = (-1, word[i])

    guess = "".join([w[1] for w in word])
    guess0 = guess

    if simple:
        return guess0

    def ind(word, i):
        for j in range(0, len(word)):
            if word[j][0] == i:
                return j
        return -1

    while guess not in wl:
        if len(pot) == 0 or pot[-1][1][1] < 0.8:
            return guess0
        nc = pot.pop()
        if nc[0] not in list(changes.keys()):
            changes[nc[0]] = []
        changes[nc[0]].append(nc)

        chco = util.allchoice(list(changes.values()))

        for c in chco:
            newword = word[:]
            for d in c:

                newword[ind(newword, d[0])] = (d[0], d[1][0])

            guess = "".join([w[1] for w in newword])
            # print guess
            if guess in wl:
                return guess

    return guess

# check if some text is noise


def isgibber(t):
    if len(t) < 3:
        return True
    if len(t) < 4 and " " in t:
        return True
    if t.count(" ") > old_div(len(t), 3):
        return True

    return False

# guess the caption of a meme


def guesscaption(simple=False):
    output = ""
    gf = guessformat()

    print("raw: ")
    for g in gf:
        print(guessline(g, True))
    print()

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        for g in gf:
            gl = guessline(g, simple=simple)
            if not isgibber(gl):
                output += gl.replace(" !", "!").replace(" ?", "?") + "\n"

    return output

if __name__ == "__main__":
    print(guesscaption())
