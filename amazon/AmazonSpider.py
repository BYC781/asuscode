from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from random import randint
import pandas as pd
from datetime import datetime

class AmazonSpider:

    def __init__(self):
        self.head = {
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-US,en;q=0.9,zh-TW;q=0.8,zh;q=0.7',
            'cookie': 'session-id=136-0340723-9192226; session-id-time=2082787201l; i18n-prefs=USD; lc-main=zh_TW; ubid-main=134-3980769-3693765; sp-cdn="L5Z9:TW"; csm-hit=tb:TZMAJPK9WYNJ0Y80TMZK+s-TZMAJPK9WYNJ0Y80TMZK|1660289724778&amp;t:1660289724778&amp;adb:adblk_no; session-token=k3RS++Iksjl7C0tJ6mcNq0RKrVUijnLF3sGiIoxeKYwsG3aTueKJ6BGxf1Z6C+j3R4W9UBC/Jlyv24bO/e4JyDPhLhiKZs64nYY0UmUBqtBsgRAkgHnkzJ4KCI2Soocp46TvfNQe7YzoO/vHjHXoCJ0bVCvhkshLYNLWvkQTSxIJaMYOP3a0Q5rSPnicXs3+54f73HotO2JZaPwBsmnxSVPrGpZpqRNI',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'
            }
        chrome_options = webdriver.ChromeOptions()
        prefs = {"profile.default_content_setting_values.notifications" : 2}
        chrome_options.add_experimental_option("prefs",prefs)
        self.driver = webdriver.Chrome()

    
    def relaunch_webdriver(self):
        chrome_options = webdriver.ChromeOptions()
        prefs = {"profile.default_content_setting_values.notifications" : 2}
        chrome_options.add_experimental_option("prefs",prefs)
        self.driver = webdriver.Chrome()



    def collect_product_page(self, firm, pages):
        self.theurl = []
        self.driver.get('https://www.amazon.com')
        for page in range(pages):
            # 去到你想要的網頁
            self.driver.get("https://www.amazon.com/s?k="+ firm +"&rh=n%3A172282%2Cp_89%3A"+ firm+ "&page="+ str(page))
            
            geturl = self.driver.find_elements(By.XPATH,'//h2/a')
            for j in geturl:
                self.theurl.append(j.get_attribute('href'))
                
            time.sleep(randint(5, 10))


    def initialize_df(self):
        columns = [
            'brand', 'title', 'url', 'price', 'star', 'starNum',
            'feature', 'productDscrp', 'view_url'
        ]
        self.df = pd.DataFrame(columns=columns)


    def init_process(self):
        self.start = 0
        self.process()
    

    def process(self):
        for page in range(self.start, len(self.theurl)):
            self.page = page
            print('第 '+ str(page) + ' 個商品')
            #儲存網址
            self.df.loc[page, 'url']= self.theurl[page]
            
            # 去到你想要的網頁
            self.driver.get(self.theurl[page])
            time.sleep(randint(2, 5))

            # 品牌名稱
            if len(self.driver.find_elements(By.ID, 'bylineInfo')) == 0 :
                self.df.loc[page, 'brand'] = 'No brand'
            else:
                self.df.loc[page, 'brand'] = self.driver.find_element(By.ID, 'bylineInfo').text

            # 商品名稱
            self.df.loc[page, 'title'] = self.driver.find_element(By.ID, 'title').text

            # 價格
            if len(self.driver.find_elements(By.XPATH, '//*[@id="corePrice_feature_div"]')) != 0:
                getprice = self.driver.find_element(By.XPATH, '//*[@id="corePrice_feature_div"]').text
                getprice = getprice.replace('US$', '').replace('\n', '.')
                try:
                    getprice = float(getprice)
                except ValueError:
                    getprice = ''
                self.df.loc[page, 'price'] = getprice
            else:
                self.df.loc[page, 'price'] = ''
            
            # 星星評分
            if len(self.driver.find_elements(By.ID, 'acrPopover'))==0:
                self.df.loc[page, 'star'] ='No star'
            else:
                self.df.loc[page, 'star'] =self.driver.find_element(By.ID, 'acrPopover').get_attribute("title").replace(' 顆星，最高 5 顆星','')

            # 星星數量
            if len(self.driver.find_elements(By.ID, 'acrCustomerReviewText')) == 0:
                self.df.loc[page, 'starNum'] = 0
            else:
                getglobalNum = self.driver.find_element(By.ID, 'acrCustomerReviewText').text
                getglobalNum = getglobalNum.replace(' 個評分','').replace(',','')
                self.df.loc[page, 'starNum'] = getglobalNum

            # product feature
            if len(self.driver.find_elements(By.ID, 'productOverview_feature_div')) != 0:
                self.df.loc[page, 'feature'] = self.driver.find_element(By.ID, 'productOverview_feature_div').text
            else:
                self.df.loc[page, 'feature'] = ''

            # prod descrip
            if len(self.driver.find_elements(By.ID, 'productDescription')) != 0:
                self.df.loc[page, 'productDscrp'] = self.driver.find_element(By.ID, 'productDescription').text
            else:
                self.df.loc[page, 'productDscrp'] = ''


            # 留言網址
            if len(self.driver.find_elements(By.XPATH,'//a[@data-hook = "see-all-reviews-link-foot"]'))== 0 :
                self.df.loc[page, 'view_url'] = 'No review'
            else:
                self.df.loc[page, 'view_url'] = self.driver.find_element(By.XPATH,'//a[@data-hook = "see-all-reviews-link-foot"]').get_attribute('href')

        return self.df
    
    def continue_process(self):
        if not hasattr(self, 'page'):
            print('Please use init_process first')
            return

        print('The previous work session was at page', self.page)
        self.start = self.page
        print('Continuing from page', self.start)
        self.process()


    

    def df_output(self, filename):
        self.df.to_csv(filename, index=False)



