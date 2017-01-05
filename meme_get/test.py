# Testing beautiful soup
import bs4
import requests
import memesites
import hashlib

page = requests.get('http://www.quickmeme.com')
soup = bs4.BeautifulSoup(page.text, 'html.parser')

# Find a list of posts on the quickmeme page
list_of_posts = soup.find_all(class_="post-image")

# Access the text of each post
list_of_texts = [str(x['alt']) for x in list_of_posts]

# get urls of each post
list_of_urls = [str(x['src']) for x in list_of_posts]

# Test Meme hash and eq
A = memesites.Meme('1', '2')
B = memesites.Meme('1', '2')
C = memesites.Meme('1', '3')
print(len(set([A, B, C])))

# Test Meme md5 hashing
memeA = memesites.Meme('1', '2')
hashID = hashlib.md5()
print(repr(memeA))
hashID.update(repr(memeA).encode('utf-8'))
print(hashID.hexdigest())

#A = memesites.QuickMeme()
#print("Should be false:", A._cache_expired())
#A._memes_on_page(1, 5)

#A_tuple = A._write_data_tuple()
# A._save_cache()
#B = memesites.QuickMeme()
# B._read_cache()
#print(A_tuple == B._write_data_tuple())

# Test get memes
#A = memesites.QuickMeme()
#result = A.get_memes(3)
#result2 = A.get_memes(500)
#result = A.get_memes(20)

# Test memegenerator.net get memes
A = memesites.MemeGenerator()
result = A.get_memes(32)
print(result)
