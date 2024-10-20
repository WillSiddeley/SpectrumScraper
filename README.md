# Spectrum Scraper

A Python package to scrape spectrum license data from the Government of Canada website.

## Installation

Install from  GitHub:
```bash
git clone git@github.com:WillSiddeley/SpectrumScraper.git
```

Install the Spectrum Scraper package:
```bash
cd SpectrumScraper
pip install .
```

Now, in your own project:
```python
from spectrum_scraper import scrape_license_data

geocode = "TEL-002"

# This will create a timestamped CSV file with the data 
scrape_license_data(geocode)
```