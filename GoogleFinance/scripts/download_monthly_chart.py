from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

"""
This script downloads the 1-month Bitcoin chart from Google Finance.
It uses Selenium to navigate to the page, click the 1M button, and take a screenshot.
"""

# Create output directory
output_dir = '../data/monthly'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Set up Chrome options
options = Options()
# options.add_argument('--headless')  # Uncomment this when everything works
options.add_argument('--window-size=1920,1080')
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.7049.95 Safari/537.36")

# Initialize the Chrome driver
print("Starting Chrome...")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

try:
    # Navigate to Google Finance Bitcoin page
    print("Loading Google Finance Bitcoin page...")
    driver.get("https://www.google.com/finance/quote/BTC-USD?window=1M")
    time.sleep(5)  # Wait for page to load
    
    # Find and click the 1M button if needed
    try:
        one_month_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[text()='1M']"))
        )
        one_month_button.click()
        print("Clicked on 1M button")
        time.sleep(3)  # Wait for chart to update
    except:
        print("Already on 1M view or button not found")
    
    # Take a screenshot of the entire page
    print("Taking screenshot...")
    driver.save_screenshot(f"{output_dir}/full_page.png")
    
    # Try to find the chart element
    try:
        chart_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "svg, canvas, div[role='img'], .chart-container"))
        )
        
        # Take a screenshot of just the chart
        print("Taking screenshot of chart...")
        chart_element.screenshot(f"{output_dir}/bitcoin_monthly_chart.png")
        print(f"Saved chart to {output_dir}/bitcoin_monthly_chart.png")
    except:
        print("Could not find chart element, using full page screenshot")
        # We'll use the full page screenshot and crop it later
    
    print("Screenshots taken successfully")
    
except Exception as e:
    print(f"Error: {e}")
    
finally:
    # Clean up
    print("Closing browser...")
    driver.quit()

print("\nDownload complete!")
print(f"Check {output_dir}/ for the screenshots")
