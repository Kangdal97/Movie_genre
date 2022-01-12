from selenium import webdriver
from selenium.common.exceptions import *
import pandas as pd
import re
import time
from selenium.webdriver.common.keys import Keys


def crawl_genre(a):
    try:
        driver.find_element_by_xpath('//*[@id="old_content"]/ul/li[{}]/a'.format(a)).send_keys(Keys.ENTER)
        time.sleep(0.2)
    except:
        print('error_{}'.format(a))
    try:  # 줄거리가 있는 경우
        title = driver.find_element_by_xpath('//*[@id="content"]/div[1]/div[4]/div[1]/div/div[1]/p').text
        title = re.compile('[^가-힣a-zA-Z ]').sub(' ', title)
        titles.append(title)
    except NoSuchElementException:  # 줄거리가 없는 경우
        print('No summary_{}'.format(a))
        pass
    driver.back()


options = webdriver.ChromeOptions()
options.add_argument('lang=ko_KR')
options.add_argument('--no-sandbox')  # 가상 컴퓨터에서 실행할때
options.add_argument('--disable-dev-shm-usage')  # 리눅스에서 사용시
options.add_argument('disable-gpu')
driver = webdriver.Chrome('./chromedriver.exe', options=options)

df_summary = pd.DataFrame()
category = [1, 2, 4, 5, 10, 11, 15, 18, 19, 21]
pages = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]  # 시작페이지
pagend = [2240, 66, 269, 215, 1178, 872, 936, 87, 442, 342]  # 끝페이지
genre = ['Drama', 'Fantasy', 'Horror', 'Romance', 'Documentary', 'Comedy', 'Anime', 'SF', 'Action', 'Erotic']

for l in range(3):
    titles = []
    for k in range(pages[l], pagend[l] + 1):
        url = 'https://movie.naver.com/movie/sdb/browsing/bmovie.naver?genre={}&page={}'.format(category[l], k)
        driver.get(url)
        for i in range(1, 21):
            try:
                crawl_genre(i)
            except StaleElementReferenceException:
                time.sleep(0.2)
                driver.get(url)
                print('loading {} page'.format(k))
                time.sleep(0.5)  # url 검색시 늦어져서 못받아들일 경우 대기시간을 준다.
                crawl_genre(i)
            except:
                print('error_{}p_{}'.format(k, i))
        if k % 30 == 0:
            df_section_titles = pd.DataFrame(titles, columns=['summary'])
            df_section_titles['genre'] = genre[l]
            df_section_titles.to_csv('./crawling/movie_genre_{}_{}-{}.csv'.format(genre[l], k - 29, k), index=False)
            titles = []

    df_section_titles = pd.DataFrame(titles, columns=['summary'])
    df_section_titles['genre'] = genre[l]
    df_section_titles.to_csv('./crawling/movie_genre_{}_remain.csv'.format(genre[l]), index=False)

driver.close()
