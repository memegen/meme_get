#pylint: disable=C0103

from builtins import range
def allchoice(L):
    pool = [[]]
    for i in range(0, len(L)):
        np = []
        for j in range(0, len(pool)):
            for k in range(0, len(L[i])):
                np.append(pool[j] + [L[i][k]])
        pool += np
    return pool


# print allchoice([[1,2],[3,4],[5,6,7]])
