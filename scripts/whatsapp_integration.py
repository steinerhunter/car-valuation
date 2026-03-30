#!/usr/bin/env python3
"""
WhatsApp Integration for Car Valuation - OME-94
Automatically detect and analyze Yad2 links in WhatsApp messages
"""

import re
from typing import Optional, Dict, List
from yad2_link_analyzer import analyze_yad2_link, Yad2LinkAnalyzer

class WhatsAppCarAnalyzer:
    """Detect car-related content in WhatsApp messages and provide analysis"""
    
    def __init__(self):
        self.yad2_analyzer = Yad2LinkAnalyzer()
        
    def detect_car_content(self, message: str) -> Dict:
        """
        Analyze WhatsApp message for car-related content
        
        Returns analysis type and relevant data
        """
        message = message.strip()
        
        # Priority 1: Yad2 Links
        yad2_urls = self._extract_yad2_links(message)
        if yad2_urls:
            return {
                'type': 'yad2_link',
                'urls': yad2_urls,
                'action': 'analyze_links'
            }
        
        # Priority 2: Car Valuation Queries 
        if self._is_car_valuation_query(message):
            car_info = self._parse_car_info(message)
            return {
                'type': 'car_valuation',
                'car_info': car_info,
                'action': 'market_analysis',
                'hebrew_response': self._is_hebrew_message(message)
            }
        
        # Priority 3: Car-related questions
        if self._is_car_related(message):
            return {
                'type': 'car_question',
                'message': message,
                'action': 'general_help',
                'hebrew_response': self._is_hebrew_message(message)
            }
        
        return {
            'type': 'none',
            'action': 'no_car_content'
        }
    
    def _extract_yad2_links(self, message: str) -> List[str]:
        """Extract Yad2 URLs from message"""
        url_patterns = [
            r'https?://(?:www\.)?yad2\.co\.il/[^\s]+',
            r'https?://(?:m\.)?yad2\.co\.il/[^\s]+',
            r'yad2\.co\.il/[^\s]+',
            r'www\.yad2\.co\.il/[^\s]+'
        ]
        
        urls = []
        for pattern in url_patterns:
            matches = re.findall(pattern, message, re.IGNORECASE)
            for match in matches:
                # Ensure it's a car-related URL
                if self.yad2_analyzer.is_yad2_car_link(match):
                    # Clean and normalize URL
                    if not match.startswith('http'):
                        match = 'https://' + match
                    urls.append(match)
        
        return list(set(urls))  # Remove duplicates
    
    def _is_car_valuation_query(self, message: str) -> bool:
        """Check if message is asking for car valuation"""
        hebrew_patterns = [
            r'כמה שווה',
            r'מה המחיר',
            r'תעריך',
            r'בכמה נמכר',
            r'מה דעתך',
            r'שווה לקנות',
            r'מחיר הוגן',
            r'עסקה טובה'
        ]
        
        english_patterns = [
            r'what.*worth',
            r'how much.*cost',
            r'value.*car',
            r'price.*fair',
            r'good deal',
            r'should i buy',
            r'worth buying'
        ]
        
        all_patterns = hebrew_patterns + english_patterns
        
        return any(re.search(pattern, message, re.IGNORECASE) for pattern in all_patterns)
    
    def _is_car_related(self, message: str) -> bool:
        """Check if message is car-related in general"""
        car_keywords = [
            # Hebrew
            'רכב', 'מכונית', 'אוטו', 'קניה', 'מכירה', 'ביטוח',
            'טויוטה', 'הונדה', 'יונדאי', 'ניסאן', 'מאזדה',
            'קילומטר', 'ק״מ', 'מנוע', 'גיר', 'בדיקה שנתית',
            
            # English  
            'car', 'vehicle', 'auto', 'buying', 'selling', 'insurance',
            'toyota', 'honda', 'hyundai', 'nissan', 'mazda', 
            'bmw', 'mercedes', 'volkswagen', 'audi',
            'kilometers', 'km', 'engine', 'transmission', 'inspection'
        ]
        
        return any(keyword.lower() in message.lower() for keyword in car_keywords)
    
    def _is_hebrew_message(self, message: str) -> bool:
        """Detect if message is primarily in Hebrew"""
        hebrew_chars = len(re.findall(r'[א-ת]', message))
        total_chars = len(re.findall(r'[a-zA-Zא-ת]', message))
        
        if total_chars == 0:
            return False
        
        return (hebrew_chars / total_chars) > 0.3
    
    def _parse_car_info(self, message: str) -> Dict:
        """Extract car information from message"""
        info = {}
        
        # Extract year
        year_match = re.search(r'\b(19[9]\d|20[0-2]\d)\b', message)
        if year_match:
            info['year'] = int(year_match.group(1))
        
        # Extract manufacturer and model
        manufacturers = [
            ('טויוטה', 'Toyota'), ('הונדה', 'Honda'), ('יונדאי', 'Hyundai'),
            ('ניסאן', 'Nissan'), ('מאזדה', 'Mazda'), ('ב.מ.וו', 'BMW'),
            ('Toyota', 'Toyota'), ('Honda', 'Honda'), ('Hyundai', 'Hyundai'),
            ('Nissan', 'Nissan'), ('Mazda', 'Mazda'), ('BMW', 'BMW')
        ]
        
        for hebrew, english in manufacturers:
            if hebrew.lower() in message.lower() or english.lower() in message.lower():
                info['manufacturer'] = english
                break
        
        # Extract mileage
        km_patterns = [
            r'(\d{1,3}(?:,\d{3})+)\s*ק[״"׳]?מ',
            r'(\d{1,3}(?:,\d{3})+)\s*km',
            r'(\d{1,6})\s*קילומטר',
            r'(\d+)\s*אלף\s*ק[״"׳]?מ'
        ]
        
        for pattern in km_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                km_str = match.group(1).replace(',', '')
                try:
                    km = int(km_str)
                    if 'אלף' in match.group(0):
                        km *= 1000
                    info['km'] = km
                    break
                except ValueError:
                    continue
        
        # Extract price if mentioned
        price_patterns = [
            r'(\d{1,3}(?:,\d{3})+)\s*₪',
            r'(\d{2,6})\s*שקל',
            r'(\d+)\s*אלף\s*₪'
        ]
        
        for pattern in price_patterns:
            match = re.search(pattern, message)
            if match:
                price_str = match.group(1).replace(',', '')
                try:
                    price = int(price_str)
                    if 'אלף' in match.group(0):
                        price *= 1000
                    info['price'] = price
                    break
                except ValueError:
                    continue
        
        return info
    
    def process_whatsapp_message(self, message: str) -> Optional[str]:
        """
        Main function to process WhatsApp message and return appropriate response
        """
        detection = self.detect_car_content(message)
        
        if detection['type'] == 'yad2_link':
            return self._handle_yad2_links(detection['urls'], message)
        
        elif detection['type'] == 'car_valuation':
            return self._handle_car_valuation(detection['car_info'], detection['hebrew_response'])
        
        elif detection['type'] == 'car_question':
            return self._handle_general_car_question(detection['message'], detection['hebrew_response'])
        
        return None  # No car-related content
    
    def _handle_yad2_links(self, urls: List[str], original_message: str) -> str:
        """Handle Yad2 link analysis"""
        hebrew_response = self._is_hebrew_message(original_message)
        
        if len(urls) == 1:
            # Single link analysis
            result = analyze_yad2_link(urls[0], hebrew_response=hebrew_response)
            
            if result['status'] == 'success':
                listing = result['listing_data']
                
                if hebrew_response:
                    response = f"🚗 **מצאתי: {listing['year']} {listing['manufacturer']} {listing['model']}**\n\n"
                    response += f"💰 מחיר: {listing['price']:,} ₪\n"
                    if listing['km']:
                        response += f"🛣️ קילומטראז': {listing['km']:,} ק״מ\n"
                    if listing['city']:
                        response += f"📍 מיקום: {listing['city']}\n"
                    
                    response += f"\n🔍 **מנתח את השוק עכשיו...**"
                    # Here we would trigger market analysis
                    response += f"\n\n💡 זה הקישור שבדקתי: {urls[0]}"
                    
                else:
                    response = f"🚗 **Found: {listing['year']} {listing['manufacturer']} {listing['model']}**\n\n"
                    response += f"💰 Price: {listing['price']:,} ILS\n"
                    if listing['km']:
                        response += f"🛣️ Mileage: {listing['km']:,} km\n"
                    if listing['city']:
                        response += f"📍 Location: {listing['city']}\n"
                    
                    response += f"\n🔍 **Analyzing market now...**"
                    response += f"\n\nThis was the link I analyzed: {urls[0]}"
                
                return response
            
            else:
                if hebrew_response:
                    return f"❌ מצטער, לא הצלחתי לנתח את הקישור: {result.get('message', 'בעיה לא ידועה')}"
                else:
                    return f"❌ Sorry, couldn't analyze the link: {result.get('message', 'Unknown error')}"
        
        else:
            # Multiple links
            if hebrew_response:
                response = f"🔍 מצאתי {len(urls)} קישורי יד2! בוא אנתח אותם:\n\n"
            else:
                response = f"🔍 Found {len(urls)} Yad2 links! Let me analyze them:\n\n"
            
            for i, url in enumerate(urls, 1):
                result = analyze_yad2_link(url, hebrew_response=hebrew_response)
                if result['status'] == 'success':
                    listing = result['listing_data']
                    response += f"{i}. {listing['year']} {listing['manufacturer']} {listing['model']} - {listing['price']:,} {'₪' if hebrew_response else 'ILS'}\n"
                else:
                    response += f"{i}. ❌ לא הצלח לנתח\n" if hebrew_response else f"{i}. ❌ Failed to analyze\n"
            
            return response
    
    def _handle_car_valuation(self, car_info: Dict, hebrew_response: bool) -> str:
        """Handle car valuation query"""
        if hebrew_response:
            response = "🔍 **מחפש בשוק עבור הרכב שלך...**\n\n"
        else:
            response = "🔍 **Searching market for your car...**\n\n"
        
        # Show what we understood from the message
        if car_info.get('manufacturer'):
            response += f"🚗 יצרן: {car_info['manufacturer']}\n" if hebrew_response else f"🚗 Manufacturer: {car_info['manufacturer']}\n"
        if car_info.get('year'):
            response += f"📅 שנה: {car_info['year']}\n" if hebrew_response else f"📅 Year: {car_info['year']}\n"
        if car_info.get('km'):
            response += f"🛣️ קילומטראז': {car_info['km']:,} ק״מ\n" if hebrew_response else f"🛣️ Mileage: {car_info['km']:,} km\n"
        if car_info.get('price'):
            response += f"💰 מחיר שאתה בודק: {car_info['price']:,} ₪\n" if hebrew_response else f"💰 Price you're checking: {car_info['price']:,} ILS\n"
        
        response += "\n⏳ אני מריץ ניתוח שוק מלא..." if hebrew_response else "\n⏳ Running full market analysis..."
        
        # TODO: Here we would trigger the actual market analysis
        # For now, return this preparation message
        
        return response
    
    def _handle_general_car_question(self, message: str, hebrew_response: bool) -> str:
        """Handle general car-related questions"""
        if hebrew_response:
            return ("🚗 **שאלת על רכבים!**\n\n"
                   "אני יכול לעזור לך עם:\n"
                   "• הערכות שווי רכב\n"
                   "• ניתוח קישורי יד2\n" 
                   "• השוואות מחירים\n"
                   "• עצות קנייה ומכירה\n\n"
                   "פשוט שלח לי קישור יד2 או תגיד לי איזה רכב אתה בודק!")
        else:
            return ("🚗 **Car question detected!**\n\n"
                   "I can help you with:\n"
                   "• Car valuations\n"
                   "• Yad2 link analysis\n"
                   "• Price comparisons\n" 
                   "• Buying/selling advice\n\n"
                   "Just send me a Yad2 link or tell me what car you're checking!")

