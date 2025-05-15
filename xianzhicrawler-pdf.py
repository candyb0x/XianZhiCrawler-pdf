import re
import time
import os
import base64
import argparse
import urllib3
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def sanitize_filename(title):
    """清理非法文件名字符"""
    clean_title = re.sub(r'[\\/*?:"<>|]', '-', title).strip()
    return clean_title[:200]  # 限制文件名长度

def generate_pdf(article, num):
    print(f"\033[32m[+] Getting: {article}\033[0m")
    
    try:
        driver.get(article)
        # 验证检查
        if '滑动验证页面' in driver.page_source:
            print(f"\033[31m[!] Verification required: {article}\033[0m")
            return 2

        # 404检查
        if '您无权查看' in driver.page_source or '已被删除' in driver.page_source:
            print(f"\033[31m[!] 404 Not Found: {article}\033[0m")
            return 1
        # 等待文档加载
        WebDriverWait(driver, 3).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )

        # 等待 markdown-body 元素非空
        WebDriverWait(driver, 3).until(
            lambda d: d.find_element(By.ID, "markdown-body").get_attribute("innerHTML").strip() != ""
        )

        # 可选：再等待一下代码块 <card type="inline" name="codeblock"> 加载出来
        time.sleep(1)

    except TimeoutException:
        print(f"\033[31m[!] markdown-body 内容加载超时: {article}\033[0m")
        return 1

    # 获取标题
    try:
        title = driver.execute_script("return document.querySelector('.detail_title').innerText") or \
                driver.title.split('-')[0].strip()
    except:
        title = f"Article_{num}"
    
    clean_title = sanitize_filename(title)
    
    # 调整页面样式
    driver.execute_script("""
        // 隐藏无关元素
        ['.header', '.comment_box', 'footer'].forEach(selector => {
            const elements = document.querySelectorAll(selector);
            elements.forEach(e => e.style.display = 'none');
        });

        // 调整正文样式
        const content = document.getElementById('markdown-body');
        if (content) {
            content.style.padding = '20px';
            content.style.maxWidth = '1000px';
            content.style.margin = '0 auto';
        }
    """)

    # 生成PDF参数
    print_options = {
        "landscape": False,
        "displayHeaderFooter": False,
        "printBackground": True,
        "preferCSSPageSize": True,
        "paperWidth": 10.00,
        "paperHeight": 11.69,
    }

    # 通过CDP生成PDF
    try:
        pdf_data = driver.execute_cdp_cmd("Page.printToPDF", print_options)
        pdf_bytes = base64.b64decode(pdf_data['data'])
    except Exception as e:
        print(f"\033[31m[!] PDF generation failed: {e}\033[0m")
        return 1

    # 保存PDF
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, f"{clean_title}.pdf")
    
    with open(file_path, "wb") as f:
        f.write(pdf_bytes)

    print(f"\n\033[32m[*] PDF saved: {file_path}\033[0m")
    return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('start', type=int, help="起始文章页码")
    parser.add_argument('end', type=int, help="结束文章页码")
    args = parser.parse_args()

    # 浏览器配置
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')

    # 设置CDP支持
    chrome_prefs = {"printing.print_preview_sticky_settings.appState": '{"recentDestinations":[{"id":"Save as PDF","origin":"local"}],"selectedDestinationId":"Save as PDF","version":2}'}
    chrome_options.add_experimental_option("prefs", chrome_prefs)
    chrome_options.add_argument('--kiosk-printing')

    # 启动 WebDriver
    service = Service(r"C:\\Program Files\\Google\\Chrome\\Application\\chromedriver.exe")  # 修改为你实际的路径
    driver = webdriver.Chrome(service=service, options=chrome_options)
    # driver = webdriver.Chrome(service=service)

    output_dir = "pdf_output"

    print(f"开始抓取: {args.start} 到 {args.end}")
    for num in range(args.start, args.end - 1, -1):  # 倒序抓取
        article_url = f'https://xz.aliyun.com/news/{num}'
        ret = generate_pdf(article_url, num)
        
        if ret == 2:
            print("\033[31m[!] 需要人工验证，停止运行...\033[0m")
            break
        elif ret == 1:
            continue
        
    driver.quit()
