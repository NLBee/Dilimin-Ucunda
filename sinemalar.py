from bs4 import BeautifulSoup
from selenium.webdriver import Chrome
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import requests
from lxml import html
from csv import writer
import re

options = Options()
options.headless = True
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.get('https://www.sinemalar.com/filmler')

with open('denemesinemalarcom.csv', 'w', newline='') as file:

    thewriter = writer(file)
    header = ['Isim', 'Konu', 'Link', 'Senaryo', 'Yonetmen', 'Oyuncular']
    thewriter.writerow(header)

    for i in range(1, 3):
        time.sleep(5)
        html = driver.page_source
        soup = BeautifulSoup(html, "lxml")
        movies = soup.find_all('a', class_ = "movie")

        for index, movie in enumerate(movies):
            movie_name = movie.find('div', class_ = "name").text.strip()
            movie_genre = movie.find('div', class_= "genre").text.strip().replace('  ', '')
            link = movie['href']

            #movie_inside_dirty = requests.get(link)
            movie_inside_html = requests.get(link).text
            movie_inside_html = requests.get(link).text
            soup = BeautifulSoup(movie_inside_html, 'lxml')
            #tree = html.fromstring(movie_inside_dirty.content)

            try:
                if(soup.find('p', itemprop = "description").text.strip() == ''): #iki farklı şekilde bilgi kaydettikleri için
                    movie_desc = soup.find('p', itemprop = "description").find_next('p').text.strip()
                else:
                    movie_desc = soup.find('p', itemprop = "description").text.strip()

                yonetmen_html = soup.find(text = re.compile("Yönetmen.*"))
                yonetmen= yonetmen_html.parent
                yonetmen = yonetmen.parent
                yonetmen = yonetmen.find('span', class_= "label").text.strip()
                #yonetmen = yonetmen_html.find('span', class_ = "label").text.strip()

                actors_html = soup.find_all('div', itemprop ="actors")
                list_actor = []
                for j, actor_html in enumerate(actors_html):
                    list_actor.append(actor_html.a.text.strip())
                actor_names = ",".join(list_actor)
            except Exception:
                continue

            film_liste = [movie_name, movie_genre, link, movie_desc, yonetmen, actor_names]
            thewriter.writerow(film_liste)

        driver.find_element(By.XPATH, '//*[@id="pagination"]/div/ul/li[11]/a').click()

file.close()
