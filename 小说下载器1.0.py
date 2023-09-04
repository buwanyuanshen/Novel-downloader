进口tkinter如同坦克
从tkinter进口ttk，消息框
进口穿线
从selenium . 选择进口选择
从硒进口网络驱动
从硒。网络驱动.普通的进口经过
从硒。网络驱动.普通的.键进口键
从硒。网络驱动.支持.用户界面进口WebDriverWait
从硒。网络驱动.支持进口预期_条件如同欧盟委员会(欧洲佣金)
进口操作系统(操作系统)
从lxml进口etree

班级NovelDownloader:
    极好的 __init__(自我，根):
自我。根=根
自我。根.标题("小说下载器")
自我。根.几何学(" 800x600 ")

自我。设置_样式()
自我。创建_小部件()
自我。章 = {}

    极好的 设置_样式(自己):
风格=ttk .风格()
风格。配置(t框架'，背景=“白色”)
风格。配置(特拉贝尔，背景=“白色”，字体=(阿里亚尔, 13)，前景=海军)
风格。配置('按钮'，背景=“浅蓝色”，字体=(阿里亚尔, 13)，前景=绿色)
风格。配置('复选框按钮'，背景=“白色”，字体=(阿里亚尔, 13))
风格。配置('列表框'，背景=“白色”，字体=(阿里亚尔, 12))
风格。配置('文本'，背景=“白色”，字体=(阿里亚尔, 13))

    def create_widgets(self):
        ttk.Label(self.root, text="请输入小说名称:", font=('Arial', 16)).pack(pady=10)
        self.entry = ttk.Entry(self.root, font=('Arial', 14))
        self.entry.pack(pady=5)

        self.save_checkbox_var = tk.BooleanVar()
        ttk.Checkbutton(self.root, text="是否下载小说内容到当前目录下", variable=self.save_checkbox_var, style="TCheckbutton").pack(pady=5)

        ttk.Button(self.root, text="获取", command=self.search_novel, style="TButton").pack(pady=10)

        self.create_listbox_frame()
        self.create_chapter_text_frame()

    def create_listbox_frame(self):
        listbox_frame = ttk.Frame(self.root)
        listbox_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10)

        scrollbar = ttk.Scrollbar(listbox_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.listbox = tk.Listbox(listbox_frame, selectmode=tk.SINGLE, yscrollcommand=scrollbar.set, font=('Arial', 12))
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar.config(command=self.listbox.yview)
        self.listbox.bind("<<ListboxSelect>>", self.show_chapter_content)

    def create_chapter_text_frame(self):
chapter_text_frame = ttk框架(self.root)
chapter _ text _ frame . pack(side = tk。对，fill=tk。两者都有，expand=True，padx=10)

        chapter_text_scrollbar = ttk.Scrollbar(chapter_text_frame)
        chapter_text_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.chapter_text = tk.Text(chapter_text_frame, yscrollcommand=chapter_text_scrollbar.set, font=('Arial', 12))
        self.chapter_text.config(spacing1=10, spacing2=20)
        self.chapter_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        chapter_text_scrollbar.config(command=self.chapter_text.yview)

def搜索_小说(自我):
keyword = self.entry.get()

如果不是关键字:
messagebox.showwarning("警告", "请输入小说名称")
返回

穿线Thread(target=self.crawl_novel，args=(keyword，).开始()

定义更新_显示(自身):
        self.listbox.delete(0, tk.END)
        self.listbox.insert(tk.END, *self.chapters.keys())

    def show_chapter_content(self, event):
        selected_title = self.listbox.get(self.listbox.curselection())
        self.chapter_text.delete("1.0", tk.END)
        self.chapter_text.insert(tk.END, self.chapters[selected_title])

    def crawl_novel(self, keyword):
        options = Options()
        options.headless = True
options . add _ argument('-no-sandbox ')
options . add _ argument('-disable-dev-shm-usage ')
选项。add _ argument("-window-size = 1920，1080 ")
选项。add _ argument(" user-agent = ' Mozilla/5.0(Windows NT 10.0；win 64x 64)apple WebKit/537.36(KHTML，像壁虎一样)Chrome/95。0 .4638 .69 Safari/537.36 '”)

driver = webdriver .铬(选项=选项)

尝试:
司机. get(" https://www .bige 3 .抄送/")
搜索输入=驱动程序。find _ element(按.XPATH，"/html/body/div[4]/div[1]/div[2]/form/input[1]")
搜索输入发送关键字(关键字)
搜索输入发送关键字(键。回车)
WebDriverWait(驱动程序,10)。直到(欧共体。element _ located的存在性(.XPATH，"/html/body/div[5]/div/div/div/div[2]/H4/a "))

元素=驱动因素。查找_元素（按。XPATH，"/html/body/div[5]/div/div/div/div[2]/H4/a ")
如果不是元素:
messagebox.showinfo("提示", "没有找到相关小说")
返回

对于元素中的元素:
element.click()
司机。切换到。车窗(驾驶员。窗口句柄[-1])
WebDriverWait(驱动程序,10)。直到(欧共体。element _ located的存在性(.XPATH，"//*[@class='listmain']/dl/dd/a ")))

章节=驱动程序。查找_元素（按。XPATH，"//*[@ class = ' listmain ']/dl/DD/a ")[0]
chapter.click()
虽然正确:
WebDriverWait(驱动程序,10)。直到（欧共体.元素_已定位的存在性(.XPATH，"//*[@ id = ' read ']/div[5]/div[3]/h1 "))
章节标题=司机查找元素(按. XPATH，"//*[@ id = ' read ']/div[5]/div[3]/h1 ")
章_内容=驱动程序find _ element(按。XPATH，"//*[@id='chaptercontent']")
html =章节_内容get _ attribute(" innerHTML ")。
树= etreeHTML(HTML)
content = tree.xpath("string。)")
章节标题=章节标题。文字。替换("、"、")
content = content.replace("无弹窗,更新快,免费阅读!", "")
content = content.replace("请收藏本站:https://www.bige3.cc .笔趣阁手机版:https://m.bige3.cc "，"")
内容=内容。替换(“和点此报错"《加入书签》"、" )

if self.save_checkbox_var.get():
book _ dir = OS .路径。加入（操作系统getcwd()，关键字)
如果不是os.path.exists(book_dir):
os.makedirs(book_dir)

chapter _ path = OS。路径。join(book _ dir，f"{chapter_title_text} .txt”)
用打开(chapter_path，" w "，encoding="utf-8 ")作为女：
f .写（内容)

自我。章节[章节标题正文]=内容
self.update_display()

尝试:
WebDriverWait(驱动程序,10)。直到可点击的。XPATH，'//div[@ class = " read page page down "]/a[@ id = " Pb _ next "]'))
next _ button =驱动程序查找元素（按. XPATH，'//div[@ class = " read page page down "]/a[@ id = " Pb _ next "]')
next_button.click()
除了:
破裂

driver.back()

例外情况为e:
messagebox.showinfo("提示", "运行完毕")
最后:
driver.close()
driver.quit()

if self.save_checkbox_var.get():
messagebox.showinfo("提示", "小说下载完成")

if __name__ == "__main__ ":
root = tk。Tk()
app = NovelDownloader(root)
根.主循环()
