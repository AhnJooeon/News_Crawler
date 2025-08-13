import requests
import pandas as pd
import numpy as np
import time
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
import re
from datetime import datetime, timedelta
from tqdm import tqdm
from dateutil.parser import parse
import urllib3
from bs4 import BeautifulSoup


class APICrawler:
    def __init__(self, ID, SCRT):
        self.urlTypes = ['blog', 'cafearticle', 'news']
        urllib3.disable_warnings()
        self.client_id = ID
        self.client_secret = SCRT
    
    def clean_html(self, raw_html):
        soup = BeautifulSoup(raw_html, "html.parser")
        return soup.get_text(" ", strip=True)  # 공백 유지하며 텍스트만 추출


    def crawl_naver(self, urlType, query, page):
        url = f'https://openapi.naver.com/v1/search/{urlType}'  # blog, cafe, news
        headers = {
            'X-Naver-Client-Id': self.client_id,
            'X-Naver-Client-Secret': self.client_secret
        }

        total_results = []  # To store all search results
        display = 10  # Number of results per request
        start = page  # Start index for pagination 1, 11, 21, ... (page num)
        flag = 0

        while True:
            params = {
                'query': query,
                'display': display,
                'start': start,
                'sort': 'sim',  # sort option(date, sim)
            }
            try:
                response = requests.get(url, headers=headers, params=params, verify=False)
            except Exception as ex:
                print(ex)


            if response.status_code == 200:
                data = response.json()
                items = data['items']

                if not items:  # No more results
                    flag += 1
                else:
                    flag = 0

                total_results.extend(items)
                start += display

            else:
                print('Failed to retrieve search results. ', flag)
                flag += 1

            # Break Point
            if flag > 10:
                print("# No more results")
                break

        html_tag = re.compile('<.*?>')

        for idx in range(len(total_results)):
            # date = total_results[idx]['postdate']
            title = re.sub(html_tag, '', total_results[idx]['title'])
            total_results[idx]['title'] = title
            link = total_results[idx]['link']
            description = re.sub(html_tag, '', total_results[idx]['description'])
            total_results[idx]['description'] = description
            # print(f'Date: {date}')
            # print(f'Title: {title}')
            # print(f'Link: {link}')
            # print(f'Description: {description}')
            # print('---' * 50)

        print("Total Result : ", len(total_results))
        df = pd.DataFrame(total_results)
        df['title'] = df['title'].apply(self.clean_html)
        df['description'] = df['description'].apply(self.clean_html)
        df['postDate'] = pd.to_datetime(df['pubDate'])  # datetime으로 변환
        df['postDate'] = df['postDate'].dt.strftime("%Y%m%d %H:%M:%S")  # 원하는 형식으로 변환
        df['postDate'] = pd.to_datetime(df['postDate'])
        df = df.sort_values(by='postDate', ascending=False)

        return df