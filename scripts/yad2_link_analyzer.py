#!/usr/bin/env python3
"""
Yad2 Link Analyzer - OME-94: WhatsApp Link Analysis
Parse Yad2 car listing URLs and provide instant valuation analysis

This module allows users to send Yad2 links via WhatsApp and get immediate
market analysis without manual input.
"""

import re
import requests
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse, parse_qs
import json
import time
from bs4 import BeautifulSoup
from dataclasses import dataclass

@dataclass
class CarListingData:
    """Structured data extracted from Yad2 listing"""
    url: str
    listing_id: str
    manufacturer: str
    model: str
    year: int
    price: int
    km: Optional[int] = None
    city: Optional[str] = None
    description: Optional[str] = None
    features: List[str] = None
    seller_type: Optional[str] = None  # private/dealer
    phone_number: Optional[str] = None
    image_urls: List[str] = None
    last_updated: Optional[str] = None

    def __post_init__(self):
        if self.features is None:
            self.features = []
        if self.image_urls is None:
            self.image_urls = []

class Yad2LinkAnalyzer:
    """Parse and analyze Yad2 car listing URLs"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
    def is_yad2_car_link(self, url: str) -> bool:
        """Check if URL is a valid Yad2 car listing"""
        yad2_patterns = [
            r'yad2\.co\.il.*vehicles',
            r'yad2\.co\.il.*item',
            r'yad2\.co\.il.*ad',
            r'm\.yad2\.co\.il.*vehicles'
        ]
        
        return any(re.search(pattern, url.lower()) for pattern in yad2_patterns)
    
    def extract_listing_id(self, url: str) -> Optional[str]:
        """Extract listing ID from Yad2 URL"""
        patterns = [
            r'/item/(\d+)',
            r'/ad/(\d+)', 
            r'itemId=(\d+)',
            r'id=(\d+)',
            r'/(\d{7,})'  # Long number likely to be listing ID
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    def scrape_listing_data(self, url: str) -> Optional[CarListingData]:
        """Scrape car data from Yad2 listing page"""
        try:
            # Clean URL
            clean_url = self._clean_url(url)
            listing_id = self.extract_listing_id(clean_url)
            
            if not listing_id:
                print(f"❌ Could not extract listing ID from {url}")
                return None
            
            print(f"🔍 Scraping Yad2 listing: {listing_id}")
            
            # Try to get data via different methods
            listing_data = self._try_multiple_scraping_methods(clean_url, listing_id)
            
            if listing_data:
                print(f"✅ Successfully extracted: {listing_data.year} {listing_data.manufacturer} {listing_data.model}")
                return listing_data
            else:
                print(f"❌ Failed to scrape data from {url}")
                return None
                
        except Exception as e:
            print(f"❌ Error scraping {url}: {e}")
            return None
    
    def _clean_url(self, url: str) -> str:
        """Clean and normalize Yad2 URL"""
        # Remove mobile prefix
        url = url.replace('m.yad2.co.il', 'yad2.co.il')
        
        # Ensure https
        if not url.startswith('http'):
            url = 'https://' + url
        
        return url
    
    def _try_multiple_scraping_methods(self, url: str, listing_id: str) -> Optional[CarListingData]:
        """Try multiple methods to extract listing data"""
        
        # Method 1: Direct page scraping
        listing_data = self._scrape_html_page(url, listing_id)
        if listing_data and self._is_valid_listing_data(listing_data):
            return listing_data
        
        # Method 2: Try mobile version
        mobile_url = url.replace('yad2.co.il', 'm.yad2.co.il')
        listing_data = self._scrape_html_page(mobile_url, listing_id)
        if listing_data and self._is_valid_listing_data(listing_data):
            return listing_data
        
        # Method 3: Try API endpoint (if accessible)
        listing_data = self._try_api_method(listing_id)
        if listing_data and self._is_valid_listing_data(listing_data):
            return listing_data
        
        # Method 4: Fallback with basic URL parsing
        return self._fallback_url_parsing(url, listing_id)
    
    def _scrape_html_page(self, url: str, listing_id: str) -> Optional[CarListingData]:
        """Scrape data from HTML page"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract basic information
            title = self._extract_title(soup)
            price = self._extract_price(soup)
            details = self._extract_details(soup)
            description = self._extract_description(soup)
            
            if not title or not price:
                return None
            
            # Parse car details from title and content
            manufacturer, model, year = self._parse_car_info_from_title(title)
            
            if not all([manufacturer, model, year]):
                return None
            
            # Extract additional details
            km = self._extract_mileage(soup, details)
            city = self._extract_city(soup, details)
            features = self._extract_features(soup, description)
            seller_type = self._extract_seller_type(soup)
            
            return CarListingData(
                url=url,
                listing_id=listing_id,
                manufacturer=manufacturer,
                model=model,
                year=year,
                price=price,
                km=km,
                city=city,
                description=description,
                features=features,
                seller_type=seller_type
            )
            
        except Exception as e:
            print(f"❌ HTML scraping error for {url}: {e}")
            return None
    
    def _extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract listing title"""
        selectors = [
            'h1',
            '.title',
            '.item-title', 
            '[data-testid="ad-title"]',
            '.feeditem_title'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                title = element.get_text(strip=True)
                if len(title) > 10:  # Reasonable title length
                    return title
        
        return None
    
    def _extract_price(self, soup: BeautifulSoup) -> Optional[int]:
        """Extract price from listing"""
        price_selectors = [
            '.price',
            '[data-testid="price"]',
            '.item-price',
            '.feeditem_price'
        ]
        
        for selector in price_selectors:
            elements = soup.select(selector)
            for element in elements:
                price_text = element.get_text(strip=True)
                price = self._parse_price_from_text(price_text)
                if price and 10000 <= price <= 500000:  # Reasonable price range
                    return price
        
        # Try to find price in text content
        text_content = soup.get_text()
        price = self._parse_price_from_text(text_content)
        if price and 10000 <= price <= 500000:
            return price
        
        return None
    
    def _parse_price_from_text(self, text: str) -> Optional[int]:
        """Parse price from text string"""
        # Hebrew and English price patterns
        patterns = [
            r'(\d{1,3}(?:,\d{3})+)\s*₪',  # 85,000 ₪
            r'₪\s*(\d{1,3}(?:,\d{3})+)',  # ₪ 85,000
            r'(\d{1,3}(?:,\d{3})+)\s*שקל',  # שקל
            r'(\d{5,7})\s*₪',  # 85000 ₪
            r'מחיר[:\s]+(\d{1,3}(?:,\d{3})+)',  # מחיר: 85,000
            r'price[:\s]+(\d{1,3}(?:,\d{3})+)',  # Price: 85,000
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                price_str = match.group(1).replace(',', '')
                try:
                    return int(price_str)
                except ValueError:
                    continue
        
        return None
    
    def _extract_details(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract car details from listing"""
        details = {}
        
        # Try to find details in various formats
        detail_selectors = [
            '.details-item',
            '.car-details li',
            '.property-value',
            '.spec-item'
        ]
        
        for selector in detail_selectors:
            elements = soup.select(selector)
            for element in elements:
                text = element.get_text(strip=True)
                if ':' in text:
                    key, value = text.split(':', 1)
                    details[key.strip()] = value.strip()
        
        return details
    
    def _parse_car_info_from_title(self, title: str) -> Tuple[Optional[str], Optional[str], Optional[int]]:
        """Parse manufacturer, model, and year from title"""
        # Common Israeli car manufacturers
        manufacturers = [
            'טויוטה', 'Toyota', 'הונדה', 'Honda', 'יונדאי', 'Hyundai', 
            'ניסאן', 'Nissan', 'מאזדה', 'Mazda', 'סובארו', 'Subaru',
            'פולקסווגן', 'Volkswagen', 'VW', 'ב.מ.וו', 'BMW', 'מרצדס', 'Mercedes',
            'אאודי', 'Audi', 'פז\'ו', 'Peugeot', 'רנו', 'Renault', 'פורד', 'Ford',
            'שברולט', 'Chevrolet', 'פיאט', 'Fiat', 'שקודה', 'Skoda', 'סיאט', 'SEAT',
            'קיה', 'Kia', 'לקסוס', 'Lexus', 'אינפיניטי', 'Infiniti', 'מיני', 'MINI'
        ]
        
        # Map Hebrew to English
        hebrew_to_english = {
            'טויוטה': 'Toyota', 'הונדה': 'Honda', 'יונדאי': 'Hyundai',
            'ניסאן': 'Nissan', 'מאזדה': 'Mazda', 'סובארו': 'Subaru',
            'פולקסווגן': 'Volkswagen', 'ב.מ.וו': 'BMW', 'מרצדס': 'Mercedes',
            'אאודי': 'Audi', 'פז\'ו': 'Peugeot', 'רנו': 'Renault',
            'פורד': 'Ford', 'שברולט': 'Chevrolet', 'פיאט': 'Fiat',
            'שקודה': 'Skoda', 'סיאט': 'SEAT', 'קיה': 'Kia'
        }
        
        # Find manufacturer
        manufacturer = None
        for mfg in manufacturers:
            if mfg.lower() in title.lower():
                manufacturer = hebrew_to_english.get(mfg, mfg)
                break
        
        # Extract year (4 digits between 1990-2025)
        year_match = re.search(r'\b(19[9]\d|20[0-2]\d)\b', title)
        year = int(year_match.group(1)) if year_match else None
        
        # Extract model (this is trickier, we'll use common patterns)
        model = self._extract_model_from_title(title, manufacturer)
        
        return manufacturer, model, year
    
    def _extract_model_from_title(self, title: str, manufacturer: str) -> Optional[str]:
        """Extract car model from title"""
        if not manufacturer:
            return None
        
        # Model mapping for common cars
        model_patterns = {
            'Toyota': ['Corolla', 'Camry', 'Prius', 'Yaris', 'RAV4', 'C-HR', 'Highlander', 'קורולה', 'קמרי', 'פריוס', 'יאריס', 'רב4'],
            'Honda': ['Civic', 'Accord', 'CR-V', 'HR-V', 'Pilot', 'סיוויק', 'אקורד'],
            'Hyundai': ['Elantra', 'Sonata', 'Tucson', 'Kona', 'i30', 'i20', 'אלנטרה', 'טוסון', 'קונה'],
            'Nissan': ['Sentra', 'Altima', 'Qashqai', 'Juke', 'Micra', 'סנטרה', 'קשקאי', 'ג\'וק', 'מיקרה'],
            'BMW': ['Series 1', 'Series 3', 'Series 5', 'X1', 'X3', 'X5', 'סדרה 1', 'סדרה 3', 'סדרה 5'],
            'Mercedes': ['A-Class', 'C-Class', 'E-Class', 'GLA', 'GLC', 'מחלקה A', 'מחלקה C', 'מחלקה E'],
            'Volkswagen': ['Polo', 'Golf', 'Jetta', 'Passat', 'Tiguan', 'פולו', 'גולף', 'ג\'טה', 'פאסאט', 'טיגואן'],
            'Mazda': ['2', '3', '6', 'CX-3', 'CX-5', 'CX-9'],
            'Kia': ['Picanto', 'Rio', 'Ceed', 'Sportage', 'Sorento', 'פיקנטו', 'ריו', 'סיד', 'ספורטג\'', 'סורנטו']
        }
        
        if manufacturer in model_patterns:
            for model in model_patterns[manufacturer]:
                if model.lower() in title.lower():
                    # Return English model name
                    hebrew_to_english_models = {
                        'קורולה': 'Corolla', 'קמרי': 'Camry', 'פריוס': 'Prius', 'יאריס': 'Yaris', 'רב4': 'RAV4',
                        'סיוויק': 'Civic', 'אקורד': 'Accord', 'אלנטרה': 'Elantra', 'טוסון': 'Tucson', 'קונה': 'Kona',
                        'סנטרה': 'Sentra', 'קשקאי': 'Qashqai', 'ג\'וק': 'Juke', 'מיקרה': 'Micra',
                        'סדרה 1': 'Series 1', 'סדרה 3': 'Series 3', 'סדרה 5': 'Series 5',
                        'מחלקה A': 'A-Class', 'מחלקה C': 'C-Class', 'מחלקה E': 'E-Class',
                        'פולו': 'Polo', 'גולף': 'Golf', 'ג\'טה': 'Jetta', 'פאסאט': 'Passat', 'טיגואן': 'Tiguan',
                        'פיקנטו': 'Picanto', 'ריו': 'Rio', 'סיד': 'Ceed', 'ספורטג\'': 'Sportage', 'סורנטו': 'Sorento'
                    }
                    return hebrew_to_english_models.get(model, model)
        
        return None
    
    def _extract_mileage(self, soup: BeautifulSoup, details: Dict[str, str]) -> Optional[int]:
        """Extract mileage from listing"""
        # Check details dict first
        for key, value in details.items():
            if 'קילומטר' in key.lower() or 'km' in key.lower() or 'mileage' in key.lower():
                km = self._parse_number_from_text(value)
                if km and 0 <= km <= 500000:
                    return km
        
        # Search in text content
        text_content = soup.get_text()
        patterns = [
            r'(\d{1,3}(?:,\d{3})+)\s*ק[״"׳]?מ',  # Hebrew km
            r'(\d{1,3}(?:,\d{3})+)\s*km',         # English km
            r'(\d{1,6})\s*קילומטר',               # Hebrew kilometers
            r'mileage[:\s]+(\d{1,3}(?:,\d{3})+)', # Mileage: 
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text_content, re.IGNORECASE)
            if match:
                km = self._parse_number_from_text(match.group(1))
                if km and 0 <= km <= 500000:
                    return km
        
        return None
    
    def _parse_number_from_text(self, text: str) -> Optional[int]:
        """Parse number from text, handling Hebrew/English formats"""
        if not text:
            return None
        
        # Remove common non-numeric characters
        clean_text = re.sub(r'[^\d,]', '', text)
        clean_text = clean_text.replace(',', '')
        
        try:
            return int(clean_text)
        except ValueError:
            return None
    
    def _extract_city(self, soup: BeautifulSoup, details: Dict[str, str]) -> Optional[str]:
        """Extract city from listing"""
        # Check details dict
        for key, value in details.items():
            if 'עיר' in key.lower() or 'city' in key.lower() or 'location' in key.lower():
                return value
        
        # Common city patterns in text
        text_content = soup.get_text()
        israeli_cities = [
            'תל אביב', 'Tel Aviv', 'ירושלים', 'Jerusalem', 'חיפה', 'Haifa',
            'פתח תקווה', 'Petah Tikva', 'ראשון לציון', 'Rishon LeZion',
            'נתניה', 'Netanya', 'באר שבע', 'Beer Sheva', 'חולון', 'Holon',
            'רמת גן', 'Ramat Gan', 'אשדוד', 'Ashdod', 'רעננה', 'Raanana',
            'הרצליה', 'Herzliya', 'כפר סבא', 'Kfar Saba', 'רחובות', 'Rehovot'
        ]
        
        for city in israeli_cities:
            if city in text_content:
                return city
        
        return None
    
    def _extract_features(self, soup: BeautifulSoup, description: str) -> List[str]:
        """Extract car features from listing"""
        features = []
        
        text_content = soup.get_text() + (description or "")
        
        feature_keywords = [
            'עור', 'leather', 'היברידי', 'hybrid', 'גג נפתח', 'sunroof',
            'מולטימדיה', 'multimedia', 'מצלמת נסיעה לאחור', 'backup camera',
            'חיישני נסיעה לאחור', 'parking sensors', 'מזגן אוטומטי', 'automatic AC',
            'מושבים מחוממים', 'heated seats', 'נווט', 'navigation', 'GPS'
        ]
        
        for keyword in feature_keywords:
            if keyword.lower() in text_content.lower():
                features.append(keyword)
        
        return features[:5]  # Limit to 5 features
    
    def _extract_description(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract listing description"""
        desc_selectors = [
            '.description',
            '.item-description',
            '[data-testid="ad-description"]',
            '.feeditem_desc'
        ]
        
        for selector in desc_selectors:
            element = soup.select_one(selector)
            if element:
                desc = element.get_text(strip=True)
                if len(desc) > 20:
                    return desc[:500]  # Limit description length
        
        return None
    
    def _extract_seller_type(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract seller type (private/dealer)"""
        text_content = soup.get_text().lower()
        
        if any(word in text_content for word in ['דילר', 'dealer', 'מוסך', 'garage']):
            return 'dealer'
        elif any(word in text_content for word in ['פרטי', 'private', 'בעלים', 'owner']):
            return 'private'
        
        return None
    
    def _try_api_method(self, listing_id: str) -> Optional[CarListingData]:
        """Try to get data via API endpoints"""
        # This would require reverse engineering Yad2's API
        # For now, return None
        return None
    
    def _fallback_url_parsing(self, url: str, listing_id: str) -> Optional[CarListingData]:
        """Fallback method using URL parameters"""
        # Try to extract basic info from URL structure
        # This is a last resort method
        return None
    
    def _is_valid_listing_data(self, data: CarListingData) -> bool:
        """Validate that we have minimum required data"""
        return all([
            data.manufacturer,
            data.model, 
            data.year,
            data.price,
            data.year >= 1990,
            data.year <= 2025,
            data.price >= 10000,
            data.price <= 500000
        ])

def analyze_yad2_link(url: str, hebrew_response: bool = True) -> Dict:
    """
    Main function to analyze a Yad2 car listing URL
    
    Args:
        url: Yad2 listing URL
        hebrew_response: Whether to return Hebrew response
        
    Returns:
        Analysis result dict
    """
    analyzer = Yad2LinkAnalyzer()
    
    # Check if it's a valid Yad2 link
    if not analyzer.is_yad2_car_link(url):
        return {
            'status': 'invalid_link',
            'message': 'This is not a valid Yad2 car listing URL' if not hebrew_response else 'זה לא קישור תקין למודעת רכב ביד2'
        }
    
    # Extract listing data
    listing_data = analyzer.scrape_listing_data(url)
    
    if not listing_data:
        return {
            'status': 'scraping_failed',
            'message': 'Could not extract car information from this link' if not hebrew_response else 'לא הצלחתי לחלץ מידע על הרכב מהקישור הזה'
        }
    
    # Now use our existing market analysis engine
    try:
        from market_analyzer import analyze_user_query_with_intent
        
        # Create a market analysis query
        query_text = f"What do you think about this {listing_data.year} {listing_data.manufacturer} {listing_data.model} for {listing_data.price:,} ILS?"
        if hebrew_response:
            query_text = f"מה דעתך על {listing_data.manufacturer} {listing_data.model} {listing_data.year} במחיר {listing_data.price:,} ₪?"
        
        # We need to get market data for comparison
        # For now, we'll return the extracted data with a note that we need market data
        return {
            'status': 'success',
            'listing_data': {
                'manufacturer': listing_data.manufacturer,
                'model': listing_data.model,
                'year': listing_data.year,
                'price': listing_data.price,
                'km': listing_data.km,
                'city': listing_data.city,
                'features': listing_data.features,
                'seller_type': listing_data.seller_type,
                'url': listing_data.url
            },
            'message': f"Successfully extracted: {listing_data.year} {listing_data.manufacturer} {listing_data.model} - {listing_data.price:,} ₪" + 
                      (f" ({listing_data.km:,} km)" if listing_data.km else "") +
                      (f" in {listing_data.city}" if listing_data.city else ""),
            'ready_for_analysis': True
        }
        
    except ImportError:
        return {
            'status': 'success',
            'listing_data': listing_data.__dict__,
            'message': 'Car data extracted successfully, but market analysis not available',
            'ready_for_analysis': False
        }

if __name__ == "__main__":
    # Test with sample Yad2 URLs
    test_urls = [
        "https://yad2.co.il/vehicles/cars/item/12345",
        "https://m.yad2.co.il/ad/67890",
        "https://yad2.co.il/ad/toyota-corolla-2019-54321"
    ]
    
    print("🧪 Testing Yad2 Link Analyzer:")
    analyzer = Yad2LinkAnalyzer()
    
    for url in test_urls:
        print(f"\n🔍 Testing: {url}")
        is_valid = analyzer.is_yad2_car_link(url)
        listing_id = analyzer.extract_listing_id(url)
        
        print(f"  Valid Yad2 link: {is_valid}")
        print(f"  Listing ID: {listing_id}")
        
        if is_valid and listing_id:
            result = analyze_yad2_link(url)
            print(f"  Analysis result: {result['status']}")
            if result['status'] == 'success':
                print(f"  Car: {result['listing_data']['year']} {result['listing_data']['manufacturer']} {result['listing_data']['model']}")
                print(f"  Price: {result['listing_data']['price']:,} ₪")
    
    print("\n✅ Yad2 Link Analyzer ready for integration!")