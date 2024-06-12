import asyncio
import logging
from playwright.async_api import async_playwright
import pandas as pd

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
            
            # Property name
            name_element = await listing.query_selector('div[data-testid="listing-card-title"]')
            result['property_name'] = await name_element.text_content() if name_element else 'N/A'
            
            # Price
            price_element = await listing.query_selector('div._1jo4hgw')
            result['price'] = await price_element.text_content() if price_element else 'N/A'
            
            # URL
            url_element = await listing.query_selector('meta[itemprop="url"]')
            relative_url = await url_element.get_attribute('content') if url_element else 'N/A'
            result['url'] = f"https://www.airbnb.com{relative_url}" if relative_url.startswith('/') else relative_url
            
            # Visit each listing URL to fetch additional information, if available
            if result['url'] != 'N/A':
                logging.info(f"Visiting listing URL: {result['url']} ...")
                try:
                    # Open a new page for each listing
                    listing_page = await context.new_page()
                    await listing_page.goto('https://'+result['url'], timeout=600000, wait_until='networkidle')
                    
                    # Wait for the host's profile link to load and extract it
                    logging.info("Waiting for the host's profile link to load...")
                    await listing_page.wait_for_selector('div.colzjmk', state='attached')
                    host_link_element = await listing_page.query_selector('div.colzjmk a[aria-label="Go to Host full profile"]')
                    if host_link_element:
                        host_profile_link = await host_link_element.get_attribute('href')
                        result['host_profile_link'] = f"https://www.airbnb.com{host_profile_link}" if host_profile_link else 'N/A'
                        logging.info(f"Host profile link: {result['host_profile_link']}")
                    else:
                        result['host_profile_link'] = 'N/A'
                        logging.info("Host profile link not found.")
                    
                    # Extract reviews and comments
                    logging.info("Extracting reviews and comments.")
                    reviews = await listing_page.query_selector_all('div._88xxct')
                    review_texts = []
                    for review in reviews:
                        host_name_element = await review.query_selector('div.t9gtck5 h3')
                        comment_element = await review.query_selector('div.r1bctolv span span')
                        
                        host_name = await host_name_element.inner_text() if host_name_element else 'N/A'
                        comment = await comment_element.inner_text() if comment_element else 'N/A'
                        if host_name == 'N/A' or comment == 'N/A':
                            continue
                        review_texts.append({'host_name': host_name, 'comment': comment})
                        logging.info(f"Host name: {host_name}, Comment: {comment}")
                    
                    result['reviews and comments'] = review_texts
                
                except Exception as e:
                    logging.error(f"Error extracting information from {result['url']}: {e}")
                
                finally:
                    # Close the newly opened listing page
                    await listing_page.close()
            
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

# Export to Excel with headers
df.to_excel(excel_file_name, index=False, engine='openpyxl')

logging.info(f"Results saved to {excel_file_name}")