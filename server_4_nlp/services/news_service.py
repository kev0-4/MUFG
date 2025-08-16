import json
from gnews import GNews
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
import trafilatura
from webdriver_manager.chrome import ChromeDriverManager

# --- Step 1: Setup GNews ---
google_news = GNews(language='en', country='IN', period='7d', max_results=1)

# --- Step 2: Function to get redirected URL with Selenium ---


def get_redirected_url(rss_url):
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--silent")

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)

        driver.get(rss_url)
        WebDriverWait(driver, 10).until(lambda d: d.current_url != rss_url)

        final_url = driver.current_url
        driver.quit()
        return final_url
    except Exception as e:
        print(f"Error resolving URL: {e}")
        return None

# --- Step 3: Fetch news + extract content ---


def fetch_news_with_content(query="finance"):
    news_items = google_news.get_news(query)
    results = []

    for item in news_items:
        gnews_url = item["url"]  # Google News redirect link
        final_url = get_redirected_url(gnews_url)

        article_text = None
        if final_url:
            downloaded = trafilatura.fetch_url(final_url)
            if downloaded:
                article_text = trafilatura.extract(downloaded)

        results.append({
            "title": item["title"],
            "published date": item.get("published date"),
            "content": article_text if article_text else "neutral"
        })


    return results

# --- Step 4: Entry function ---


def get_news_for_queries(queries):
    """
    Takes a list of search queries and returns a list of news articles with resolved URLs and extracted content.
    """
    all_results = []
    for q in queries:
        print(f"🔍 Fetching news for: {q}")
        results = fetch_news_with_content(q)
        all_results.extend(results)
    return all_results


# # Example usage
# if __name__ == "__main__":
#     queries = ["Artificial Intelligence"]
#     data = get_news_for_queries(queries)
#     print(json.dumps(data, indent=4, ensure_ascii=False))  # print preview
