import pandas as pd
from tqdm import tqdm
import sys
from datetime import timedelta

import Selenium_Crawling
import Naver_Crawler
import API_Crawler
import Remove_Post
import Setting

def Init_Config():
    cfg = Setting.Config_Setting()
    config = cfg.Read_Setting()

    return config

def Search(date, keywords, ID, scrt):
    # keywords = ["상 수상", "표창"]
    # naver_Search = Naver_Crawler.NaverSearch()
    naver_Search = API_Crawler.APICrawler(ID, scrt)

    df = pd.DataFrame()
    for idx, word in enumerate(keywords):
        print(f"Search : {word}")
        tmp_df = naver_Search.crawl_naver("news", word, 1)
        df = pd.concat([df, tmp_df])
        print(f"concat : {df.shape}")

    df = df.drop_duplicates(subset='link')
    naver_reuslt = f"./Data/naver_result_{date}.csv"
    df.to_csv(naver_reuslt)

    return df

def Crawling(df, date):
    sel = Selenium_Crawling.DetailCrawling()
    # df = df[:10]  # test

    for idx, row in tqdm(df.iterrows(), total=df.shape[0]):
        try:
            if "n.news.naver.com" in row["link"]:
                df.loc[idx, "detail"] = sel.Crawling_NaverNews(row["link"])
            else:
                df.loc[idx, "detail"] = sel.Crawling_News(row["originallink"])

            df.to_csv("./result_tmp.csv", encoding='utf-8-sig', index=False)  # 임시 저장

        except Exception as ex:
            print(ex)


    df = df.drop(columns=['originallink', 'link', 'pubDate'])
    df.to_csv(f"./Data/naver_result_{date}.csv", encoding='utf-8-sig', index=False)

    return df

def Remove_duplicate(df):
    rmPost = Remove_Post.RemovePost()
    # 뉴스 기사가 담긴 df를 받아 중복 제거
    df_cleaned = rmPost.deduplicate_news_articles(df)
    print(f"최종 기사 수: {len(df_cleaned)}개")
    return df_cleaned
    

def filter_date(df, start=None, end=None):
    if start:
        df = df[df["postDate"] >= pd.to_datetime(start)]
    if end:
        df = df[df["postDate"] <= pd.to_datetime(end)]
    return df

def Run_Crawler(startdate, enddate):
    if startdate == None:
        startdate = pd.Timestamp.today(tz='Asia/Seoul').normalize() - timedelta(days=1)
        startdate = startdate.strftime("%Y%m%d")
    if enddate == None:
        enddate = pd.Timestamp.today().date().strftime("%Y%m%d")

    print(f"startdate : {startdate} / enddate : {enddate}")

    config = Init_Config()
    keywords = config["keywords"]
    ID = config["client_id"]
    scrt = config["client_secret"]

    result_df = Search(enddate, keywords=keywords, ID=ID, scrt=scrt)
    result_df = filter_date(result_df, start=startdate, end=enddate)

    # result_df = pd.read_csv(f"./Data/naver_result_{enddate}.csv", encoding='utf-8-sig')
    result_df = Crawling(result_df, enddate)

    # 중복 제거 테스트
    # result_df = pd.read_csv(f"./Data/naver_result_{enddate}.csv", encoding='utf-8-sig')

    cleaned_df = Remove_duplicate(result_df)
    cleaned_df = cleaned_df.drop(columns=['full_text', 'cleaned_content', 'intro'])
    cleaned_df.to_csv(f"./result/{enddate}.csv", index=False, encoding='utf-8-sig')


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    args = sys.argv[1:]

    startdate = args[0] if len(args) > 0 else None
    enddate = args[1] if len(args) > 1 else None
    print(f"startdate : {startdate} / enddate : {enddate}")
    Run_Crawler(startdate, enddate)