def process_whatsapp_car_message(message: str) -> Optional[str]:
    """
    Main entry point for WhatsApp car analysis
    
    Args:
        message: WhatsApp message content
        
    Returns:
        Response string if car-related, None otherwise
    """
    analyzer = WhatsAppCarAnalyzer()
    return analyzer.process_whatsapp_message(message)

if __name__ == "__main__":
    # Test the WhatsApp integration
    test_messages = [
        "מה דעתך על זה? https://yad2.co.il/ad/toyota-corolla-2019-85000",
        "Heinrich, check this out: https://yad2.co.il/vehicles/item/12345",
        "כמה שווה טויוטה קורולה 2019 עם 60 אלף קמ?",
        "Is 85,000 ILS good for a 2018 Honda Civic?",
        "אני מחפש רכב עד 90 אלף",
        "Hello how are you today?"  # Non-car message
    ]
    
    print("🧪 Testing WhatsApp Car Integration:")
    print("="*50)
    
    analyzer = WhatsAppCarAnalyzer()
    
    for message in test_messages:
        print(f"\n📱 Message: {message}")
        print("-" * 40)
        
        detection = analyzer.detect_car_content(message)
        print(f"🔍 Detection: {detection['type']}")
        
        response = analyzer.process_whatsapp_message(message)
        if response:
            print(f"✅ Response:\n{response}")
        else:
            print("❌ No car-related response")
    
    print("\n✅ WhatsApp integration ready!")