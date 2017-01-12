from __future__ import print_function
from __future__ import division
# pylint: disable=C0103
# pair letters in words with similar spelling


from builtins import range
from past.utils import old_div
def wordpair(w1, w2):
    result = []
    l = min(len(w1), len(w2))
    while len(w1) > 0 and len(w2) > 0:
        # print result
        if w1[0] == w2[0]:
            result.append((w1[0], w2[0]))
            w1 = w1[1:]
            w2 = w2[1:]
        else:
            ws = [w1, w2]
            xs = [len(w1), len(w2)]
            for n in range(1, 5):
                for i1, i2 in [(0, 1), (1, 0)]:
                    found = False
                    for j in range(len(ws[i1])):
                        for k in range(j, min(j + n, len(ws[i2]))):
                            if ws[i1][j] == ws[i2][k]:

                                if abs(j - k) + (j + k) < abs(xs[i1] - xs[i2]) + (xs[i1] + xs[i2]):
                                    xs[i1] = j
                                    xs[i2] = k
                                found = True
                                break
                        if found == True:
                            break
            x1, x2 = xs

            result.append((w1[:x1], w2[:x2]))
            w1 = w1[x1:]
            w2 = w2[x2:]
    if len(w1) > 0 or len(w2) > 0:
        result.append((w1[:], w2[:]))
    return result

# pretty print result of wordpair


def printwordpair(wp):
    l1 = ""
    l2 = ""
    for w in wp:
        l1 += w[0] + "\t"
        l2 += w[1] + "\t"
    return l1 + "\n" + l2 + "\n"

# test wordpair with function f


def testwordpair(f):
    print(f(wordpair("president", "precedent")))
    print(f(wordpair("affection", "affectation")))
    print(f(wordpair("eminent", "immanent")))
    print(f(wordpair("principal", "principle")))
    print(f(wordpair("desert", "dessert")))
    print(f(wordpair("deed", "indeed")))
    print(f(wordpair("immense", "intense")))
    print(f(wordpair("drastic", "dramatic")))
    print(f(wordpair("emulsion", "emotion")))
    print(f(wordpair("wikipedia", "vvil<ieolix")))

# similarity of a word pair


def wordsim(wp):
    return sum([w[0] == w[1] for w in wp]) * 1.0 / sum([old_div((len(w[0]) + len(w[1])), 2.0) for w in wp])


if __name__ == "__main__":
    testwordpair(printwordpair)
    testwordpair(wordsim)
