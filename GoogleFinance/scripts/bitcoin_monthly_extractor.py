import cv2
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
from datetime import datetime, timedelta

"""
Bitcoin Monthly Chart Data Extractor

This script extracts price data from a 1-month Bitcoin chart image.
It processes the chart image to identify the price line, extract data points,
and generate analysis of Bitcoin price movements.
"""

def extract_bitcoin_monthly_data(image_path=None, output_dir='../data/monthly'):
    """Main function to extract Bitcoin price data from a monthly chart image."""
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Use default image path if none provided
    if image_path is None:
        image_path = f"{output_dir}/full_page.png"
    
    # Step 1: Load and validate the chart image
    print("Loading Bitcoin monthly chart image...")
    if not os.path.exists(image_path):
        print(f"Error: Could not find image at {image_path}")
        return None
    
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: Could not read image at {image_path}")
        return None
    
    # Convert to RGB for better visualization
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # Step 2: Extract the chart area from the full image
    print("Finding chart area in the full page...")
    chart_area = detect_chart_area(image)
    x, y, w, h = chart_area
    print(f"Detected chart area: x={x}, y={y}, width={w}, height={h}")
    
    # Extract just the chart area
    chart = image_rgb[y:y+h, x:x+w]
    
    # Save the chart area for reference
    cv2.imwrite(f"{output_dir}/chart_area.png", cv2.cvtColor(chart, cv2.COLOR_RGB2BGR))
    
    # Step 3: Define the price and date ranges for the chart
    min_price = 74000  # Bottom of chart (lowest price in the month)
    max_price = 88000  # Top of chart (highest price in the month)
    
    start_date = datetime(2025, 3, 17)  # Adjust based on the chart
    end_date = datetime(2025, 4, 17)    # Adjust based on the chart
    total_days = (end_date - start_date).days
    
    # Step 4: Detect the Bitcoin price line in the chart
    combined_mask = detect_price_line(chart)
    
    # Step 5: Extract data points from the line
    data_points = extract_data_points(combined_mask, total_days)
    print(f"Extracted {len(data_points)} data points")
    
    # Create a visualization of the extracted points
    chart_viz = chart.copy()
    for x, y in data_points:
        cv2.circle(chart_viz, (x, y), 2, (255, 0, 0), -1)
    cv2.imwrite(f"{output_dir}/extracted_points.png", cv2.cvtColor(chart_viz, cv2.COLOR_RGB2BGR))
    
    # Step 6: Convert pixel coordinates to actual values
    price_data = []
    for x, y in data_points:
        # Calculate the price based on y position (0 = top/highest price, 1 = bottom/lowest price)
        y_norm = y / chart.shape[0]
        price = max_price - y_norm * (max_price - min_price)
        
        # Calculate the date based on x position (0 = left/start date, 1 = right/end date)
        x_norm = x / chart.shape[1]
        day_offset = int(x_norm * total_days)
        date = start_date + timedelta(days=day_offset)
        date_str = date.strftime('%Y-%m-%d')
        
        # Add to price data
        price_data.append({
            'x': x,
            'y': y,
            'date': date_str,
            'price': price
        })
    
    # Step 7: Save data to CSV
    df = pd.DataFrame(price_data)
    csv_path = f"{output_dir}/bitcoin_monthly_data.csv"
    df.to_csv(csv_path, index=False)
    print(f"Saved {len(price_data)} data points to {csv_path}")
    
    # Step 8: Create visualizations and statistics
    create_price_chart(price_data, output_dir)
    generate_statistics(price_data, start_date, end_date, output_dir)
    
    return df

def detect_chart_area(image):
    """Detect the chart area in the full page screenshot."""
    # Convert to grayscale for processing
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)
    
    # Find the chart area (usually one of the largest contours)
    chart_area = None
    for contour in contours[:10]:  # Check the 10 largest contours
        x, y, w, h = cv2.boundingRect(contour)
        if w > image.shape[1] * 0.5 and h > image.shape[0] * 0.2 and w/h > 1.5 and w/h < 4:
            chart_area = (x, y, w, h)
            break
    
    if chart_area is None:
        # If we couldn't find a chart area, use a reasonable default
        print("Could not automatically detect chart area. Using default values.")
        x = int(image.shape[1] * 0.1)
        y = int(image.shape[0] * 0.3)
        w = int(image.shape[1] * 0.8)
        h = int(image.shape[0] * 0.4)
        chart_area = (x, y, w, h)
    
    return chart_area

