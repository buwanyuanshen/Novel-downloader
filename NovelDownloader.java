import javafx.application.Application;
import javafx.application.Platform;
import javafx.collections.FXCollections;
import javafx.collections.ObservableList;
import javafx.concurrent.Task;
import javafx.geometry.Insets;
import javafx.scene.Scene;
import javafx.scene.control.*;
import javafx.scene.layout.*;
import javafx.scene.text.Font;
import javafx.stage.Stage;
import org.jsoup.Jsoup;
import org.jsoup.nodes.Document;
import org.jsoup.select.Elements;
import org.openqa.selenium.By;
import org.openqa.selenium.Keys;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.chrome.ChromeOptions;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

public class NovelDownloader extends Application {
    private Map<String, String> chapters = new LinkedHashMap<>();
    private TextField novelNameInput;
    private CheckBox saveCheckBox;
    private ListView<String> chapterList;
    private TextArea chapterText;
    private WebDriver driver;

    public static void main(String[] args) {
        launch(args);
    }

    @Override
    public void start(Stage primaryStage) {
        primaryStage.setTitle("小说下载器");

        novelNameInput = new TextField();
        saveCheckBox = new CheckBox("是否下载小说内容到当前目录下");
        Button searchButton = new Button("获取");
        chapterList = new ListView<>();
        chapterText = new TextArea();

        VBox root = new VBox(10);
        root.setPadding(new Insets(10));
        HBox inputBox = new HBox(10);
        HBox.setHgrow(novelNameInput, Priority.ALWAYS);
        inputBox.getChildren().addAll(novelNameInput, saveCheckBox, searchButton);

        HBox contentBox = new HBox(10);
        contentBox.getChildren().addAll(createChapterPane(), chapterText);
        HBox.setHgrow(chapterText, Priority.ALWAYS);

        root.getChildren().addAll(new Label("请输入小说名称:"), inputBox, contentBox);

        searchButton.setOnAction(event -> {
            String novelName = novelNameInput.getText();
            if (!novelName.isEmpty()) {
                searchNovelAndScrape(novelName);
            } else {
                showAlert("警告", "请输入小说名称", Alert.AlertType.WARNING);
            }
        });

        chapterList.getSelectionModel().selectedItemProperty().addListener((observable, oldValue, newValue) -> {
            if (newValue != null) {
                showChapterContent(newValue);
            }
        });

        primaryStage.setScene(new Scene(root, 800, 600));
        primaryStage.show();
    }

    public VBox createChapterPane() {
        VBox chapterPane = new VBox(10);
        chapterPane.setPadding(new Insets(10));
        chapterPane.setStyle("-fx-background-color: #f1f1f1");

        HBox headerBox = new HBox(10);
        headerBox.setPadding(new Insets(5));
        headerBox.setStyle("-fx-background-color: #e1e1e1");

        Label chapterLabel = new Label("章节列表");
        chapterLabel.setFont(Font.font(14));

        Region spacer = new Region();
        HBox.setHgrow(spacer, Priority.ALWAYS);

        headerBox.getChildren().addAll(chapterLabel, spacer);

        chapterText.setEditable(false);
        chapterText.setWrapText(true);

        chapterPane.getChildren().addAll(headerBox, chapterList);

        VBox.setVgrow(chapterList, Priority.ALWAYS);
        return chapterPane;
    }

