import Controller.Main_Controller
import requests
import pandas as pd
import numpy as np
import time
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
import re
import os
import shutil
from datetime import datetime, timedelta
from tqdm import tqdm
from dateutil.parser import parse
import urllib3
from Model.SeleniumCrawling.Detail_Crawling import DetailCrawling
# from Controller.Main_Controller import MainController
from Presenter.Progress_Presenter import ProgressPresenter


class APICrawler():
    def __init__(self):
        self.fileName = '{}_블로그_02'
        self.resultName = "_Detail_Result_{}.csv"

        self.readFile = ""
        self.resultFile = ""
        self.urlTypes = ['blog', 'cafearticle', 'news']
        self.date = datetime.today().strftime('%Y-%m-%d')
        self.path = './out'
        self.rawPath = f"./out/raw/{self.date}"
        urllib3.disable_warnings()

        # self.mctl = Controller.Main_Controller.MainController
        self.prog = ProgressPresenter.instance

    def ShowTask(self, func, tmp):
        def wraper():
            self.prog.Set_Task(func.__name__, len(tmp))
            func()

        return wraper


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

        return df


    def Start_Crawler(self, query):
        result = []  # 수집 결과 저장
        # self.mctl = MainController.instance()

        num = 1
        while True:
            for i in self.urlTypes:
                print('---' * 50, f"{query}_Start_{num}_{i}")
                tmp_df = self.crawl_naver(i, query, num)
                tmp_df['urltype'] = i
                result.append(tmp_df)

            num += 10
            if num > 10:  # 디버깅용
                break

        links_df = pd.DataFrame()  # 모든 결과 저장
        for idx, df in enumerate(result):
            if idx == 0:
                links_df = df
            else:
                links_df = pd.concat([links_df, df])

        print(f"**** Total Result : {len(links_df)} ****")

        self.Create_Directory(self.rawPath)
        self.resultFile = f"{self.rawPath}/{self.date}_{query}.csv"

        # try 위치 확인 필요
        try:
            # URL 전달
            # 링크를 다듬기 (필요없는 부분 제거 및 수정)
            html_tag = re.compile('<.*?>')
            for i in range(0, len(links_df['link'])):
                a = links_df.loc[i, 'link']
                a = a.replace('\\', '')
                b = a.replace('?Redirect=Log&logNo=', '/')
                links_df[i, 'link'] = b.copy()

                links_df.loc[i, 'title'] = re.sub(html_tag, '', links_df.loc[i, 'title'])
                links_df.loc[i, 'description'] = re.sub(html_tag, '', links_df.loc[i, 'description'])

        except Exception as ex:
            print(ex)

        links_df = links_df.drop_duplicates(subset=['link'])
        print(f"**** Total Result (drop_duplicates) : {len(links_df)} ****")
        links_df.to_csv(self.resultFile, encoding='utf-8-sig', index=False)

    def Read_links(self, name):
        print(name)
        self.Check_Files(name)
        self.Read_File()

    def Read_File(self):
        result = pd.read_csv(self.readFile)
        result = result.drop_duplicates('link')
        # result = self.Detail_Crawling(result, True)
        result.to_csv(self.resultFile, encoding='utf-8-sig', index=False)

    def Check_Files(self, name):
        try:
            idx = 1
            tmpReadFile = self.fileName.format(name)
            tmpResultFile = tmpReadFile + self.resultName.format(idx)
            while True:
                if os.path.isfile(tmpResultFile):
                    print("Exisit")
                    idx += 1
                    tmpResultFile = tmpReadFile + self.resultName.format(idx)
                else:
                    self.readFile = tmpReadFile + self.resultName.format(idx - 1)
                    self.resultFile = tmpReadFile + self.resultName.format(idx)
                    break
        except Exception as ex:
            print(ex)

    def Read_Folder(self):
        path = './Result_Keywords'
        file_list = os.listdir(path)

        for file in file_list:
            self.readFile = file
            self.resultFile = "[Result]" + file
            self.Read_File()

    def Create_Directory(self, path):
        try:
            if not os.path.exists(path):
                os.makedirs(path)
        except Exception as ex:
            print(ex)

    def Summary_Result(self):
        print(f"**** Start Summary_Result ****")
        if os.path.exists(self.rawPath):
            file_list = os.listdir(self.rawPath)
        else:
            print("")

        resultFileName = f"{self.date}_Summary.csv"

        result_df = pd.DataFrame()  # 모든 결과 저장
        # Controller.Main_Controller.SignalInstance.Set_Task("Summary_Result(file)", len(file_list))
        self.prog.Set_Task("Summary_Result(file)", len(file_list))
        for file in tqdm(file_list, desc="file_list"):
            if not "Summary" in file:
                if file.endswith(".csv"):
                    tmp_file = pd.read_csv(f"{self.rawPath}/{file}")

                    querys = file.split('_')
                    tmp_file['query'] = querys[1].replace('.csv', "")

                    # result_df = result_df.append(tmp_file)
                    result_df = pd.concat([result_df, tmp_file])

        result_df = result_df.drop_duplicates(subset=['link'])
        print(f"**** Total Result (drop_duplicates) : {len(result_df)} ****")
        self.prog.Set_Task("Summary_Result(Result)", result_df.shape[0])

        # for idx, tmp in tqdm(result_df.iterrows(), total=result_df.shape[0], desc="result_df"):
        idx = 0
        for tmp in result_df.itertuples():
            # if pd.isnull(tmp['pubDate']) is False:
            if pd.isnull(tmp.pubDate) is False:
                self.prog.Set_Progress(idx)
                # date = parse(tmp['pubDate']).strftime("%Y%m%d")
                date = parse(tmp.pubDate).strftime("%Y%m%d")
                result_df.loc[idx, ['postdate']] = date
            # print(f"{idx} in Summary_Result(Result)")
            idx += 1
        print("---- Summary_Result(Result) End ----")
        result_df.to_csv(f"{self.rawPath}/{resultFileName}", encoding='utf-8-sig', index=False)

    def Last_Date(self):
        for i in range(1, 5):
            date = datetime.today() - timedelta(days=i)
            predate = f"./out/raw/{date.strftime('%Y-%m-%d')}"
            if os.path.isdir(predate):
                return date.strftime('%Y-%m-%d')

    def Read_PreData(self):
        print(f"**** Start Read_PreData ****")
        preDate = self.Last_Date()
        toDate = f"{self.date}"
        pre_resultFile = f"./out/raw/{preDate}/[Detail]{preDate}_Summary.csv"
        to_resultFile = f"./out/raw/{toDate}/{toDate}_Summary.csv"
        saveFileName = f"./out/raw/{toDate}/[Detail]{toDate}_Summary.csv"

        pre_Result = pd.read_csv(pre_resultFile)
        to_Result = pd.read_csv(to_resultFile)

        if 'contents' not in to_Result.columns:
            to_Result['contents'] = None

        for idx, tmp in tqdm(pre_Result.iterrows(), total=pre_Result.shape[0], desc="pre_Result"):
            if not pd.isnull(tmp['contents']):
                to_Result = self.Matching_Row(tmp,to_Result)

        to_Result.to_csv(saveFileName)


    def Matching_Row(self, source_row, target_df):
        prKey = 'link'
        content = 'contents'
        for idx, target_row in target_df.iterrows():
            if target_row[prKey] == source_row[prKey]:
                target_df.loc[idx, content] = source_row[content]
                break

        return target_df

    def Join_Link(self, source, target):
        pd.merge(left=target, right=source, on='link', how='inner')

    def Calc_Date(self, startDate, endDate, dateList):
        timeList = []
        startTime = datetime.strptime(startDate, '%Y-%m-%d')
        endTime = datetime.strptime(endDate, '%Y-%m-%d')

        for i in dateList:
            i = datetime.strptime(i, '%Y-%m-%d')
            startDelta = startTime - i
            endDelta = endTime - i
            if startDelta.days > 1:
                i = i.strftime('%Y-%m-%d')
                timeList.append(i)

            if endDelta.days > 1:
                if i not in timeList:
                    i = i.strftime('%Y-%m-%d')
                    timeList.append(i)

        return timeList

    def Convet_DateTime(self, list):
        tmp = []
        for i in list:
            dt = datetime.strftime(i, "%Y-%m-%d")
            tmp.append(dt)

        return tmp

    def Create_All_Data(self, startDate=None, endDate=None):
        path = f'./out'
        merge_df = None
        file_list = os.listdir(f"{path}/raw/")
        file_list = sorted(file_list, key=lambda date: datetime.strptime(date, "%Y-%m-%d"), reverse=True)

        if startDate is not None and endDate is not None:
            file_list = self.Calc_Date(startDate, endDate, file_list)
            merge_name = f"{startDate}-{endDate}_Merge_File.csv"
        else:
            merge_name = f"[Company][All]Crawling_Merge_File.csv"

            if os.path.exists(f"{path}/{merge_name}"):
                merge_df = pd.read_csv(f"{path}/{merge_name}", index_col=0)
                # merge_df.iloc[1, 12] = "text"
                # print(merge_df.loc[1, 13])

        for date in tqdm(file_list, desc="Create_All_Data"):
            date_list = os.listdir(f"{path}/raw/{date}")
            # detailName = f"[Detail]{date}_Summary.csv"
            detailName = f"{date}_Summary.csv"

            if detailName in date_list:
                df = pd.read_csv(f"{path}/raw/{date}/{detailName}", index_col=0)
                if merge_df is None:
                    merge_df = df
                else:
                    # merge_df = self.Merge_df(df, merge_df, detailName)
                    merge_df = pd.concat([merge_df, df])
                    merge_df = merge_df.drop_duplicates(subset=['link'])

                merge_df.to_csv(f"{path}/{merge_name}")

        print(f"**** Finish Task, Result : {merge_df.shape}")

    def Merge_df(self, source_df, target_df, name):
        for idx, row in tqdm(source_df.iterrows(), total=source_df.shape[0], desc=f"Merge_df[{name}]", position=0, leave=True):
            if target_df["link"].str.contains(row["link"]) is False:
                target_df = pd.concat(target_df, row)

        return target_df

    def Read_Summary(self):
        resultFileName = f"{self.rawPath}/{self.date}_Summary.csv"
        saveFileName = f"{self.rawPath}/[Detail]{self.date}_Summary.csv"

        # Detail Crawling
        dc = DetailCrawling()
        dc.Crawling_All(resultFileName, saveFileName)

    def Read_Merge(self):
        filelist = os.listdir('./out')
        resultName = ""
        for file in filelist:
            if os.path.splitext(file)[1] == ".csv":
                resultName = file
                if "[All]Crawling_Merge_File" in resultName:
                    break

        if resultName != "":
            backFileName = f"./out/[Test]{resultName}"  # 디버깅용
            saveFileName = f"./out/{resultName}"
            dc = DetailCrawling()
            dc.Crawling_All(f"./out/{resultName}", saveFileName, backFileName)

    def Detail_Meta(self, resultName=""):
        path = "./out"

        if resultName == "":
            resultName = "[Merge]Crawling_Merge_File.csv"
            readFileName = f"{path}/{resultName}"
        else:
            tmp_list = resultName.split('_')
            readFileName = f"{path}/raw/{tmp_list[0]}/{resultName}"  # 처음 시작할 때 사용
            # readFileName = f"{path}/raw/{tmp_list[0]}/[Test]{resultName}"  # 이어서 할 때 사용

        backFileName = f"{path}/[Test]{resultName}"  # 디버깅용
        dc = DetailCrawling()
        dc.Crawling_Meta(readFileName, backFileName)

    def Read_Files(self, path):
        file_list = os.listdir(path)
        files = []
        for file in file_list:
            if os.path.splitext(file)[1] == ".csv":
                files.append(file)

        return files

    def Get_DateFile(self, path):
        file_list = os.listdir(f"{path}/raw/")  # 전체 날짜
        files = []
        for idx, file in enumerate(file_list):
            try:
                parse(file)
                files.append(file)
            except:
                print("Type Error")

        files = sorted(files, key=lambda date: datetime.strptime(date, "%Y-%m-%d"), reverse=True)

        return files

    def Find_link(self, df):
        meta_path = f'{self.path}/metaData.csv'

        # Check Meta Data
        if os.path.exists(meta_path):
            meta_df = pd.read_csv(meta_path)
        else:
            meta_df = df

        rows = []
        for idx, row in tqdm(df.iterrows(), total=df.shape[0], desc='Find_link'):
            if row['link'] not in meta_df['link']:
                meta_df = pd.concat([meta_df, row])
                # meta_df.to_csv(meta_path)
                rows.append(idx)
                self.prog.Set_Progress(idx)

        new_df = df.loc[rows]

        return new_df

    def Creat_Meta(self):
        path = './out'
        meta_path = f'{path}/metaData.csv'
        merge_df = None

        file_list = os.listdir(f"{path}/raw/")
        files = []
        for idx, file in enumerate(file_list):
            try:
                parse(file)
                files.append(file)
            except:
                print("Type Error")

        files = sorted(files, key=lambda date: datetime.strptime(date, "%Y-%m-%d"), reverse=True)

        # Merge summary
        for date in tqdm(files, desc="Creat_Meta"):
            detailName = f"{date}_Summary.csv"

            # Check detailName file
            tmp_path = f"{path}/raw/{date}/{detailName}"
            if os.path.exists(tmp_path):
                df = pd.read_csv(tmp_path, index_col=0)

                if merge_df is None:
                    merge_df = df
                else:
                    # merge_df = self.Merge_df(df, merge_df, detailName)
                    merge_df = pd.concat([merge_df, df])
                    merge_df = merge_df.drop_duplicates(subset=['link'])

                merge_df.to_csv(f"{meta_path}")

        print(f"**** Finish Task, Result : {merge_df.shape}")

    def Check_ResultFiles(self):
        preFile = "./out/[Test][Merge]Crawling_Merge_File.csv"
        path = './out/Result'

        if os.path.exists(preFile):
            num = 0
            filename = "[Test][Merge]Crawling_Merge_File.csv"
            while True:
                fullname = f"{path}/{filename}"
                if os.path.exists(fullname):
                    num += 1
                    filename = f"[Test][Merge]Crawling_Merge_File_({num}).csv"
                else:
                    print(f"Full Name : {fullname}")
                    shutil.move(preFile, fullname)
                    break


    def Fill_Contents(self):
        path = f'./out/Result'
        meta_df = pd.read_csv(f"./out/metaData.csv", index_col=0)
        target_df = meta_df.reset_index()
        if 'contents' not in target_df.columns:
            target_df['contents'] = None

        reFilter = ["Exception", "Exception_xPath : ", "Exception_xPath : None"
                    , "Exception : Message: disconnected", "timeout: Timed out receiving message"]

        self.Check_ResultFiles()
        try:
            files = self.Read_Files(path)


            for file in files:
                source_df = pd.read_csv(f"{path}/{file}", index_col=0)
                if 'contents' in source_df.columns:
                    source_dict = source_df.set_index('link')['contents'].to_dict()
                    self.prog.Set_Task(file, target_df.shape[0])
                    for idx, target_row in tqdm(target_df.iterrows(), total=target_df.shape[0], desc=file):
                        if 'contents' in target_row:
                            if target_row['contents'] is None:
                                if target_row['link'] in source_dict:
                                    content = source_dict[target_row['link']]
                                    flag = False

                                    if content is not None:
                                        if not pd.isna(content):
                                            flag = True

                                    if flag:
                                        # 임시 확인 (이전 예외처리구문 처리용)
                                        ex_flag = False
                                        for i in reFilter:
                                            if content in i:
                                                ex_flag = True
                                                break

                                        if ex_flag is False:
                                            target_df.loc[idx, 'contents'] = content
                                            self.prog.Set_Progress(idx)

        except Exception as ex:
            print(ex)
        finally:
            target_df.to_csv("./out/[Merge]Crawling_Merge_File.csv")
            print(f"Finish Fill Task : {target_df.shape}")

    #
    def Update_Meta(self):
        path = './out/metaData.csv'
        # Check Meta
        if os.path.exists(path):
            print("Start Update Meta")
            self.Find_NewLink(path)
        else:
            print("this file is not exists")
            self.Creat_Meta()

        # Get None contents row
        # newrow = self.Get_Groupby()
        # Get New Link
        # newlink = self.Get_Groupby()

    def Find_NewLink(self, path):
        print()
        meta_df = pd.read_csv(path)
        meta_Dic = meta_df.set_index('link')['contents'].to_dict()

        # Summary File List
        file_list = os.listdir(f"./out/raw/")
        file_list = sorted(file_list, key=lambda date: datetime.strptime(date, "%Y-%m-%d"), reverse=True)

        for idx, file in enumerate(file_list):
            tmp = f"./out/raw/{file}/{file}_Summary.csv"
            if os.path.exists(tmp):
                sum_df = pd.read_csv(tmp, index_col=0)
                for idx, row in sum_df.iterrows():
                    if row.link not in meta_Dic.keys():
                        meta_df = meta_df.concat([meta_df,row])

        # Write meta_df
        meta_df.to_csv(path)

    def Get_Groupby(self):
        df = pd.DataFrame

        return df