def detect_price_line(chart):
    """Detect the Bitcoin price line in the chart using color detection and edge detection."""
    # Convert chart to HSV color space for better color detection
    chart_hsv = cv2.cvtColor(chart, cv2.COLOR_RGB2HSV)
    
    # Bitcoin line in Google Finance monthly chart is usually green
    lower_green = np.array([40, 50, 50])
    upper_green = np.array([80, 255, 255])
    green_mask = cv2.inRange(chart_hsv, lower_green, upper_green)
    
    # Also try to detect the line using edge detection
    chart_gray = cv2.cvtColor(chart, cv2.COLOR_RGB2GRAY)
    chart_blur = cv2.GaussianBlur(chart_gray, (5, 5), 0)
    edges = cv2.Canny(chart_blur, 50, 150)
    
    # Combine the green mask and edges for better line detection
    combined_mask = cv2.bitwise_or(green_mask, edges)
    return combined_mask

def extract_data_points(combined_mask, total_days):
    """Extract data points from the price line mask."""
    data_points = []
    num_samples = total_days
    step = combined_mask.shape[1] // num_samples
    
    # For each x position, find the y position of the line
    for i in range(num_samples):
        x = i * step
        if x >= combined_mask.shape[1]:
            continue
            
        # Get the column of pixels at this x position
        column = combined_mask[:, x]
        y_values = np.where(column > 0)[0]
        
        if len(y_values) > 0:
            # Take the median y value to avoid outliers
            y = int(np.median(y_values))
            data_points.append((x, y))
    
    return data_points

def create_price_chart(price_data, output_dir):
    """Create a visualization of the price chart."""
    plt.figure(figsize=(12, 6))
    
    # Plot the extracted data
    plt.plot([pd.to_datetime(p['date']) for p in price_data], 
             [p['price'] for p in price_data], 'g-', linewidth=2)
    plt.scatter([pd.to_datetime(p['date']) for p in price_data], 
                [p['price'] for p in price_data], color='red', s=10)
    
    # Add labels and grid
    plt.title('Bitcoin Price Chart (1-Month Period)', fontsize=16)
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Price (USD)', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.gcf().autofmt_xdate()
    plt.gca().yaxis.set_major_formatter(plt.matplotlib.ticker.StrMethodFormatter('{x:,.0f}'))
    
    # Add some padding to the y-axis
    y_min = min([p['price'] for p in price_data]) * 0.998
    y_max = max([p['price'] for p in price_data]) * 1.002
    plt.ylim(y_min, y_max)
    
    # Save the chart
    chart_path = f"{output_dir}/bitcoin_monthly_chart_viz.png"
    plt.savefig(chart_path, dpi=300, bbox_inches='tight')
    print(f"Saved price chart visualization to {chart_path}")

def generate_statistics(price_data, start_date, end_date, output_dir):
    """Calculate and save statistics about the price data."""
    prices = [p['price'] for p in price_data]
    stats = {
        'min_price': min(prices),
        'max_price': max(prices),
        'avg_price': sum(prices) / len(prices),
        'price_range': max(prices) - min(prices),
        'start_price': prices[0],
        'end_price': prices[-1],
        'percent_change': (prices[-1] - prices[0]) / prices[0] * 100,
        'data_points': len(prices)
    }
    
    # Print statistics
    print("\nExtraction complete!")
    print(f"All results saved to {output_dir}/")
    print("\nStatistics:")
    print(f"Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    print(f"Starting Price: ${stats['start_price']:,.2f}")
    print(f"Ending Price: ${stats['end_price']:,.2f}")
    print(f"Percent Change: {stats['percent_change']:+.2f}%")
    print(f"Min Price: ${stats['min_price']:,.2f}")
    print(f"Max Price: ${stats['max_price']:,.2f}")
    print(f"Avg Price: ${stats['avg_price']:,.2f}")
    print(f"Price Range: ${stats['price_range']:,.2f}")

# Run the extraction if this script is executed directly
if __name__ == "__main__":
    extract_bitcoin_monthly_data()
