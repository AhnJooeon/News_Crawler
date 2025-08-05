import pandas as pd
import urllib.request
import requests
import re
from bs4 import BeautifulSoup
from datetime import timedelta

class NaverSearch():
    def __init__(self):
        print("init")

    def clean_html(self, raw_html):
        soup = BeautifulSoup(raw_html, "html.parser")
        return soup.get_text(" ", strip=True)  # 공백 유지하며 텍스트만 추출

    def crawl_naver(self, urlType, query, page):
        client_id = 'UPJGOwLLHVof6piN_M8e'  # Replace with your Naver API client ID
        client_secret = 'odN08XtmhN'  # Replace with your Naver API client secret

        url = f'https://openapi.naver.com/v1/search/{urlType}'  # blog, cafe, news
        headers = {
            'X-Naver-Client-Id': client_id,
            'X-Naver-Client-Secret': client_secret
        }

        total_results = []  # To store all search results
        display = 10  # Number of results per request
        start = page  # Start index for pagination 1, 11, 21, ... (page num)
        flag = 0

        while True:
            encText = urllib.parse.quote(query)
            url = "https://openapi.naver.com/v1/search/blog?query=" + encText # JSON 결과
            request = urllib.request.Request(url)
            request.add_header("X-Naver-Client-Id",client_id)
            request.add_header("X-Naver-Client-Secret",client_secret)
            response = urllib.request.urlopen(request)
            rescode = response.getcode()

            if rescode == 200:
                items = response.read()
                # items = data['items']

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
            if flag > 1:
                print("# No more results")
                break

        print("Total Result : ", len(total_results))
        df = pd.DataFrame(total_results)

        df['title'] = df['title'].apply(self.clean_html)
        df['description'] = df['description'].apply(self.clean_html)
        df['postDate'] = pd.to_datetime(df['pubDate'])  # datetime으로 변환
        df['pubDate'] = pd.to_datetime(df['pubDate'])  # datetime으로 변환
        df['postDate'] = df['postDate'].dt.strftime("%Y-%m-%d %H:%M:%S")  # 원하는 형식으로 변환
        df = df.sort_values(by='postDate', ascending=False)

        # # 권장 방식 (서울 시간 기준으로 오늘 -2일)
        # two_days_ago = pd.Timestamp.today(tz='Asia/Seoul').normalize() - timedelta(days=2)

        # # 필터링
        # df_filtered = df[df['pubDate'] >= two_days_ago]

        return df

