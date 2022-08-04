import requests
from bs4 import BeautifulSoup
import pandas as pd

URL = "https://www.beyazperde.com/filmler-tum/kullanici-puani/"
NUM_OF_PAGES = 228

def page_link_generator():
    page_urls = [URL]
    for i in range(1,NUM_OF_PAGES+1):
        page_urls.append(URL + "kullanici-puani/?page=" + str(i))
    return page_urls

def get_urls(baselink):
    r = requests.get(baselink)
    soup = BeautifulSoup(r.content, 'html.parser')
    
    exts = soup.find_all('a', class_='meta-title-link')
    url_list = []

    for ext in exts:
        url_list.append("https://www.beyazperde.com" + ext['href'])
    return url_list

def get_cast(meta):
    try:
        cast_raw = meta.find('div', class_='meta-body-item meta-body-actor').select('span[class*=vc]')
    except:
        cast_raw = []
    cast = []
    for casting in cast_raw:
        cast.append(casting.get_text(strip=True))
    return cast

def get_dirs(meta):
    try:
        dirs_raw = meta.find('div', class_='meta-body-item meta-body-direction').select('span[class*=vc]')
    except:
        dirs_raw = []
    dirs = []
    for dir in dirs_raw:
        dirs.append(dir.get_text(strip=True))
    return dirs

def get_genres(meta):
    try:
        genres_raw = meta.select('span[class*=td]')
    except:
        genres_raw = []
    genres = []
    for genre in genres_raw:
        genres.append(genre.get_text(strip=True))
    return genres

def write_info(movie, url):
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    meta = soup.find('div', class_='meta')
    movie['Title'] = soup.find('h1', class_='item').get_text(strip=True)
    movie['Description'] = soup.find('div', class_='content-txt').get_text(strip=True)
    movie['Genre(s)'] = get_genres(meta)
    movie['Director(s)'] = get_dirs(meta)
    movie['Cast'] = get_cast(meta)

def run_scraper():
    pages = page_link_generator()
    movies = []

    for page in pages:
        in_page_urls = get_urls(page)
        for url in in_page_urls:
            movie = {}
            write_info(movie, url)
            movies.append(movie)
            print(movie['Title'])
        
    df=pd.DataFrame(movies)
    df.to_csv('movies.csv', sep='\t', encoding='utf-8')

if __name__ == "__main__":
    run_scraper()