import asyncio
import logging
from playwright.async_api import async_playwright
import pandas as pd
import json

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def scrape_airbnb():
    logging.info("Starting to scrape Airbnb listings...")

    async with async_playwright() as pw:
        # Launch new browser
        logging.info("Launching browser...")
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # Go to Airbnb URL
        airbnb_url = 'https://www.airbnb.com/s/London--United-Kingdom/homes'
        logging.info(f"Navigating to {airbnb_url} ...")
        await page.goto(airbnb_url, timeout=600000, wait_until='networkidle')
        
        # Wait for the listings to load
        logging.info("Waiting for listings to load...")
        await page.wait_for_selector('div.g1qv1ctd.c1v0rf5q.dir.dir-ltr', state='attached')
        
        # Extract information from the main listings page
        logging.info("Extracting information from the main listings page...")
        results = []
        listings = await page.query_selector_all('div.c1l1h97y')
        
        for index, listing in enumerate(listings):
            logging.info(f"Processing listing {index + 1} out of {len(listings)}...")
            result = {}

            # Property Name 
            description_element = await listing.query_selector('meta[itemprop="name"]')
            result['property_name'] = await description_element.get_attribute('content') if description_element else 'N/A'
            
            # Property subtitles(s)
            name_elements = await listing.query_selector_all('div[data-testid="listing-card-subtitle"]')
            # Initialize an empty list to hold all subtitles for the current listing
            subtitles = []
            for name_element in name_elements:
                # Target the first span within the current name_element
                first_span = await name_element.query_selector('span:first-child')
                if first_span:  # Ensure the first span exists
                    subtitle_text = await first_span.text_content()
                    subtitles.append(subtitle_text.strip())  # Add the subtitle text to the list, stripping any extra whitespace
            if subtitles:
                # Property Description
                result['property_description'] = subtitles[1]  # Always use the first subtitle as the property name

            # Property classification
            classification_element = await listing.query_selector('div[data-testid="listing-card-title"]')
            result['property_classification'] = await classification_element.text_content() if classification_element else 'N/A'
            
            # Price
            price_element = await listing.query_selector('div._1jo4hgw')
            result['price'] = await price_element.text_content() if price_element else 'N/A'

            # Rating
            rating_element = await listing.query_selector('div.t1a9j9y7 span.a8jt5op')
            if rating_element:
                rating_text = await rating_element.text_content()
                # Parse the rating text
                rating_parts = rating_text.split(' out of ')
                rating_score = rating_parts[0] if rating_parts else 'N/A'
                rating_overall = '5' if len(rating_parts) > 1 else 'N/A'
                reviews_count = rating_text.split(', ')[-1].split(' ')[1] if ',' in rating_text else 'N/A'
                result['rating'] = {
                    'rating_score': rating_score,
                    'rating_overall': f"{rating_score} out of {rating_overall}",
                    'reviews_count': reviews_count
                }
            else:
                result['rating'] = {
                    'rating_score': 'N/A',
                    'rating_overall': 'N/A',
                    'reviews_count': 'N/A'
                }
            # URL
            url_element = await listing.query_selector('meta[itemprop="url"]')
            relative_url = await url_element.get_attribute('content') if url_element else 'N/A'
            result['url'] = f"https://www.airbnb.com{relative_url}" if relative_url.startswith('/') else relative_url
            results.append(result)
        
        # Close browser
        logging.info("Closing browser...")
        await browser.close()

        return results

# Run the scraper and save results to an Excel file
logging.info("Running the scraper...")
results = asyncio.run(scrape_airbnb())
logging.info("Scraper finished. Saving results to Excel file...")
df = pd.DataFrame(results)

# Specify the Excel file name
excel_file_name = 'airbnb_listings.xlsx'

json_file_name = 'airbnb_listings.json'

# Save results to JSON file
logging.info("Saving results to JSON file...")
with open(json_file_name, 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=4)

logging.info(f"Results saved to {json_file_name}")