from PIL import Image, ImageDraw, ImageFont
import sys
import time
import random
import json

path = "images/img6.jpg"

# characters to recognize
C = "ABCDEFGHIJKLMNOPQRSTUVWXYZ123456789"

# standard character glyphs
cimgs = []

# original image
IM = Image.open(path)
w, h = IM.size
PX = IM.load()

# display layer
disp = Image.new("RGB",(w,h))
draw = ImageDraw.Draw(disp)

# threshold layer
thim = Image.new("RGB",(w,h))
thpx = thim.load()
thdr = ImageDraw.Draw(thim)

# character areas
areas = []
badareas = []

# rgb(255,255,255) to hsv(360,1.0,1.0) conversion
def rgb2hsv(r,g,b):
  R = r/255.0;
  G = g/255.0;
  B = b/255.0;
  cmax = max(R,G,B);
  cmin = min(R,G,B);
  delta = cmax-cmin;
  H, S, V = 0,0,0
  if delta == 0: H = 0
  elif cmax == R: H = 60 * (((G-B)/delta)%6)
  elif cmax == G: H = 60 * ((B-R)/delta+2)
  elif cmax == B: H = 60 * ((R-G)/delta+4)
  if cmax == 0: S = 0
  else: S = delta/cmax
  V = cmax
  return H,S,V

# find the left cutoff of character glyph
def firstwhitex(im):
	fwx = im.size[0]
	px = im.load()
	for y in range(0,im.size[1]):
		for x in range(0,im.size[0]):
			r, g, b = px[x,y][:3]
			if (r,g,b)==(255,255,255):
				if x < fwx:
					fwx = x
	return fwx
			
# been there
def visited(x,y,areas):
	for i in range(0,len(areas)):
		if (x,y) in areas[i]:
			return True
	return False

# floodfill from pixel
def flood(x,y,d):
	global areas
	area = []
	seeds = [(x,y)]
	while d > 0 and len(seeds) > 0:
		
		d -= 1
		if d==0:
			#print "too large"
			badareas.append(area)
			return []
		x,y = seeds.pop()

		if visited(x,y,areas) or visited(x,y,badareas):
			#print "visited"
			return []

		if (d > 0 and x > 0 and x < w-1 and y > 0 and y < h-1):
			if not((x,y) in area):
				r,g,b = thpx[x,y][:3]
				
				if (r != 0):
					area.append((x,y))
					seeds += [(x,y),(x-1,y),(x,y-1),(x+1,y),(x,y+1)]
	return area


# get all character areas
def getareas():
	for y in list(range(0,h/3,5))+list(range(2*h/3,h,5)):
		print y, "/", h
		for x in range(0,w,2):
			area = flood(x,y,10000)
			#print area
			if len(area) > 1:
				col = (random.randrange(0,255),random.randrange(0,255),random.randrange(0,255))
				for i in range(0,len(area)):
					draw.point(list(area[i]),fill=col)
				areas.append(area)

# boundaries of a character
def getbounds(area):
	xmin = area[0][0]
	xmax = area[0][0]
	ymin = area[0][1]
	ymax = area[0][1]
	for i in range(0,len(area)):
		if area[i][0] < xmin: xmin = area[i][0]
		if area[i][1] < ymin: ymin = area[i][1]
		if area[i][0] > xmax: xmax = area[i][0]
		if area[i][1] > ymax: ymax = area[i][1]
	return xmin-1,ymin-1,xmax+1,ymax+1

# draw a boundary
def drawbounds():
	bds = []
	for i in range(0,len(areas)):
		bd = getbounds(areas[i])
		bds.append(bd)
		draw.rectangle(bd,outline=(255,0,0))
	return bds


# OCR
def checkchars():
	scoreboard = []
	for i in range(0,len(areas)):
		print i, "/", len(areas)
		bd = getbounds(areas[i])
		scores = []
		for j in range(0,len(cimgs)):
			score = 0
			px = cimgs[j].load()
			score = 0
			sc = (1.0*(bd[3]-bd[1]))/100.0
			for x in range(0,cimgs[j].size[0]):
				for y in range(0,cimgs[j].size[1]):
					xp = min(int(x*sc+bd[0]),w-1)
					yp = min(int(y*sc+bd[1]),h-1)

					r1,g1,b1 = px[x,y][:3]
					r2,g2,b2 = thpx[xp,yp][:3]

					if (xp < bd[2]):
						if (r1 == r2):score += 1
						else: score -= 1
					else:
						if (r1 == 0):score += 0
						else: score -= 1
			scores.append((C[j],int(score*10)/10.0))
		scoreboard.append(normalize(scores))
		draw.text((bd[0],bd[1]-5),normalize(scores)[0][0],(0,255,255))
	return scoreboard


# normalize scores to 0.0-1.0
def normalize(scores):
	scores = sorted(scores,key=lambda x: x[1],reverse=True)

	ns = sorted(scores,key=lambda x: x[1],reverse=True)

	for i in range(0,len(scores)):

		if scores[i][1] <= 0 or scores[0][1] == 0:
			ns[i] = (scores[i][0],0)
		else:
			n = (scores[i][1])/scores[0][1]
			ns[i] = (scores[i][0],int(n*1000)/1000.0)

	return ns

# print OCR result
def showresult(scoreboard):
	for i in range(0,len(scoreboard)):
		print "".join([s[0] for s in scoreboard[i]])

# make character glyphs
for i in range(0,len(C)):
	im = Image.new("RGB",(100,110))
	dr = ImageDraw.Draw(im)
	font = ImageFont.truetype("Impact", 124)
	dr.text((0, -25),C[i],(255,255,255),font=font)

	fwx = firstwhitex(im)

	im = Image.new("RGB",(100,110))
	dr = ImageDraw.Draw(im)
	font = ImageFont.truetype("Impact", 124)
	dr.text((-fwx, -26),C[i],(255,255,255),font=font)

	cimgs.append(im)

# make threshold image
for x in range(0,w):
	for y in range(0,h):
		r, g, b = PX[x,y][:3]
		hsv = rgb2hsv(r,g,b)
		if hsv[2] > 0.9 and hsv[1] < 0.1:
			thdr.point([x,y],fill=(255,255,255))
		else:
			thdr.point([x,y],fill=(0,0,0))



thim.show()
getareas()

bds = drawbounds()

disp.show()

ccr = checkchars()

showresult(ccr)

disp.show()

js = json.dumps([bds,ccr])
fo = open("data/"+path.split("/")[-1].split(".")[0]+".json","w")
fo.write(js)

