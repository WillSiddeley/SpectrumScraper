# Spectrum Scraper

A Python package to scrape spectrum license data from the Government of Canada website.

## Prerequisites

Docker must be installed. 

If you are running on Windows / Mac, download Docker Desktop from the [Docker website](https://www.docker.com/products/docker-desktop).

If you are running on Linux, follow the instructions on the [Docker CLI installation page](https://docs.docker.com/engine/install/).

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