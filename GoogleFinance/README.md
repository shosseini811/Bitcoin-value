# Bitcoin Price Data Extractor

A simple tool to extract Bitcoin price data from Google Finance charts.

## Project Structure

```
GoogleFinance_clean/
├── data/
│   └── monthly/           # Monthly Bitcoin price data
│       ├── bitcoin_monthly_data.csv         # Extracted price data points
│       ├── bitcoin_monthly_chart_viz.png    # Visualization of the price chart
│       └── full_page.png                    # Original screenshot from Google Finance
├── docs/                  # Documentation
└── scripts/               # Python scripts
    ├── bitcoin_monthly_extractor.py  # Main script to extract data from monthly chart
    └── download_monthly_chart.py     # Script to download chart from Google Finance
```

## How to Use

1. Download a Bitcoin monthly chart from Google Finance:
   ```
   python scripts/download_monthly_chart.py
   ```

2. Extract price data from the chart:
   ```
   python scripts/bitcoin_monthly_extractor.py
   ```

3. View the results in the `data/monthly/` directory:
   - CSV file with price data points
   - Visualization of the price chart

## Requirements

- Python 3.6+
- OpenCV (cv2)
- NumPy
- Matplotlib
- Pandas
- Selenium (for downloading charts)
- Chrome WebDriver

## Installation

1. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```
   pip install opencv-python numpy matplotlib pandas selenium webdriver-manager
   ```

## How It Works

The Bitcoin Price Data Extractor works in two main steps:

1. **Download**: The `download_monthly_chart.py` script uses Selenium to navigate to Google Finance and take a screenshot of the Bitcoin price chart.

2. **Extract**: The `bitcoin_monthly_extractor.py` script processes the chart image to:
   - Detect the chart area in the screenshot
   - Identify the Bitcoin price line using color detection
   - Extract data points along the line
   - Convert pixel coordinates to actual dates and prices
   - Generate statistics and visualizations

## Results

The extraction produces:
- CSV file with date and price data
- Visualization of the price chart
- Statistics including:
  - Starting and ending prices
  - Percent change
  - Minimum and maximum prices
  - Average price
  - Price range
