from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import InvalidSessionIdException, WebDriverException
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
import psutil

class DetailCrawling:
    def __init__(self):
        self.urlTypes = ['blog', 'cafearticle', 'news']
        self.Set_Driver()
        self.comm_xPath = ["contents", "container", "wrap", "articleBody", "dic_area"
            , "newsct_article", "newsEndContents", "newsEndContents", "article"
            , "article-view"]

    def Set_Driver(self):
        # 크롬 드라이버 불러오기
        # driverPath = "./SeleniumCrawling/chromedriver"  # 크롬드라이버 설치된 경로. 파이썬(.py) 저장 경로와 동일하면 그냥 파일명만
        driverPath = "./chromedriver.exe"
        service = Service(executable_path=driverPath)
        # print(os.getcwd())
        # brew install --cask chromedriver  크롬 업데이트 시 터미널에서 사용
        options = webdriver.ChromeOptions()
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        options.add_argument("--blink-settings=imagesEnabled=false")  # image not load
        options.add_argument("--disable-blink-features=AutomationControlled")
        # options.add_argument("headless")  # Not show
        options.add_argument("headless=new")  # Not show??
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-application-cache")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-extenstions")
        options.add_argument("--disable-background-networking")
        options.add_argument("--disable-background-timer-throttling")
        options.add_argument("--disable-background-occluded-windows")
        options.add_argument("--disable-site-isolation-trials")
        options.add_argument("--disable-sync")
        options.add_argument("--disable-translate")
        options.add_argument("--disable-default-apps")
        options.add_argument("--metrics-recording-only")
        options.add_argument("--no-sandbox")
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument("--hide-scrollbars")
        # options.add_argument("--enable-logging")
        # options.add_argument("--log-level=0")
        options.add_argument("--single-process")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--homedir=/tmp")
        options.add_argument("--disable-logging")
        options.add_argument("--log-level=3")
        options.add_argument("--js-flags=--max-old-space-size=1024")  # 가비지 컬렉터 제한
        options.add_argument("--enable-unsafe-swiftshader")
        options.add_argument("--mute-audio")
    
        self.driver = webdriver.Chrome(service=service, options=options)  # Open Chrome
        # self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        # self.wait = WebDriverWait(self.driver, 10)
        self.driver.set_page_load_timeout(30)
        self.driver.implicitly_wait(0)
        self.driver.set_window_size(720, 480)
        self.driver.execute_cdp_cmd("Network.enable", {})
        self.driver.execute_cdp_cmd("Network.setBlockedURLs", {"urls":["*.png", "*.jpg", "*.jpeg", "*.gif", "*.svg"]})

        # Crawling Speed up?
        caps = DesiredCapabilities.CHROME
        caps["pageLoadStrategy"] = "none"

    def Get_Memory_Usage(self):
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / 1024**2  # MB
    
    def Get_Chrome_Memory(self):
        chrome_mb = 0
        for proc in psutil.process_iter(['name', 'cmdline']):
            try:
                name = proc.info.get('name') or ""
                cmdline = proc.info.get('cmdline') or []

                if 'chrome' in name.lower() or any('chrome' in str(arg).lower() for arg in cmdline):
                    chrome_mb += proc.memory_info().rss / 1024**2
            except Exception as ex:
                print(f"Chrome : {ex}")
        
        return chrome_mb
    
    def Close_driver(self):
        try:
            if self.Get_Memory_Usage() > 512:
                self.kill_driver()
                time.sleep(1)
                self.Set_Driver()
            elif self.Get_Chrome_Memory() > 256:
                self.kill_driver()
                time.sleep(1)
                self.Set_Driver()
            else:
                self.Close_Tab()
        except Exception as ex:
            print(f"Close_driver : {ex}")

    def kill_driver(self):
        try:
            self.driver.delete_all_cookies()
            self.driver.quit()
            parent = psutil.Process(self.driver.service.process.pid)
            children = parent.children(recursive=True)
            for proc in children:
                proc.kill()
            if parent.is_running():
                parent.kill()
            if psutil.pid_exists(pid):
                os.kill(pid, 9)
        except:
            pass


    def Close_Tab(self):
        try:
            main = self.driver.window_handles
            for handle in main:
                if handle != main[0]:
                    self.driver.switch_to.window(handle)
                    self.driver.close()

            self.driver.switch_to.window(main[0])
        except Exception as ex:
            print(f"Close_Tab : {ex}")
            self.driver.quit()
            self.Set_Driver()
        finally:
            time.sleep(1)


    def Crawling_News(self, url):
        text = ""
        xPath = ""
        try:
            self.driver.execute_script("window.open('');")
            self.driver.switch_to.window(self.driver.window_handles[1])
            self.driver.get(url)
            self.driver.execute_script("window.stop();")
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
                        # text = f"[Container_{idx}]{text}"
                        break
                    except:
                        # print(f"Comm_xPath_{idx} Error")
                        # text = "Comm_xPath_Error"
                        text = ""
            else:
                text = self.driver.find_element(By.XPATH, f"//div[@id='{xPath}']").text

        except NoSuchElementException as nosuch:
            print(nosuch)
            # Access Error
            try:
                text = self.driver.find_element(By.XPATH, "/html/body/center/font").text
            except:
                print("Unknown URL Error")
                # text = "Unknown_URL_Error"
                text = ""
        except Exception as ex:
            print(f"xPath_Error : {ex}")
            # text = f"Exception_xPath_Error : {xPath}"
            text = ""
        finally:
            self.Close_driver()

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
                    # text = "Comm_xPath Error"
                    text = ""

        except NoSuchElementException as nosuch:
            print(nosuch)
            # Access Error
            try:
                text = self.driver.find_element(By.XPATH, "/html/body/center/font").text
            except:
                print("Unknown URL Error")
                # text = "Unknown URL Error"
                text = ""
        except Exception as ex:
            # text = f"Exception_xPath : {ex}"
            text = ""
        finally:
            self.Close_driver()

        return text