class AmazonReviewSpider:
  

    def __init__(self, amazon_obj):
        self.productData = amazon_obj
        self.head = {
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-US,en;q=0.9,zh-TW;q=0.8,zh;q=0.7',
            'cookie': 'session-id=136-0340723-9192226; session-id-time=2082787201l; i18n-prefs=USD; lc-main=zh_TW; ubid-main=134-3980769-3693765; sp-cdn="L5Z9:TW"; csm-hit=tb:TZMAJPK9WYNJ0Y80TMZK+s-TZMAJPK9WYNJ0Y80TMZK|1660289724778&amp;t:1660289724778&amp;adb:adblk_no; session-token=k3RS++Iksjl7C0tJ6mcNq0RKrVUijnLF3sGiIoxeKYwsG3aTueKJ6BGxf1Z6C+j3R4W9UBC/Jlyv24bO/e4JyDPhLhiKZs64nYY0UmUBqtBsgRAkgHnkzJ4KCI2Soocp46TvfNQe7YzoO/vHjHXoCJ0bVCvhkshLYNLWvkQTSxIJaMYOP3a0Q5rSPnicXs3+54f73HotO2JZaPwBsmnxSVPrGpZpqRNI',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'
            }
        chrome_options = webdriver.ChromeOptions()
        prefs = {"profile.default_content_setting_values.notifications" : 2}
        chrome_options.add_experimental_option("prefs",prefs)
        self.driver = webdriver.Chrome()
        self.dataframe_list = []


    def concat_dfs(self):
        self.merged_df = pd.concat(self.dataframe_list, ignore_index=True).drop_duplicates()
        return self.merged_df


    def initialize_df(self):
        columns = [
            'theproduct', 'theCommenturl', 'who', 'star', 'thetime', 'location',
            'SKU', 'comment', 'helpful']
        self.df = pd.DataFrame(columns=columns)
        return self.df


    def init_process(self):
        self.initialize_df()
        self.start = 0
        self.rowcnt = 0
        self.process()
        self.dataframe_list.append(self.df)

    def conti_process(self):
        self.dataframe_list.append(self.df)
        self.initialize_df()
        self.start = self.data
        self.process()
        self.dataframe_list.append(self.df)


    def process(self):
        for data in range(self.start, self.productData.shape[0]):
            self.data = data
            # 決定要抓取的網址
            print('現在處理第', data, '件商品')
            geturl = self.productData.iloc[data]['view_url']

            doit = True # 決定是否繼續進行留言爬蟲
            page = 1 # 爬到第幾頁
            if geturl == 'No review':
                print('No review')
                doit = False

            while doit:
                url = geturl + '&pageNumber=' + str(page)
                print(url)

            #請求網站
                self.driver.get(url)
            #將整個網站的程式碼爬下來
                getdata = self.driver.find_elements(By.CSS_SELECTOR, 'div[data-hook="review"]')
                if len(getdata) == 0:
                    doit = False
                else: # 判斷是否有流言資料，沒有就直接將doit改成False，停止執行
                    for i in getdata:
                        self.rowcnt += 1
                        self.df.loc[self.rowcnt, 'theproduct'] = self.productData.iloc[data]['title'] # 儲存商品名稱
                        self.df.loc[self.rowcnt, 'theCommenturl'] = self.productData.iloc[data]['view_url'] # 儲存留言網址
                        self.df.loc[self.rowcnt, 'who'] = i.find_element(By.CSS_SELECTOR, 'span.a-profile-name').text # 儲存留言者

                    # 處理星星
                        try:
                            getstart = i.find_element(By.CSS_SELECTOR, 'div:nth-child(2) > a > i > span').get_attribute('textContent')
                        except:
                            getstart = i.find_element(By.CSS_SELECTOR, 'div.a-row.a-spacing-none > i > span').get_attribute('textContent')
                        getstart = getstart.replace(' 顆星，最高 5 顆星','') # 中文網頁
                        getstart = getstart.replace(' out of 5 stars','') # 英文網頁
                        self.df.loc[self.rowcnt, 'star'] = float(getstart)

                    # 處理購買時間、地點
                        gettime = i.find_element(By.CSS_SELECTOR, 'span[data-hook="review-date"]').text
                        if 'Reviewed' in gettime: # 判斷是否為英文網頁
                            # 將英文月份換成數字，這樣待會才能給datetime辨別
                            gettime = gettime.replace('January','1')
                            gettime = gettime.replace('February','2')
                            gettime = gettime.replace('March','3')
                            gettime = gettime.replace('April','4')
                            gettime = gettime.replace('May','5')
                            gettime = gettime.replace('June','6')
                            gettime = gettime.replace('July','7')
                            gettime = gettime.replace('August','8')
                            gettime = gettime.replace('September','9')
                            gettime = gettime.replace('October','10')
                            gettime = gettime.replace('November','11')
                            gettime = gettime.replace('December','12')

                            gettime_list = gettime.split(' on ')
                            self.df.loc[self.rowcnt, 'thetime'] = (datetime.strptime(gettime_list[1], "%m %d, %Y")) # 儲存留言時間
                            self.df.loc[self.rowcnt, 'location'] = (gettime_list[0].replace('Reviewed in the ','')) # 儲存留言地點
                        else:
                            gettime_list = gettime.split('在')
                            cuttime = gettime_list[0].replace(' ','')
                            self.df.loc[self.rowcnt, 'thetime'] = (datetime.strptime(cuttime, "%Y年%m月%d日")) # 儲存留言時間
                            self.df.loc[self.rowcnt, 'location'] = (gettime_list[1].replace('評論','')) # 儲存留言地點

                    # 處理覺得留言有用人數
                        gethelpful = i.find_elements(By.CSS_SELECTOR, 'span[data-hook="helpful-vote-statement"]') # 儲存覺得留言有用人數
                        if len(gethelpful) != 0: # 判斷是否有資料
                            gethelpful = gethelpful[0].text
                            gethelpful = gethelpful.replace(',','') # 把千分位的「,」拿掉
                            gethelpful = gethelpful.replace(' 個人覺得有用','') # 中文網頁
                            gethelpful = gethelpful.replace(' people found this helpful','') # 英文網頁
                            if '一人覺得有用' == gethelpful or 'One person found this helpful' == gethelpful: # 判斷是否只有一人
                                self.df.loc[self.rowcnt, 'helpful'] = (1)
                            else:
                                self.df.loc[self.rowcnt, 'helpful'] = (int(gethelpful))
                        else:
                            self.df.loc[self.rowcnt, 'helpful'] = (0)

                    # 處理留言內容
                        if len(i.find_elements(By.CSS_SELECTOR, 'span[data-hook="review-body"]')) == 0:
                            self.df.loc[self.rowcnt, 'comment'] = ('')
                        else:
                            self.df.loc[self.rowcnt, 'comment'] = (i.find_elements(By.CSS_SELECTOR, 'span[data-hook="review-body"]')[0].text)

                    # 處理SKU
                        getsku = i.find_elements(By.CSS_SELECTOR, 'a[data-hook="format-strip"]')
                        if len(getsku) == 1: # 判斷是否有資料
                            self.df.loc[self.rowcnt, 'sku'] = (getsku[0].text)
                        else:
                            self.df.loc[self.rowcnt, 'sku'] = (None)

                    print('累積data:', self.rowcnt)
                    page += 1
                    time.sleep(randint(5,10))
            print(self.productData.iloc[data]['title'] + '****  DONE!')