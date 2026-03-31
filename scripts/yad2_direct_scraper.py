#!/usr/bin/env python3
"""
Yad2 Direct Scraper - Real Market Data Collection
Collects actual Toyota Auris 2014 listings from Yad2.co.il
"""

import requests
import json
import re
import time
from urllib.parse import urlencode
from datetime import datetime
from typing import List, Dict, Optional
import random

class Yad2DirectScraper:
    def __init__(self):
        self.base_url = "https://www.yad2.co.il"
        self.api_url = "https://www.yad2.co.il/api/pre-load/getFeed"
        self.session = requests.Session()
        
        # Headers to appear more like a real browser
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9,he;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://www.yad2.co.il/vehicles/cars',
            'sec-ch-ua': '"Not A;Brand";v="99", "Chromium";v="91"',
            'sec-ch-ua-mobile': '?0',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
        }
        self.session.headers.update(self.headers)
        
        # Rate limiting
        self.delay_between_requests = random.uniform(2, 4)
    
    def search_toyota_auris_2014(self, max_results: int = 30) -> List[Dict]:
        """Search for Toyota Auris 2014 listings"""
        print("🔍 Searching Yad2 for Toyota Auris 2014...")
        
        # Build search parameters for Toyota Auris 2014
        params = {
            'category': '1',  # Vehicles
            'subCategory': '1',  # Cars
            'manufacturer': 'טויוטה',  # Toyota in Hebrew
            'model': 'אוריס',  # Auris in Hebrew  
            'year': '2014-2014',  # Specific year 2014
            'take': str(max_results),
            'skip': '0'
        }
        
        try:
            # Make the request
            response = self.session.get(self.api_url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract listings from the response
                listings = []
                feed_items = data.get('feed', {}).get('feed_items', [])
                
                for item in feed_items:
                    try:
                        listing_data = self._extract_listing_data(item)
                        if listing_data:
                            listings.append(listing_data)
                    except Exception as e:
                        print(f"Error extracting item: {e}")
                        continue
                
                print(f"✅ Found {len(listings)} Toyota Auris 2014 listings")
                return listings
                
            else:
                print(f"❌ Failed to fetch data: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Error searching Yad2: {e}")
            return []
    
    def _extract_listing_data(self, item: Dict) -> Optional[Dict]:
        """Extract relevant data from a listing item"""
        try:
            # Basic listing info
            listing = {
                'listing_id': item.get('id'),
                'url': f"{self.base_url}{item.get('link_token', '')}",
                'title': item.get('title', ''),
                'price': self._extract_price(item.get('price', '')),
                'currency': 'ILS',
                'year': self._extract_year(item),
                'manufacturer': 'Toyota',
                'model': 'Auris',
                'km': self._extract_kilometers(item),
                'location': item.get('city', ''),
                'area': item.get('area', ''),
                'seller_type': item.get('seller_type', ''),
                'date_updated': item.get('date_added', ''),
                'has_image': len(item.get('images', [])) > 0,
                'image_count': len(item.get('images', [])),
                'description': item.get('description_text', ''),
                'row_4': item.get('row_4', []),  # Additional details
                'contact_name': item.get('contact_name', ''),
                'date_scraped': datetime.now().isoformat()
            }
            
            # Extract additional details from row_4
            if listing['row_4']:
                for detail in listing['row_4']:
                    if 'hand' in detail.lower() or 'יד' in detail:
                        listing['hand'] = detail
                    elif 'ק"מ' in detail or 'km' in detail.lower():
                        if not listing['km']:
                            listing['km'] = self._extract_number(detail)
                    elif 'אוטומט' in detail or 'ידני' in detail:
                        listing['gearbox'] = detail
                    elif 'בנזין' in detail or 'דיזל' in detail or 'גז' in detail:
                        listing['fuel_type'] = detail
            
            # Validate required fields
            if listing['price'] and listing['price'] > 0:
                return listing
            else:
                return None
                
        except Exception as e:
            print(f"Error extracting listing data: {e}")
            return None
    
    def _extract_price(self, price_str: str) -> int:
        """Extract numeric price from price string"""
        if not price_str:
            return 0
        
        # Remove currency symbols and commas
        price_clean = re.sub(r'[^\d]', '', str(price_str))
        
        try:
            return int(price_clean) if price_clean else 0
        except ValueError:
            return 0
    
    def _extract_year(self, item: Dict) -> int:
        """Extract year from item data"""
        # Check various fields for year information
        year_sources = [
            item.get('year', ''),
            item.get('model_year', ''),
            item.get('title', '')
        ]
        
        for source in year_sources:
            if source:
                year_match = re.search(r'20(1[4-9]|2[0-5])', str(source))
                if year_match:
                    return int(year_match.group())
        
        return 2014  # Default to 2014 since that's what we're searching for
    
    def _extract_kilometers(self, item: Dict) -> int:
        """Extract kilometers from item data"""
        # Check various fields for kilometer information
        km_sources = [
            item.get('km', ''),
            item.get('mileage', ''),
            *item.get('row_4', [])
        ]
        
        for source in km_sources:
            km = self._extract_number(str(source))
            if km and km > 1000:  # Reasonable km range
                return km
        
        return 0
    
    def _extract_number(self, text: str) -> int:
        """Extract the first reasonable number from text"""
        if not text:
            return 0
        
        numbers = re.findall(r'\d{1,3}(?:,\d{3})*', text)
        
        for num_str in numbers:
            try:
                num = int(num_str.replace(',', ''))
                if num > 0:
                    return num
            except ValueError:
                continue
        
        return 0
    
    def get_detailed_listing(self, listing_url: str) -> Dict:
        """Get detailed information from individual listing page"""
        try:
            time.sleep(self.delay_between_requests)
            
            response = self.session.get(listing_url)
            
            if response.status_code == 200:
                # This would require HTML parsing to extract detailed info
                # For now, return basic success indicator
                return {'detailed_data_available': True, 'status': 'success'}
            else:
                return {'detailed_data_available': False, 'status': 'failed'}
                
        except Exception as e:
            print(f"Error getting detailed listing: {e}")
            return {'detailed_data_available': False, 'status': 'error', 'error': str(e)}
    
    def analyze_market_data(self, listings: List[Dict]) -> Dict:
        """Analyze the collected market data"""
        if not listings:
            return {'error': 'No listings to analyze'}
        
        prices = [l['price'] for l in listings if l['price'] > 0]
        kms = [l['km'] for l in listings if l['km'] > 0]
        
        analysis = {
            'total_listings': len(listings),
            'price_analysis': {
                'count': len(prices),
                'min': min(prices) if prices else 0,
                'max': max(prices) if prices else 0,
                'average': round(sum(prices) / len(prices)) if prices else 0,
                'median': sorted(prices)[len(prices)//2] if prices else 0,
                'range': max(prices) - min(prices) if prices else 0
            },
            'mileage_analysis': {
                'count': len(kms),
                'min': min(kms) if kms else 0,
                'max': max(kms) if kms else 0,
                'average': round(sum(kms) / len(kms)) if kms else 0,
                'median': sorted(kms)[len(kms)//2] if kms else 0
            },
            'location_distribution': {},
            'seller_type_distribution': {},
            'listings_with_images': sum(1 for l in listings if l['has_image']),
            'average_image_count': round(sum(l['image_count'] for l in listings) / len(listings)),
            'data_collection_timestamp': datetime.now().isoformat()
        }
        
        # Location distribution
        for listing in listings:
            location = listing.get('location', 'Unknown')
            analysis['location_distribution'][location] = analysis['location_distribution'].get(location, 0) + 1
        
        # Seller type distribution  
        for listing in listings:
            seller_type = listing.get('seller_type', 'Unknown')
            analysis['seller_type_distribution'][seller_type] = analysis['seller_type_distribution'].get(seller_type, 0) + 1
        
        return analysis

def main():
    """Test the scraper with Toyota Auris 2014"""
    print("🎩 Heinrich Real Data Collection - Toyota Auris 2014")
    print("="*55)
    
    scraper = Yad2DirectScraper()
    
    # Search for Toyota Auris 2014
    listings = scraper.search_toyota_auris_2014(max_results=20)
    
    if listings:
        print(f"\n✅ Successfully collected {len(listings)} real listings!")
        
        # Analyze the data
        analysis = scraper.analyze_market_data(listings)
        
        print(f"\n📊 REAL MARKET ANALYSIS:")
        print(f"========================")
        print(f"Total Listings: {analysis['total_listings']}")
        
        price_data = analysis['price_analysis']
        print(f"\n💰 Price Analysis (₪):")
        print(f"   Range: {price_data['min']:,} - {price_data['max']:,}")
        print(f"   Average: {price_data['average']:,}")
        print(f"   Median: {price_data['median']:,}")
        
        if analysis['mileage_analysis']['count'] > 0:
            km_data = analysis['mileage_analysis']
            print(f"\n📏 Mileage Analysis (km):")
            print(f"   Range: {km_data['min']:,} - {km_data['max']:,}")
            print(f"   Average: {km_data['average']:,}")
            print(f"   Median: {km_data['median']:,}")
        
        print(f"\n📍 Location Distribution:")
        for location, count in analysis['location_distribution'].items():
            print(f"   {location}: {count} listings")
        
        # Show sample listings
        print(f"\n📋 Sample Real Listings:")
        print(f"========================")
        for i, listing in enumerate(listings[:5], 1):
            price = f"{listing['price']:,} ₪" if listing['price'] else "Price N/A"
            km = f"{listing['km']:,} km" if listing['km'] else "KM N/A"
            location = listing.get('location', 'Location N/A')
            print(f"{i}. {price} | {km} | {location}")
        
        return listings, analysis
    
    else:
        print("❌ No listings found. The scraper may need adjustment.")
        return [], {}

if __name__ == "__main__":
    main()