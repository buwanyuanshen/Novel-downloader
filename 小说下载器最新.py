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
        self.is_getting_novel = False # Flag to control novel getting process
        self.is_downloading_novel = False # Flag to control novel downloading process
        self.getting_thread = None # To store the getting novel thread
        self.download_thread = None # To store the download novel thread
        self.current_keyword = "" # Store current keyword for download

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

        self.get_button_text = tk.StringVar(value="开始获取(书源1<推荐>)")
        self.get_novel_button = ttk.Button(self.root, textvariable=self.get_button_text, command=self.start_stop_get_novel, style="TButton")
        self.get_novel_button.pack(pady=10)

        self.download_button = ttk.Button(self.root, text="下载小说", command=self.start_download_novel, style="TButton", state=tk.DISABLED)
        self.download_button.pack(pady=10)

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

    def start_stop_get_novel(self):
        keyword = self.entry.get()
        if not keyword:
            messagebox.showwarning("警告", "请输入小说名称")
            return

        if not self.is_getting_novel:
            self.start_get_novel(keyword)
        else:
            self.stop_get_novel()

    def start_get_novel(self, keyword):
        self.current_keyword = keyword
        self.is_getting_novel = True
        self.get_button_text.set("停止获取")
        self.chapters = {} # Clear previous chapters
        self.update_display() # Clear listbox
        self.download_button.config(state=tk.DISABLED) # Disable download button while getting
        self.getting_thread = threading.Thread(target=self.crawl_novel, args=(keyword, 1)) # Only source 1 now
        self.getting_thread.start()

    def stop_get_novel(self):
        self.is_getting_novel = False
        self.get_button_text.set("开始获取(书源1<推荐>)")

    def after_get_novel(self):
        if not self.is_getting_novel:
            self.get_button_text.set("开始获取(书源1<推荐>)")
            self.download_button.config(state=tk.NORMAL) # Enable download button after getting
            messagebox.showinfo("提示", "小说获取完成")


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
            driver.get("https://www.bqgui.cc/")
            search_input = driver.find_element(By.XPATH, "/html/body/div[4]/div[1]/div[2]/form/input[1]")
            search_input.send_keys(keyword)
            search_input.send_keys(Keys.ENTER)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[5]/div/div/div/div/div[2]/h4/a")))

            elements = driver.find_elements(By.XPATH, "/html/body/div[5]/div/div/div/div/div[2]/h4/a")
            if not elements:
                messagebox.showinfo("提示", "没有找到相关小说")
                return

            for element in elements:
                if not self.is_getting_novel: # Check if getting should stop before starting a new novel
                    break
                element.click()
                driver.switch_to.window(driver.window_handles[-1])
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//*[@class='listmain']/dl/dd/a")))

                chapter = driver.find_elements(By.XPATH, "//*[@class='listmain']/dl/dd/a")[0]
                chapter.click()
                while True:
                    if not self.is_getting_novel: # Check if getting should stop before starting a new chapter
                        break
                    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//*[@id='read']/div[5]/div[3]/h1")))
                    chapter_title = driver.find_element(By.XPATH, "//*[@id='read']/div[5]/div[3]/h1")
                    chapter_content = driver.find_element(By.XPATH, "//*[@id='chaptercontent']")
                    html = chapter_content.get_attribute("innerHTML")
                    tree = etree.HTML(html)
                    content = tree.xpath("string(.)")
                    chapter_title_text = chapter_title.text.replace("、", "")
                    content = content.replace("无弹窗，更新快，免费阅读！", "")
                    content = content.replace("请收藏本站：https://www.bi01.cc。笔趣阁手机版：https://m.bi01.cc", "")
                    content = content.replace("『点此报错』『加入书签』", "")


                    self.chapters[chapter_title_text] = content
                    self.update_display()

                    try:
                        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="Readpage pagedown"]/a[@id="pb_next"]')))
                        next_button = driver.find_element(By.XPATH, '//div[@class="Readpage pagedown"]/a[@id="pb_next"]')
                        next_button.click()
                    except:
                        break

                driver.back()
                if not self.is_getting_novel: # Check if getting should stop after finishing a novel
                    break


        except Exception as e:
            messagebox.showinfo("提示", "运行完毕")
        finally:
            driver.close()
            driver.quit()
            self.is_getting_novel = False # Reset flag
            self.after_get_novel() # Call after get novel function to update button and message


    def crawl_novel(self, keyword, source):
        if source == 1:
            self.crawl_novel_source1(keyword)


    def start_download_novel(self):
        if not self.chapters:
            messagebox.showwarning("警告", "请先获取小说章节列表")
            return

        if not self.is_downloading_novel:
            self.is_downloading_novel = True
            self.download_button.config(text="停止下载")
            self.download_thread = threading.Thread(target=self._download_novel_to_file, args=(self.current_keyword,))
            self.download_thread.start()
        else:
            self.stop_download_novel()


    def stop_download_novel(self):
        self.is_downloading_novel = False
        self.download_button.config(text="下载小说")

    def after_download_novel(self):
         if not self.is_downloading_novel:
            self.download_button.config(text="下载小说")
            messagebox.showinfo("提示", "小说下载完成")


    def _download_novel_to_file(self, keyword):
        try:
            book_dir = os.path.join(os.getcwd(), keyword)
            if not os.path.exists(book_dir):
                os.makedirs(book_dir)

            for chapter_title_text, content in self.chapters.items():
                if not self.is_downloading_novel: # Check if download should stop before starting a new chapter file
                    break
                chapter_path = os.path.join(book_dir, f"{chapter_title_text}.txt")
                with open(chapter_path, "w", encoding="utf-8") as f:
                    f.write(content)
        except Exception as e:
            messagebox.showerror("错误", f"下载小说失败: {e}")
        finally:
            self.is_downloading_novel = False # Reset flag
            self.after_download_novel() # Call after download function to update button and message


if __name__ == "__main__":
    root = tk.Tk()
    # 设置背景颜色为浅蓝色
    root.configure(bg='light blue')
    app = NovelDownloader(root)
    root.mainloop()