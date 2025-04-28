"""
Crea un índex de vídeos de TV3 a partir de les temporades d'una sèrie o d'una cerca.
"""

from requests_html import HTMLSession

DATA_PATH = "/media/clic/ppastells/subs_scrapping_corpus/data/tv3/"

session = HTMLSession()
# series = ["30-minuts"]
series = []
cerques = ["cuines Gessami"]


def get_urls_from_url(url):
    r = session.get(url)
    # per carregar més vídeos es pot fer scroll, es pot jugar amb els 2 paràmetres
    r.html.render(scrolldown=30, sleep=1)
    return r.html.xpath('//a[contains(@href, "/video/")]/@href')


def get_serie(serie):
    video_urls = []
    prev_urls = []
    for num in range(1, 10):
        url_temporada = f"https://www.3cat.cat/3cat/{serie}/capitols/temporada/{num}/"
        urls = get_urls_from_url(url_temporada)
        if urls == [] or urls == prev_urls:
            break
        video_urls.extend(urls)
        prev_urls = urls

    video_urls = {"https://www.3cat.cat" + url for url in video_urls}

    with open(DATA_PATH + f"index_{serie}.txt", "w") as f:
        for url in video_urls:
            f.write(url + "\n")


def get_cerca(cerca):
    cerca_url = "https://www.3cat.cat/3cat/cercador/?cerca=" + cerca.replace(" ", "%2520")
    video_urls = get_urls_from_url(cerca_url)
    video_urls = {"https://www.3cat.cat" + url for url in video_urls}

    with open(DATA_PATH + f"index_{cerca.replace(' ', '_')}.txt", "w") as f:
        for url in video_urls:
            f.write(url + "\n")


if __name__ == "__main__":
    for serie in series:
        print(serie)
        get_serie(serie)
    for cerca in cerques:
        print(cerca)
        get_cerca(cerca)
