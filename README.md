
### Step 1: Install Python
Make sure you have Python installed on your machine. You can download it from [Python's official website](https://www.python.org/).

### Step 2: Open Command Line/Terminal
Open your Command Line (CMD) on Windows or Terminal on macOS/Linux.

### Step 3: Install Required Packages
Install the necessary Python packages using `pip`:

1. **Upgrade pip:**
    ```sh
    pip install --upgrade pip
    ```

2. **Install Dependencies:**
    ```sh
    pip install playwright pandas openpyxl
    ```

3. **Install Playwright Browsers:**
    ```sh
    playwright install
    ```

### Step 4: Save the Script
Save the provided Python script into a file named `scrape_airbnb.py` using a text editor like Notepad, Notepad++, VS Code, etc.

### Step 5: Run the Script
Run the script using Python:

```sh
python scrape_airbnb.py
```

And that's it! Your script should now run and generate the `airbnb_listings.xlsx` file with the scraped data.

### Full Setup Commands (Simplified)
Here's a summary of all the commands:

```sh
# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install playwright pandas openpyxl

# Install Playwright browsers
playwright install

# Save the script to a file named 'scrape_airbnb.py' and then run the script
python scrape_airbnb.py
```

### Additional Notes:
- Ensure you have an active internet connection when running the script, as it needs to load the webpages from Airbnb.
- The results will be saved in an Excel file named `airbnb_listings.xlsx` in the same directory where you run the script.
- If you encounter issues, make sure the URL selectors and HTML structure have not changed on Airbnb's website, as this might require adjustments in the script.