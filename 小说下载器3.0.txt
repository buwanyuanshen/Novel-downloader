import os
import requests
import threading
import tkinter as tk
from lxml import etree
from bs4 import BeautifulSoup
from selenium import webdriver
from tkinter import ttk, messagebox
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class NovelDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("小说下载器")
        self.root.geometry("800x600")
        self.setup_styles()
        self.create_widgets()
        self.chapters = {}

    def setup_styles(self):
        # 设置界面元素样式
        style = ttk.Style()
        style.configure('TFrame', background='white')
        style.configure('TLabel', background='light green', font=('微软雅黑', 13), foreground='gray')
        style.configure('TButton', background='light blue', font=('微软雅黑', 13), foreground='blue')
        style.configure('TCheckbutton', background='light blue', font=('微软雅黑', 13))
        style.configure('TListbox', background='yellow', font=('微软雅黑', 12))
        style.configure('TText', background='white', font=('微软雅黑', 13))

    def create_widgets(self):
        # 创建界面元素
        ttk.Label(self.root, text="请输入小说名称:", font=('微软雅黑', 16),foreground='blue').pack(pady=10)
        self.entry = ttk.Entry(self.root, font=('Arial', 14))
        self.entry.pack(pady=5)

        self.save_checkbox_var = tk.BooleanVar()
        ttk.Checkbutton(self.root, text="是否下载小说内容到当前目录下", variable=self.save_checkbox_var, style="TCheckbutton").pack(pady=5)

        ttk.Button(self.root, text="获取(书源1<推荐>)", command=self.search_novel_source1, style="TButton").pack(pady=10)
        ttk.Button(self.root, text="获取(书源2)", command=self.search_novel_source2, style="TButton").pack(pady=10)

        self.create_listbox_frame()
        self.create_chapter_text_frame()

    def create_listbox_frame(self):
        # 创建小说章节列表框
        listbox_frame = ttk.Frame(self.root)
        listbox_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10)

        scrollbar = ttk.Scrollbar(listbox_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.listbox = tk.Listbox(listbox_frame, selectmode=tk.SINGLE, yscrollcommand=scrollbar.set, font=('微软雅黑', 12))
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar.config(command=self.listbox.yview)
        self.listbox.bind("<<ListboxSelect>>", self.show_chapter_content)

    def create_chapter_text_frame(self):
        # 创建章节内容显示框
        chapter_text_frame = ttk.Frame(self.root)
        chapter_text_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10)

        chapter_text_scrollbar = ttk.Scrollbar(chapter_text_frame)
        chapter_text_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.chapter_text = tk.Text(chapter_text_frame, yscrollcommand=chapter_text_scrollbar.set, font=('微软雅黑', 12))
        self.chapter_text.config(spacing1=10, spacing2=20)
        self.chapter_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        chapter_text_scrollbar.config(command=self.chapter_text.yview)

    def search_novel_source1(self):
        # 调用书源1的小说搜索方法
        self.search_novel(source=1)

    def search_novel_source2(self):
        # 调用书源2的小说搜索方法
        self.search_novel(source=2)

    def update_display(self):
        # 更新章节列表显示
        self.listbox.delete(0, tk.END)
        self.listbox.insert(tk.END, *self.chapters.keys())

    def show_chapter_content(self, event):
        # 显示选定章节的内容
        selected_title = self.listbox.get(self.listbox.curselection())
        self.chapter_text.delete("1.0", tk.END)
        self.chapter_text.insert(tk.END, self.chapters[selected_title])

    def crawl_novel_source1(self, keyword):
        # 使用 Selenium 抓取小说内容（书源1）
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument("--window-size=1920,1080")
        options.add_argument("user-agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36'")

        driver = webdriver.Chrome(options=options)

        try:
            driver.get("https://www.bige3.cc/")
            search_input = driver.find_element(By.XPATH, "/html/body/div[4]/div[1]/div[2]/form/input[1]")
            search_input.send_keys(keyword)
            search_input.send_keys(Keys.ENTER)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[5]/div/div/div/div/div[2]/h4/a")))

            elements = driver.find_elements(By.XPATH, "/html/body/div[5]/div/div/div/div/div[2]/h4/a")
            if not elements:
                messagebox.showinfo("提示", "没有找到相关小说")
                return

            for element in elements:
                element.click()
                driver.switch_to.window(driver.window_handles[-1])
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//*[@class='listmain']/dl/dd/a")))

                chapter = driver.find_elements(By.XPATH, "//*[@class='listmain']/dl/dd/a")[0]
                chapter.click()
                while True:
                    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//*[@id='read']/div[5]/div[3]/h1")))
                    chapter_title = driver.find_element(By.XPATH, "//*[@id='read']/div[5]/div[3]/h1")
                    chapter_content = driver.find_element(By.XPATH, "//*[@id='chaptercontent']")
                    html = chapter_content.get_attribute("innerHTML")
                    tree = etree.HTML(html)
                    content = tree.xpath("string(.)")
                    chapter_title_text = chapter_title.text.replace("、", "")
                    content = content.replace("无弹窗，更新快，免费阅读！", "")
                    content = content.replace("请收藏本站：https://www.bige3.cc。笔趣阁手机版：https://m.bige3.cc", "")
                    content = content.replace("『点此报错』『加入书签』", "")

                    if self.save_checkbox_var.get():
                        book_dir = os.path.join(os.getcwd(), keyword)
                        if not os.path.exists(book_dir):
                            os.makedirs(book_dir)

                        chapter_path = os.path.join(book_dir, f"{chapter_title_text}.txt")
                        with open(chapter_path, "w", encoding="utf-8") as f:
                            f.write(content)

                    self.chapters[chapter_title_text] = content
                    self.update_display()

                    try:
                        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="Readpage pagedown"]/a[@id="pb_next"]')))
                        next_button = driver.find_element(By.XPATH, '//div[@class="Readpage pagedown"]/a[@id="pb_next"]')
                        next_button.click()
                    except:
                        break

                driver.back()

        except Exception as e:
            messagebox.showinfo("提示", "运行完毕")
        finally:
            driver.close()
            driver.quit()

            if self.save_checkbox_var.get():
                messagebox.showinfo("提示", "小说下载完成")

    def crawl_novel_source2(self, keyword):
        # 使用 requests 和 BeautifulSoup 抓取小说内容（书源2）
        novel_name = keyword

        # 构建搜索 URL
        search_url = f"https://www.biquge66.net/search/?searchkey={novel_name}"

        # 发送 HTTP GET 请求到搜索页面
        search_response = requests.get(search_url)

        # 检查请求是否成功
        if search_response.status_code == 200:
            # 解析搜索页面内容
            search_soup = BeautifulSoup(search_response.content, "html.parser")

            # 查找第一个搜索结果并提取其 href
            first_result = search_soup.find("div", class_="image").find("a")
            if first_result:
                novel_href = first_result["href"]

                # 构建小说主页面的 URL
                novel_url = f"https://www.biquge66.net{novel_href}"

                # 发送 HTTP GET 请求到小说主页面
                response = requests.get(novel_url)

                # 检查请求是否成功
                if response.status_code == 200:
                    # 解析小说主页面内容
                    soup = BeautifulSoup(response.content, "html.parser")

                    # 查找所有章节链接
                    chapter_lists = soup.find_all("div", class_="flex flex-between book-info-main")

                    # 遍历每个章节链接并提取章节内容
                    for chapter_list in chapter_lists:
                        for chapter in chapter_list.find_all("a", rel="chapter"):
                            chapter_title = chapter.text  # 获取章节标题
                            chapter_url = "https://www.biquge66.net" + chapter["href"]  # 构建完整章节 URL

                            # 发送 HTTP GET 请求获取章节内容的第一页
                            chapter_response = requests.get(chapter_url)
                            chapter_soup = BeautifulSoup(chapter_response.content, "html.parser")

                            # 查找章节内容的第一页
                            chapter_content = chapter_soup.find("div", id="booktxt")

                            # 提取并打印章节内容的第一页
                            if chapter_content:
                                chapter_text = chapter_content.text.replace("本站最新网址：www.biquge66.net", "")  # 移除站点信息

                                # 检查是否有第二页
                                chapter_url2 = chapter_url.replace(".html", "_2.html")
                                chapter_response2 = requests.get(chapter_url2)
                                chapter_soup2 = BeautifulSoup(chapter_response2.content, "html.parser")
                                chapter_content2 = chapter_soup2.find("div", id="booktxt")

                                # 如果有第二页，将其与第一页拼接
                                if chapter_content2:
                                    chapter_text2 = chapter_content2.text.replace("本站最新网址：www.biquge66.net", "")  # 移除站点信息
                                    chapter_text += chapter_text2

                                if self.save_checkbox_var.get():
                                    book_dir = os.path.join(os.getcwd(), keyword)
                                    if not os.path.exists(book_dir):
                                        os.makedirs(book_dir)

                                    chapter_path = os.path.join(book_dir, f"{chapter_title}.txt")
                                    with open(chapter_path, "w", encoding="utf-8") as f:
                                        f.write(chapter_text)
                                chapter_title = chapter_title.replace("、","")
                                # 更新self.chapters字典
                                self.chapters[chapter_title] = chapter_text

                                # 更新显示
                                self.update_display()
                            else:
                                messagebox.showinfo("提示","无法获取章节内容: {chapter_title}\n")
                else:
                    messagebox.showerror("错误","无法检索小说页面: {novel_url}")
            else:
                messagebox.showwarning("警告","未找到给定小说名称的搜索结果")
        else:
            messagebox.showerror("错误","无法检索搜索结果页: {search_url}")

    def search_novel(self, source):
        keyword = self.entry.get()

        if not keyword:
            messagebox.showwarning("警告", "请输入小说名称")
            return

        threading.Thread(target=self.crawl_novel, args=(keyword, source)).start()

    def crawl_novel(self, keyword, source):
        if source == 1:
            self.crawl_novel_source1(keyword)
        elif source == 2:
            self.crawl_novel_source2(keyword)

if __name__ == "__main__":
    root = tk.Tk()
    # 设置背景颜色为浅蓝色
    root.configure(bg='light blue')
    app = NovelDownloader(root)
    root.mainloop()
