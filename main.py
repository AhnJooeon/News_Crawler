import pandas as pd
from tqdm import tqdm

import Selenium_Crawler
import Naver_Crawler
import Remove_Post

def Search(date):
    keywords = ["상 수상", "표창"]
    naver_Search = Naver_Crawler.NaverSearch()

    df = pd.DataFrame()
    for idx, word in enumerate(keywords):
        print(f"Search : {word}")
        tmp_df = naver_Search.crawl_naver("news", word, 1)
        df = pd.concat([df, tmp_df])
        print(f"concat : {df.shape}")

    df = df.drop_duplicates(subset='link')
    naver_reuslt = f"./naver_result_{date}.csv"
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
    df.to_csv(f"./Data/result_{date}.csv", encoding='utf-8-sig', index=False)

    return df

def Remove_duplicate(df):
    rmPost = Remove_Post.RemovePost()
    # 뉴스 기사가 담긴 df를 받아 중복 제거
    df_cleaned = rmPost.deduplicate_news_articles(df)
    print(f"최종 기사 수: {len(df_cleaned)}개")
    df_cleaned.to_csv("./news_cleaned.csv", index=False)


def Run_Crawler():
    date = pd.Timestamp.today().date()
    print(date)

    # result_df = Search(date)
    # result_df = Crawling(result_df, date)

    # 중복 제거 테스트
    result_df = pd.read_csv(f"./Data/result_{date}.csv", encoding='utf-8-sig')

    Remove_duplicate(result_df)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    Run_Crawler()

