import urllib.request as request
import os
import base64
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

manga_link = input("\nMangaDex Chapter Link: ")

chrome_options = Options()
chrome_options.add_argument("--headless")

driver = webdriver.Chrome(options=chrome_options)
driver.get(manga_link)

manga_name = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CLASS_NAME, "reader--header-manga"))).text

chapter_number = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.XPATH, "//div[@class='reader--meta chapter']"))).text


chapter_file_path = os.path.join(f"{manga_name} | RohanSensei", chapter_number)
if not os.path.exists(chapter_file_path):
    os.makedirs(chapter_file_path)

try:
    c = 1
    current_url = driver.current_url
    count = 0
    for i, char in enumerate(current_url):
        if char == '/':
            count += 1
            if count == 5:
                current_url = current_url[:i]
                break
    
    url_rn = driver.current_url
    count = 0
    for i, char in enumerate(url_rn):
        if char == '/':
            count += 1
            if count == 5:
                url_rn = url_rn[:i]
                break

    while c != 0:
        if current_url != url_rn:
            break
            c = 0
        else:         
            page = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//img[not(contains(@style, 'display: none')) and contains(@class, 'img') and contains(@class, 'sp') and contains(@class, 'limit-width') and contains(@class, 'limit-height') and contains(@class, 'mx-auto')]")))
            def get_file_content_chrome(driver, uri):
                result = driver.execute_async_script("""
                var uri = arguments[0];
                var callback = arguments[1];
                var toBase64 = function(buffer){for(var r,n=new Uint8Array(buffer),t=n.length,a=new Uint8Array(4*Math.ceil(t/3)),i=new Uint8Array(64),o=0,c=0;64>c;++c)i[c]="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/".charCodeAt(c);for(c=0;t-t%3>c;c+=3,o+=4)r=n[c]<<16|n[c+1]<<8|n[c+2],a[o]=i[r>>18],a[o+1]=i[r>>12&63],a[o+2]=i[r>>6&63],a[o+3]=i[63&r];return t%3===1?(r=n[t-1],a[o]=i[r>>2],a[o+1]=i[r<<4&63],a[o+2]=61,a[o+3]=61):t%3===2&&(r=(n[t-2]<<8)+n[t-1],a[o]=i[r>>10],a[o+1]=i[r>>4&63],a[o+2]=i[r<<2&63],a[o+3]=61),new TextDecoder("ascii").decode(a)};
                var xhr = new XMLHttpRequest();
                xhr.responseType = 'arraybuffer';
                xhr.onload = function(){ callback(toBase64(xhr.response)) };
                xhr.onerror = function(){ callback(xhr.status) };
                xhr.open('GET', uri);
                xhr.send();
                """, uri)
                if type(result) == int :
                    raise Exception("Request failed with status %s" % result)
                return base64.b64decode(result)

            bytes = get_file_content_chrome(driver, page.get_attribute("src"))
            
            image_path = os.path.join(chapter_file_path,f"Page{c}.jpg")
            if not os.path.exists(image_path):
                with open(image_path, "wb") as file:
                    file.write(bytes)
            
            c = c+1
            body = driver.find_element(By.TAG_NAME, "body")
            body.send_keys(Keys.ARROW_RIGHT)
            url_rn = driver.current_url
            count = 0
            for i, char in enumerate(url_rn):
                if char == '/':
                    count += 1
                    if count == 5:
                        url_rn = url_rn[:i]
                        break

finally:
    files = [(filename, os.path.getctime(os.path.join(chapter_file_path, filename))) for filename in os.listdir(chapter_file_path)]

    files.sort(key=lambda x: x[1])

    if files:
        last_file = files[-1][0]
        file_path = os.path.join(chapter_file_path, last_file)

        os.remove(file_path)

        print(f"\n{chapter_file_path} pages installed as image files successfully.\n")
    driver.quit()