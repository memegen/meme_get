from .memesites import RedditMemes

A = RedditMemes()

B = A.get_memes(1)

B[0].ocr_caption(method="Tesseract", thres=False,cfg="urban")

print(B[0].get_caption())