"""
Debug utility to fetch and display eBird rare bird alerts
"""
import sys
import os
import json
from datetime import datetime
import argparse
import requests

# Add parent directory to path so we can import our modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from src.ebird_fetcher import EBirdFetcher
from config.config import COUNTIES

def display_alert(alert, index=None):
    """Display a single alert in a formatted way"""
    prefix = f"[{index}] " if index is not None else ""
    print(f"\n{prefix}{'=' * 50}")
    print(f"Species: {alert['species']}")
    if alert['scientificName']:
        print(f"{alert['scientificName']}")
    print(f"Count: {alert['count']}")
    print(f"Date: {alert['date']}")
    print(f"Location: {alert['location']}")
    print(f"Observer: {alert['observer']}")
    print(f"URL: {alert['checklistUrl']}")
    print(f"{'=' * 50}")

def save_html_report(alerts, county, filename):
    """Save alerts as an HTML report for better visualization"""
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>eBird RBA Debug - {county['name']} County</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .header {{ background-color: #43a047; color: white; padding: 10px; text-align: center; }}
            .alert {{ border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 4px; }}
            .alert:hover {{ background-color: #f5f5f5; }}
            .species {{ font-size: 18px; font-weight: bold; color: #2e7d32; }}
            .scientific {{ font-style: italic; color: #555; margin-bottom: 8px; }}
            .details {{ margin-top: 10px; }}
            .url {{ margin-top: 10px; }}
            a {{ color: #2e7d32; text-decoration: none; }}
            a:hover {{ text-decoration: underline; }}
            .timestamp {{ text-align: center; color: #666; margin: 20px 0 10px 0; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>eBird Rare Bird Alerts</h1>
            <h2>{county['name']} County, {county['state']}</h2>
        </div>
        
        <div class="timestamp">
            Data fetched on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>
    """
    
    for alert in alerts:
        scientific_html = f"<div class='scientific'>{alert['scientificName']}</div>" if alert['scientificName'] else ""
        html += f"""
        <div class="alert">
            <div class="species">{alert['species']}</div>
            {scientific_html}
            <div class="details">
                <strong>Count:</strong> {alert['count']} • 
                <strong>Date:</strong> {alert['date']} • 
                <strong>Location:</strong> {alert['location']} • 
                <strong>Observer:</strong> {alert['observer']}
            </div>
            <div class="url">
                <a href="{alert['checklistUrl']}" target="_blank">View on eBird</a>
            </div>
        </div>
        """
    
    html += """
    </body>
    </html>
    """
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"\nHTML report saved to {filename}")
    return filename

def save_raw_html(url, filename):
    """
    Fetch and save the raw HTML from the eBird website to help with debugging
    
    Args:
        url: URL to fetch
        filename: File to save the HTML to
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        print(f"\nRaw HTML saved to {filename}")
        return True
    except Exception as e:
        print(f"Error saving raw HTML: {e}")
        return False

def extract_html_sample(url, alert_class='.Observation', output_file=None):
    """
    Extract a sample of the HTML structure around bird observations to help with debugging
    
    Args:
        url: URL to fetch
        alert_class: CSS selector for the alert container
        output_file: File to save the HTML sample to
    """
    try:
        from bs4 import BeautifulSoup
        
        print(f"Fetching page to extract HTML structure...")
        response = requests.get(url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the first observation card
        obs_card = soup.select_one(alert_class)
        
        if not obs_card:
            print(f"Could not find any elements matching '{alert_class}' selector")
            return
        
        # Get the prettified HTML for just this card
        html_sample = obs_card.prettify()
        
        print(f"\n===== HTML Structure Sample =====\n")
        print(html_sample)
        print(f"\n================================\n")
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("<!-- HTML Structure Sample for eBird RBA -->\n")
                f.write(f"<!-- URL: {url} -->\n")
                f.write(f"<!-- Selector: {alert_class} -->\n\n")
                f.write(html_sample)
            print(f"HTML sample saved to {output_file}")
        
    except Exception as e:
        print(f"Error extracting HTML sample: {e}")

def debug_reporter_extraction(url):
    """
    Special debug function to analyze the reporter field structure
    
    Args:
        url: The URL to the eBird alerts page
    """
    try:
        from bs4 import BeautifulSoup
        print("Fetching page to debug reporter extraction...")
        response = requests.get(url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        obs_cards = soup.select('.Observation')
        
        if not obs_cards:
            print("No observation cards found")
            return
        
        # Take the first card for analysis
        card = obs_cards[0]
        
        print("\n==== REPORTER FIELD DEBUG ====")
        
        # Find all user icons
        user_icons = card.select('.Icon--user')
        print(f"Found {len(user_icons)} user icons")
        
        if user_icons:
            icon = user_icons[0]
            parent_cell = icon.find_parent('.GridFlex-cell')
            print(f"Parent cell found: {parent_cell is not None}")
            
            if parent_cell:
                # Print the parent container structure
                flex_container = parent_cell.find_parent('.GridFlex')
                
                if flex_container:
                    print("\nContainer HTML:")
                    print(flex_container.prettify())
                    
                    # Find all cells in this container
                    cells = flex_container.select('.GridFlex-cell')
                    print(f"\nFound {len(cells)} cells in this container")
                    
                    # Look for the name cell which should be adjacent
                    for i, cell in enumerate(cells):
                        print(f"\nCell {i}:")
                        print(cell.prettify())
                        
                        # Check for spans
                        spans = cell.select('span')
                        for j, span in enumerate(spans):
                            print(f"\n  Span {j}: '{span.text.strip()}'")
                            print(f"  Classes: {span.get('class', 'None')}")
                            print(f"  Hidden: {'is-visuallyHidden' in span.get('class', [])}")
        
        print("\n==== END DEBUG ====")
        
    except Exception as e:
        print(f"Error in reporter debug: {e}")

def main():
    parser = argparse.ArgumentParser(description='Debug eBird RBA data fetching')
    parser.add_argument('--html', action='store_true', help='Generate HTML report')
    parser.add_argument('--json', action='store_true', help='Output raw JSON data')
    parser.add_argument('--county', type=int, default=0, 
                      help='Index of county to fetch (default: 0 for first county)')
    parser.add_argument('--save-raw', action='store_true', 
                      help='Save the raw HTML from eBird for debugging')
    parser.add_argument('--extract-sample', action='store_true',
                      help='Extract and display sample HTML structure')
    parser.add_argument('--debug-reporter', action='store_true',
                      help='Debug reporter field extraction')
    args = parser.parse_args()
    
    if args.county < 0 or args.county >= len(COUNTIES):
        print(f"Error: County index {args.county} is out of range. Available counties: 0-{len(COUNTIES)-1}")
        sys.exit(1)
    
    county = COUNTIES[args.county]
    print(f"Fetching data for {county['name']} County, {county['state']}...")
    print(f"URL: {county['url']}")
    
    # Debug reporter extraction if requested
    if args.debug_reporter:
        debug_reporter_extraction(county['url'])
        return
    
    # If requested, save raw HTML or extract sample before parsing
    if args.save_raw:
        raw_filename = f"raw_ebird_{county['name'].lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        save_raw_html(county['url'], raw_filename)
    
    if args.extract_sample:
        sample_filename = f"html_sample_{county['name'].lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        extract_html_sample(county['url'], '.Observation', sample_filename)
    
    # Create a temporary directory for the debug file if needed
    debug_dir = os.path.join(os.path.dirname(__file__), 'logs')
    os.makedirs(debug_dir, exist_ok=True)
    debug_file = os.path.join(debug_dir, 'debug_temp.json')
    
    # Initialize the fetcher with a proper file path
    fetcher = EBirdFetcher(debug_file)
    
    try:
        # Fetch the alerts
        alerts = fetcher.fetch_alerts(county)
        
        if not alerts:
            print("\nNo alerts found. This could mean:")
            print("1. There are no current rare bird alerts for this county")
            print("2. The page structure has changed and the parser needs to be updated")
            print("3. There's an issue with the connection or eBird website")
            sys.exit(0)
            
        print(f"\nFound {len(alerts)} alerts.")
        
        if args.json:
            # Output raw JSON
            print(json.dumps(alerts, indent=2))
        else:
            # Display each alert in a readable format
            for i, alert in enumerate(alerts):
                display_alert(alert, i)
        
        if args.html:
            # Create an HTML report
            filename = f"debug_{county['name'].lower()}_county_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            html_file = save_html_report(alerts, county, filename)
            
            # Try to open the HTML file in the default browser
            try:
                import webbrowser
                webbrowser.open('file://' + os.path.realpath(html_file))
            except:
                pass
    
    except Exception as e:
        print(f"\nError fetching alerts: {e}")
        raise

if __name__ == "__main__":
    main()