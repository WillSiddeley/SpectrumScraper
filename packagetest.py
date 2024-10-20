from spectrum_scraper import scrape_license_data

geocodes = ["TEL-002", "TEL-007"]

# This will create a timestamped CSV file with the data 
for geocode in geocodes:
    scrape_license_data(geocode, "output.csv")