    public void searchNovelAndScrape(String novelName) {
        Task<Void> task = new Task<Void>() {
            @Override
            protected Void call() throws Exception {
                try {
                    setupChromeDriver();

                    driver.get("https://www.bige3.cc/");
                    WebElement searchInput = driver.findElement(By.xpath("/html/body/div[4]/div[1]/div[2]/form/input[1]"));
                    searchInput.sendKeys(novelName);
                    searchInput.sendKeys(Keys.ENTER);
                    WebDriverWait wait = new WebDriverWait(driver, 10);
                    wait.until(ExpectedConditions.presenceOfElementLocated(By.xpath("/html/body/div[5]/div/div/div/div/div[2]/h4/a")));

                    List<WebElement> elements = driver.findElements(By.xpath("/html/body/div[5]/div/div/div/div/div[2]/h4/a"));
                    if (elements.isEmpty()) {
                        showAlert("提示", "没有找到相关小说", Alert.AlertType.INFORMATION);
                        return null;
                    }

                    for (WebElement element : elements) {
                        element.click();
                        driver.switchTo().window(driver.getWindowHandles().stream().reduce((first, second) -> second).orElse(null));
                        wait.until(ExpectedConditions.presenceOfElementLocated(By.xpath("//*[@class='listmain']/dl/dd/a")));

                        List<WebElement> chapterElements = driver.findElements(By.xpath("//*[@class='listmain']/dl/dd/a"));
                        for (WebElement chapter : chapterElements) {
                            chapter.click();
                            while (true) {
                                wait.until(ExpectedConditions.presenceOfElementLocated(By.xpath("//*[@id='read']/div[5]/div[3]/h1")));
                                WebElement chapterTitleElement = driver.findElement(By.xpath("//*[@id='read']/div[5]/div[3]/h1"));
                                WebElement chapterContentElement = driver.findElement(By.xpath("//*[@id='chaptercontent']"));
                                String chapterTitle = chapterTitleElement.getText().replace("、", "");
                                String chapterContent = chapterContentElement.getAttribute("innerHTML")
                                        .replaceAll("无弹窗，更新快，免费阅读！", "")
                                        .replaceAll("请收藏本站：https://www.bige3.cc。笔趣阁手机版：https://m.bige3.cc", "")
                                        .replaceAll("『点此报错』『加入书签』", "");
                                if (saveCheckBox.isSelected()) {
                                    saveChapterToFile(novelName, chapterTitle, chapterContent);
                                }

                                String cleanContent = cleanChapterContent(chapterContent);
                                chapters.put(chapterTitle, cleanContent);
                                updateChapterList();

                                try {
                                    wait.until(ExpectedConditions.elementToBeClickable(By.xpath("//div[@class='Readpage pagedown']/a[@id='pb_next']")));
                                    WebElement nextButton = driver.findElement(By.xpath("//div[@class='Readpage pagedown']/a[@id='pb_next']"));
                                    nextButton.click();
                                } catch (Exception e) {
                                    break;
                                }
                            }
                            driver.navigate().back();
                        }
                    }

                } catch (Exception e) {
                    e.printStackTrace();
                    showAlert("提示", "运行出错", Alert.AlertType.ERROR);
                } finally {
                    cleanupChromeDriver();
                }

                return null;
            }
        };

        Thread thread = new Thread(task);
        thread.setDaemon(true);
        thread.start();
    }

    private void setupChromeDriver() {
        ChromeOptions options = new ChromeOptions();
        options.addArguments("--headless");
        options.addArguments("--no-sandbox");
        options.addArguments("--disable-dev-shm-usage");
        options.addArguments("--window-size=1920,1080");
        options.addArguments("user-agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36'");
        driver = new ChromeDriver(options);
    }

    private void cleanupChromeDriver() {
        if (driver != null) {
            driver.close();
            driver.quit();
        }
    }

    private void saveChapterToFile(String novelName, String chapterTitle, String chapterContent) {
        String bookDir = System.getProperty("user.dir") + "/" + novelName;
        File bookDirectory = new File(bookDir);
        if (!bookDirectory.exists()) {
            bookDirectory.mkdirs();
        }

        String chapterPath = bookDir + "/" + chapterTitle + ".txt";
        try (BufferedWriter writer = new BufferedWriter(new FileWriter(chapterPath))) {
            writer.write(chapterContent);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private String cleanChapterContent(String chapterContent) {
        Document doc = Jsoup.parse(chapterContent);
        Elements chapterBrElements = doc.select("br");
        return chapterBrElements.stream()
                .map(brElement -> brElement.nextSibling().toString().trim())
                .filter(text -> !text.isEmpty())
                .collect(Collectors.joining(""));
    }

    public void updateChapterList() {
        Platform.runLater(() -> {
            ObservableList<String> chapterTitles = FXCollections.observableArrayList(chapters.keySet());
            chapterList.setItems(chapterTitles);
        });
    }

    public void showChapterContent(String chapterTitle) {
        Platform.runLater(() -> {
            String content = chapters.get(chapterTitle);
            if (content != null) {
                content = content.replaceAll("<br>", "\n "); // Replace <br> with spaces
                chapterText.setText(content);
            }
        });
    }

    public static void showAlert(String title, String message, Alert.AlertType alertType) {
        Platform.runLater(() -> {
            Alert alert = new Alert(alertType);
            alert.setTitle(title);
            alert.setHeaderText(null);
            alert.setContentText(message);
            alert.showAndWait();
        });
    }

    @Override
    public void stop() {
        cleanupChromeDriver();
    }
}