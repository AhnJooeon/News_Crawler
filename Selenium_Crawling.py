
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import requests
import time
import pandas as pd
from tqdm import tqdm
import os


class DetailCrawling():
    def __init__(self):
        self.urlTypes = ['blog', 'cafearticle', 'news']
        self.Set_Driver()
        self.comm_xPath = ["contents", "container", "wrap", "articleBody", "dic_area"
            , "newsct_article", "newsEndContents", "newsEndContents", "article"
            , "article-view"]

    def Set_Driver(self):
        # 크롬 드라이버 불러오기
        # driverPath = "./SeleniumCrawling/chromedriver"  # 크롬드라이버 설치된 경로. 파이썬(.py) 저장 경로와 동일하면 그냥 파일명만
        driverPath = "./chromedriver"
        # print(os.getcwd())
        # brew install --cask chromedriver  크롬 업데이트 시 터미널에서 사용
        options = webdriver.ChromeOptions()
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        options.add_argument("--blink-settings=imagesEnabled=false")  # image not load
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("headless")  # Not show
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-application-cache")
        options.add_argument("--disable-infobars")
        options.add_argument("--no-sandbox")
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument("--hide-scrollbars")
        options.add_argument("--enable-logging")
        options.add_argument("--log-level=0")
        options.add_argument("--single-process")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--homedir=/tmp")

        # self.driver = webdriver.Chrome(options=options)  # Open Chrome
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        # self.wait = WebDriverWait(self.driver, 10)
        self.driver.set_page_load_timeout(30)
        self.driver.implicitly_wait(0)
        self.driver.set_window_size(720, 480)

        # Crawling Speed up?
        caps = DesiredCapabilities.CHROME
        caps["pageLoadStrategy"] = "none"
        # self.driver.switch_to.new_window('tab')

    def Get_EC(self, element, xPath):
        try:
            ecDriver = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((element, f"//div[@id='{xPath}']"))
            )
            return ecDriver
        except TimeoutError:
            print("TimeoutError")
        except Exception as ex:
            print(f"Get_EC Error : {ex}")

    def Close_Tab(self):
        try:
            # login popup
            main = self.driver.window_handles
            for handle in main:
                if handle != main[0]:
                    self.driver.switch_to.window(handle)
                    self.driver.close()
            self.driver.switch_to.window(main[0])
        except Exception as ex:
            print(ex)
            self.Set_Driver()


    def Crawling_News(self, url):
        text = ""
        xPath = ""
        try:
            self.driver.execute_script("window.open('');")
            self.driver.switch_to.window(self.driver.window_handles[1])
            self.driver.get(url)
            time.sleep(1)

            if "yna.com" in url:  # 연합
                xPath = "articleWrap"
            elif "dailian.co.kr" in url:  # 데일리안
                xPath = "contentsArea"
            elif "news.imaeil.com" in url:  # 매일신문
                xPath = "articlebody"
            elif "idaegu.com" in url:  # 대구일보
                xPath = "articleContent"
            elif "yeongnam.com" in url:  # 영남일보
                xPath = "wrap"
            elif "fnnews.com" in url:  # 파이낸셜뉴스
                xPath = "article_content"
            elif "news.mt.co.kr" in url:  # 머니투데이
                xPath = "textBody"
            elif "newsis.com" in url:  # 뉴시스
                xPath = "content"
            elif "news1.kr" in url:  # 뉴스1
                xPath = "articles_detail"
            elif "news.kbs.co.kr" in url:  # KBS
                xPath = "cont_newstext"
            elif "dgmbc.com" in url:  # 대구MBC
                xPath = "journal_article_wrap"
            elif "segye.com" in url:  # 세계일보
                xPath = "wrapCont"
            elif "ajunews.com" in url:  # 아주경제
                xPath = "articleBody"
            elif "hankyung.com" in url:  # 한국경제
                xPath = "articletxt"
            elif "biz.sbs.co.kr" in url:  # SBS Biz
                xPath = "cnbc-front-articleContent-area-font"
            elif "fntoday.co.kr" in url:  # 파이낸션투데이
                xPath = "snsAnchor"
            elif "m-i.kr" in url:  # 매일일보
                xPath = "article-view-content-div"
            elif "fntimes.com" in url:  # 한국금융
                xPath = "articleBody"
            elif "etnews.com" in url:  # 전자신문
                xPath = "articleBody"
            elif "newspim.com" in url:  # 뉴스핌
                xPath = "news-contents"
            elif "idaegu.co.kr" in url:  # 대구신문
                xPath = "article-view-content-div"
            elif "biz.chosun.com" in url:  # 조선비즈
                xPath = "fusion-app"
            elif "donga.com" in url:  # 동아일보
                xPath = "article_txt"
            elif "pressian.com" in url:  # 프레시안
                xPath = "articleBody"
            elif "sentv.co.kr" in url:  # 서울경제TV
                xPath = "newsView"
            elif "sports.news.naver.com" in url:  # 네이버 스포츠 기사
                xPath = "newsEndContents"
            else:
                xPath = "None"

            if xPath == "None":
                for idx, tmpPath in enumerate(self.comm_xPath):
                    try:
                        text = self.driver.find_element(By.XPATH, f"//div[@id='{tmpPath}']").text
                        text = f"[Container_{idx}]{text}"
                        break
                    except:
                        # print(f"Comm_xPath_{idx} Error")
                        text = "Comm_xPath_Error"
            else:
                text = self.driver.find_element(By.XPATH, f"//div[@id='{xPath}']").text

        except NoSuchElementException as nosuch:
            print(nosuch)
            # Access Error
            try:
                text = self.driver.find_element(By.XPATH, "/html/body/center/font").text
            except:
                print("Unknown URL Error")
                text = "Unknown_URL_Error"
        except Exception as ex:
            print(ex)
            text = f"Exception_xPath_Error : {xPath}"
        finally:
            self.Close_Tab()

        return text

    def Crawling_NaverNews(self, url):
        text = ""
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            res = requests.get(url, headers=headers)
            soup = BeautifulSoup(res.text, "html.parser")
            self.driver.execute_script("window.open('');")
            self.driver.switch_to.window(self.driver.window_handles[1])
            self.driver.get(url)
            time.sleep(1)

            for idx, tmpPath in enumerate(self.comm_xPath):
                try:
                    text = self.driver.find_element(By.XPATH, f"//div[@id='{tmpPath}']").text
                    # text = f"[Container_{idx}]{text}"  # 디버깅용
                    break
                except:
                    print(f"Comm_xPath_{idx} Error")
                    text = "Comm_xPath Error"

        except NoSuchElementException as nosuch:
            print(nosuch)
            # Access Error
            try:
                text = self.driver.find_element(By.XPATH, "/html/body/center/font").text
            except:
                print("Unknown URL Error")
                text = "Unknown URL Error"
        except Exception as ex:
            text = f"Exception_xPath : {ex}"
        finally:
            self.Close_Tab()

        return text
