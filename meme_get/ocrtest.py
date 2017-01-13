from .memesites import RedditMemes

A = RedditMemes()

B = A.get_memes(3)

B[0].ocr_caption(method="Tesseract", thres=False,cfg="urban")
B[1].ocr_caption(method="Tesseract", thres=False, cfg="urban")
B[2].ocr_caption(method="Tesseract", thres=False, cfg="urban")

#B[2].ocr_caption(method="FontMatching")

print("Result:")
print(B[0].get_title())
print(B[0].get_caption())
print(B[1].get_title())
print(B[1].get_caption())
print(B[2].get_title())
print(B[2].get_caption())