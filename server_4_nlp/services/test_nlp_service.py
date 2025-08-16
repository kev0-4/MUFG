from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
def get_redirected_url(rss_url):
    try:    
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in background

        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        driver.get(rss_url)
        WebDriverWait(driver, 10).until(lambda d: d.current_url != rss_url)

        final_url = driver.current_url
        driver.quit()
        
        return final_url
    except Exception as e:
        print(f"Error with selenium: {e}")
        return None
# Test it
rss_url = "https://news.google.com/rss/articles/CBMixgFBVV95cUxQcUZDWHZrRlBGVk9HaHozSHBpYkZqdGJ6NmVjcHRYNzlObHo4VThKS0FCZWlUSmJpMDJtVS1ja3lCMGFqSGpZejlPV0pwRDhYR1dOZjE5czVpcE5Hd1lndXRXejE5RUlaZW82VTZjMmhMN2pra1VuY3c4Y0JSa0RtNzhFYmpoeHZJUkFIZnFkSU5EUWowWTFkelh6c3lZTkEzQ2lCbHBSeXRqcUFvR21oLUdEdzVqS2hNYm80WmpvRGRrelFiZmc?oc=5&hl=en-IN&gl=IN&ceid=IN:en"


import trafilatura

article_url = get_redirected_url(rss_url)

if article_url:
    downloaded = trafilatura.fetch_url(article_url)
    if downloaded:
        article_text = trafilatura.extract(downloaded)
        print("Extracted Content:\n", article_text)
    else:
        print("Failed to fetch article content")
