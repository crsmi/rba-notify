"""
Module to fetch and parse eBird rare bird alerts
"""
import requests
from bs4 import BeautifulSoup
import json
import os
import logging
import re
from datetime import datetime
from typing import List, Dict, Any

# Set up logging
logging.basicConfig(
    filename='logs/ebird_fetcher.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EBirdFetcher:
    def __init__(self, data_storage_file: str):
        """
        Initialize the EBird Rare Bird Alert fetcher
        
        Args:
            data_storage_file: File path to store previously seen alerts
        """
        self.data_storage_file = data_storage_file
        self.previous_alerts = self._load_previous_alerts()
    
    def _load_previous_alerts(self) -> Dict[str, List[str]]:
        """
        Load previously seen alerts from storage file
        
        Returns:
            Dictionary mapping county alert_id to list of observation IDs
        """
        if os.path.exists(self.data_storage_file):
            try:
                with open(self.data_storage_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading previous alerts: {e}")
                return {}
        else:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.data_storage_file), exist_ok=True)
            return {}
    
    def _save_previous_alerts(self):
        """Save the current alerts to the storage file"""
        try:
            with open(self.data_storage_file, 'w') as f:
                json.dump(self.previous_alerts, f)
        except Exception as e:
            logger.error(f"Error saving previous alerts: {e}")
    
    def fetch_alerts(self, county: Dict[str, str]) -> List[Dict[str, Any]]:
        """
        Fetch rare bird alerts for a specific county
        
        Args:
            county: County information including alert URL
            
        Returns:
            List of alert dictionaries with observation details
        """
        alert_id = county['alert_id']
        url = county['url']
        
        try:
            logger.info(f"Fetching alerts for {county['name']} County, {county['state']}")
            response = requests.get(url)
            response.raise_for_status()
            
            # Parse the HTML content
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract observation data
            observations = []
            obs_cards = soup.select('.Observation')
            
            for card in obs_cards:
                try:
                    # Extract the observation ID - this is in the card's id attribute
                    obs_id = card.get('id', '').replace('obs-OBS', '')
                    
                    # Extract the checklist ID directly from the date link href
                    date_link = card.select_one('.Observation-meta a[href*="/checklist/"]')
                    checklist_id = None
                    checklist_url = None
                    
                    if date_link and 'href' in date_link.attrs:
                        checklist_href = date_link['href']
                        # Extract the checklist ID (format: /checklist/S12345678)
                        if '/checklist/' in checklist_href:
                            checklist_id = checklist_href.split('/checklist/')[1]
                            # Create the full URL
                            checklist_url = f"https://ebird.org/checklist/{checklist_id}"
                    
                    if not checklist_url:
                        # Fallback to using obs_id if we couldn't get the checklist ID
                        logger.warning("Could not extract checklist ID from link - using fallback")
                        checklist_url = f"https://ebird.org/checklist/{obs_id}"
                    
                    # Extract species name
                    species_elem = card.select_one('.Observation-species a')
                    if species_elem:
                        species_main = species_elem.select_one('.Heading-main')
                        species_sub = species_elem.select_one('.Heading-sub')
                        
                        main_text = species_main.text.strip() if species_main else ''
                        scientific_name = species_sub.text.strip() if species_sub else ''
                        
                        species = main_text
                    else:
                        species = 'Unknown Species'
                        scientific_name = ''
                    
                    # Extract count - looking specifically for the content after the visually hidden span
                    count_container = card.select_one('.Observation-numberObserved')
                    count = 'Unknown'
                    if count_container:
                        # First, try to find all spans that are not visually hidden
                        non_hidden_spans = [
                            span.text.strip() 
                            for span in count_container.find_all('span') 
                            if 'is-visuallyHidden' not in span.get('class', [])
                        ]
                        
                        # If that didn't work, try getting all text and removing the label
                        if non_hidden_spans:
                            count = ' '.join(non_hidden_spans)
                        else:
                            all_text = count_container.text.strip()
                            # Use regex to extract just the number after any text
                            count_match = re.search(r'Number observed:\s*(.+)', all_text)
                            if count_match:
                                count = count_match.group(1).strip()
                                
                        # Clean up by removing any "Number observed:" text that might remain
                        count = count.replace('Number observed:', '').strip()
                    
                    # Extract date - found in the link with checklist URL
                    date_elem = card.select_one('.Observation-meta a[href*="/checklist/"]')
                    date_str = date_elem.text.strip() if date_elem else 'Unknown Date'
                    
                    # Extract location - found in the a tag with google maps URL
                    loc_elem = card.select_one('.Observation-meta a[href*="google.com/maps"]')
                    location = loc_elem.text.strip() if loc_elem else 'Unknown Location'
                    
                    # Direct approach for observer extraction based on exact HTML pattern
                    observer = 'eBird User'  # Default fallback
                    
                    # 1. First approach - Find the span with text "Observer:" and get its sibling
                    observer_labels = card.find_all('span', class_='is-visuallyHidden')
                    for label in observer_labels:
                        if label.text.strip() == "Observer:":
                            # The next sibling span should contain the observer name
                            next_span = label.find_next_sibling('span')
                            if next_span:
                                observer = next_span.text.strip()
                                break
                    
                    # 2. If that didn't work, look for the Icon--user and navigate to the name
                    if observer == 'eBird User':
                        user_icon = card.select_one('.Icon--user')
                        if user_icon:
                            # Get the parent container with flex structure
                            flex_container = user_icon.find_parent('.GridFlex--flex')
                            if flex_container:
                                # The sizeFill div should contain both the hidden label and the name
                                size_fill_div = flex_container.select_one('.GridFlex-cell.u-sizeFill')
                                if size_fill_div:
                                    # Get the second span which should contain the name
                                    spans = size_fill_div.find_all('span')
                                    if len(spans) >= 2:
                                        observer = spans[1].text.strip()
                    
                    # 3. Last resort - try to get direct HTML and parse with regex
                    if observer == 'eBird User' and user_icon:
                        parent_cell = user_icon.find_parent('.GridFlex-cell')
                        if parent_cell:
                            parent_div = parent_cell.find_parent('div')
                            if parent_div:
                                html_content = str(parent_div)
                                name_match = re.search(r'Observer:</span>\s*<span>\s*(.*?)\s*</span>', html_content)
                                if name_match:
                                    observer = name_match.group(1)
                    
                    # Create observation with field names matching eBird terminology
                    observation = {
                        'id': obs_id,
                        'species': species,
                        'scientificName': scientific_name,
                        'count': count,
                        'date': date_str,
                        'location': location,
                        'observer': observer,
                        'checklistUrl': checklist_url
                    }
                    
                    observations.append(observation)
                    logger.debug(f"Parsed observation: {species}")
                except Exception as e:
                    logger.error(f"Error parsing observation card: {e}")
            
            return observations
            
        except Exception as e:
            logger.error(f"Error fetching alerts for {county['name']} County: {e}")
            return []
    
    def get_new_alerts(self, county: Dict[str, str]) -> List[Dict[str, Any]]:
        """
        Get new alerts that haven't been seen before
        
        Args:
            county: County information
            
        Returns:
            List of new alert dictionaries
        """
        alert_id = county['alert_id']
        all_alerts = self.fetch_alerts(county)
        
        # Initialize this county in previous alerts if not exists
        if alert_id not in self.previous_alerts:
            self.previous_alerts[alert_id] = []
        
        # Filter to only new alerts
        new_alerts = []
        for alert in all_alerts:
            if alert['id'] not in self.previous_alerts[alert_id]:
                new_alerts.append(alert)
                self.previous_alerts[alert_id].append(alert['id'])
        
        # Save updated previous alerts if there are new ones
        if new_alerts:
            self._save_previous_alerts()
            
        return new_alerts