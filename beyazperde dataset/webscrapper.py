from bs4 import BeautifulSoup
import requests
import pandas as pd

# boş dataframe oluşturma
movies_df = pd.DataFrame(columns=["başlık", "özet", "tür", "vizyon_tarihi", "oyuncular", "yönetmen", "resim_link"])

movie_links = list()

last_page_num = 228

# sitede sayfa sayfa gezerek her filmin linkini çekme
for page_num in range(1, last_page_num+1):

    req = requests.get(f"https://www.beyazperde.com/filmler-tum/kullanici-puani/?page={page_num}")

    soup = BeautifulSoup(req.text, "html.parser")

    elements = soup.find_all("li", class_="mdl")

    for movie in elements:
        mov_link = movie.find("a", class_="meta-title-link")
        movie_links.append(mov_link["href"].strip("/").split("-")[1])


# elde edilen linklerden her film için bilgileri çekme
for each in movie_links:

    req = requests.get(f"https://www.beyazperde.com/filmler/film-{each}/")

    soup = BeautifulSoup(req.text, "html.parser")

    # başlık
    try:
        title = soup.find("div", class_="titlebar-title titlebar-title-lg").text
        print(title)
    except AttributeError:
        title = "None"

    # özet
    try:
        description = soup.find("div", class_="content-txt").text.strip("\n")
    except AttributeError:
        description = "None"

    # vizyon tarihi
    try:
        metabody_info = soup.find("div", class_="meta-body-item meta-body-info")
        date = metabody_info.find("span", class_="date").text.strip("\n")
    except AttributeError:
        date = "None"

    # tür(ler)
    try:
        metabody_info = soup.find("div", class_="meta-body-item meta-body-info")
        if date == "None":
            genre = [a.text for a in metabody_info.find_all("span")[2:]]
        else:
            genre = [a.text for a in metabody_info.find_all("span")[3:]]

    except AttributeError:
        genre = "None"

    # oyuncular
    try:
        metabody_cast = soup.find("div", class_="meta-body-item meta-body-actor")
        cast_html = metabody_cast.find_all("span")
        cast = [a.text for a in cast_html][1:]
    except AttributeError:
        cast = "None"

    # yönetmen(ler)
    try:
        metabody_director = soup.find("div", class_="meta-body-item meta-body-direction")
        director_html = metabody_director.find_all("span")
        director = [a.text for a in director_html][1:]
    except AttributeError:
        director = "None"

    # resim linki
    try:
        img_url = soup.find("img", class_="thumbnail-img")["src"]
    except AttributeError:
        img_url = "None"

    # film bilgilerini içeren dataframe satırı oluşturma
    movies_df = movies_df.append({"başlık": title, "özet": description, "tür": genre, "vizyon_tarihi": date, "oyuncular": cast, "yönetmen": director, "resim_link": img_url}, ignore_index=True)


# verileri csv dosyasına kaydetme
movies_df.to_csv("movies2.csv", encoding="utf-8")
