from .memesites import RedditMemes
from .memesites import MemeGenerator
import sys

A = MemeGenerator()
A_memes = A.get_memes(500)

f = open('memegenerator.txt', 'w')
for i in A_memes:
    f.write(str(i.get_caption()) + '\n')

f.close()

B = RedditMemes()
B_memes = B.get_memes(500)

f2 = open('redditmemes.txt', 'w')
for i in B_memes:
    print("New meme: ", i)
    try:
        i.ocr_caption(method="Tesseract", thres=False, cfg="urban")
        print(str(i.get_caption()))
        f2.write(str(i.get_caption()) + '\n')
    except:
        print("error: ", sys.exc_info()[0])
f2.close()
