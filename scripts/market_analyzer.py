#!/usr/bin/env python3
"""
Real-Time Car Market Analyzer
Analyze scraped vehicle data to provide user insights
ENHANCED with OME-84: Smart Yad2 Listing Analysis
"""

from typing import List, Dict, Optional, Tuple
import statistics
import re
from datetime import datetime
from advanced_price_analysis import enhance_market_analysis
from buyer_seller_intelligence import analyze_buyer_seller_intent

class MarketAnalyzer:
    """Analyze real-time vehicle data for user insights"""
    
    def __init__(self):
        self.min_valid_price = 15000  # ILS
        self.max_valid_price = 500000  # ILS
    
    def analyze_vehicle_listings(self, vehicles: List[Dict], user_query: Dict) -> Dict:
        """
        Analyze scraped vehicles for a user query
        
        Args:
            vehicles: List of vehicle data from Yad2/scraping
            user_query: Dict with 'year', 'manufacturer', 'model', 'km' (optional)
        
        Returns:
            Analysis with price ranges, insights, recommendations
        """
        if not vehicles:
            return {
                'status': 'no_data',
                'message': f"No current listings found for {user_query.get('year')} {user_query.get('manufacturer')} {user_query.get('model')}",
                'suggestion': "Try searching for similar years or models"
            }
        
        # Clean and validate data
        clean_vehicles = self._clean_vehicle_data(vehicles)
        
        if not clean_vehicles:
            return {
                'status': 'invalid_data',
                'message': "Found listings but they appear to have invalid pricing data",
                'raw_count': len(vehicles)
            }
        
        # Calculate market statistics
        prices = [v['price'] for v in clean_vehicles]
        
        # ENHANCED: Add advanced price analysis (OME-84)
        advanced_analysis = enhance_market_analysis(clean_vehicles)
        
        analysis = {
            'status': 'success',
            'query': user_query,
            'market_data': {
                'listings_found': len(clean_vehicles),
                'price_range': {
                    'min': min(prices),
                    'max': max(prices),
                    'average': int(statistics.mean(prices)),
                    'median': int(statistics.median(prices))
                },
                'sample_listings': self._get_sample_listings(clean_vehicles, 3)
            },
            'advanced_analysis': advanced_analysis,  # NEW: Advanced insights
            'insights': self._generate_insights(clean_vehicles, user_query, advanced_analysis),
            'recommendation': self._generate_recommendation(clean_vehicles, user_query, advanced_analysis)
        }
        
        return analysis
    
    def _clean_vehicle_data(self, vehicles: List[Dict]) -> List[Dict]:
        """Remove invalid listings and outliers"""
        clean = []
        
        for vehicle in vehicles:
            price = vehicle.get('price')
            year = vehicle.get('year')
            
            # Basic validation
            if not price or not isinstance(price, (int, float)):
                continue
            
            if price < self.min_valid_price or price > self.max_valid_price:
                continue
                
            if year and (year < 1990 or year > datetime.now().year + 1):
                continue
            
            clean.append(vehicle)
        
        # Remove extreme outliers (beyond 2 standard deviations)
        if len(clean) > 5:
            prices = [v['price'] for v in clean]
            mean_price = statistics.mean(prices)
            std_price = statistics.stdev(prices)
            
            lower_bound = mean_price - (2 * std_price)
            upper_bound = mean_price + (2 * std_price)
            
            clean = [v for v in clean if lower_bound <= v['price'] <= upper_bound]
        
        return clean
    
    def _get_sample_listings(self, vehicles: List[Dict], count: int = 3) -> List[Dict]:
        """Get representative sample of listings"""
        # Sort by price and pick spread
        sorted_vehicles = sorted(vehicles, key=lambda x: x['price'])
        
        if len(sorted_vehicles) <= count:
            return sorted_vehicles
        
        # Pick low, medium, high
        indices = [0, len(sorted_vehicles) // 2, len(sorted_vehicles) - 1]
        
        samples = []
        for i in indices:
            vehicle = sorted_vehicles[i]
            samples.append({
                'price': vehicle['price'],
                'year': vehicle.get('year'),
                'km': vehicle.get('km'),
                'city': vehicle.get('cityEn', vehicle.get('city', 'Unknown')),
                'url': vehicle.get('url', '').split('/')[-1] if vehicle.get('url') else None
            })
        
        return samples[:count]
    
    def _generate_insights(self, vehicles: List[Dict], query: Dict, advanced_analysis: Dict = None) -> List[str]:
        """Generate market insights from the data - ENHANCED with OME-84"""
        insights = []
        prices = [v['price'] for v in vehicles]
        
        # Basic insights (existing)
        if len(vehicles) >= 5:
            avg_price = statistics.mean(prices)
            median_price = statistics.median(prices)
            
            if abs(avg_price - median_price) / avg_price > 0.15:
                if avg_price > median_price:
                    insights.append("Price distribution skews higher - some expensive outliers in market")
                else:
                    insights.append("Price distribution skews lower - good deals available")
        
        # ENHANCED: Advanced analysis insights (OME-84)
        if advanced_analysis:
            # Mileage correlation insights
            mileage_analysis = advanced_analysis.get('mileage_analysis', {})
            if mileage_analysis.get('status') == 'success':
                insights.extend(mileage_analysis.get('insights', []))
            
            # Geographic insights
            geo_analysis = advanced_analysis.get('geographic_analysis', {})
            if geo_analysis.get('status') == 'success':
                insights.extend(geo_analysis.get('insights', []))
            
            # Content analysis insights
            content_analysis = advanced_analysis.get('content_analysis', {})
            if content_analysis.get('status') == 'success':
                insights.extend(content_analysis.get('insights', []))
        
        # Fallback to basic mileage insights if advanced analysis failed
        if not advanced_analysis or advanced_analysis.get('mileage_analysis', {}).get('status') != 'success':
            mileage_data = [v for v in vehicles if v.get('km') and isinstance(v.get('km'), (int, float))]
            if len(mileage_data) >= 3:
                avg_km = statistics.mean([v['km'] for v in mileage_data])
                user_km = query.get('km')
                
                if user_km:
                    if user_km < avg_km * 0.8:
                        insights.append(f"Your {user_km:,} km is below market average ({avg_km:,.0f} km) - expect premium pricing")
                    elif user_km > avg_km * 1.2:
                        insights.append(f"Your {user_km:,} km is above market average ({avg_km:,.0f} km) - expect lower pricing")
        
        # Market size insights
        if len(vehicles) < 5:
            insights.append("Limited market data - consider expanding search criteria (year range, areas)")
        elif len(vehicles) > 20:
            insights.append("Rich market data - pricing estimates are highly reliable")
        
        return insights
    
    def _generate_recommendation(self, vehicles: List[Dict], query: Dict, advanced_analysis: Dict = None) -> Dict:
        """Generate pricing recommendation - ENHANCED with OME-84"""
        prices = [v['price'] for v in vehicles]
        
        if len(prices) < 3:
            return {
                'confidence': 'low',
                'range': f"{min(prices):,} - {max(prices):,} ILS",
                'note': "Limited data available - use with caution"
            }
        
        median_price = int(statistics.median(prices))
        q1 = int(statistics.quantiles(prices, n=4)[0])  # 25th percentile  
        q3 = int(statistics.quantiles(prices, n=4)[2])  # 75th percentile
        
        # ENHANCED: Adjust confidence based on advanced analysis (OME-84)
        base_confidence = 'high' if len(prices) >= 10 else 'medium'
        confidence = base_confidence
        
        confidence_factors = []
        
        if advanced_analysis:
            # Geographic analysis boosts confidence
            geo_analysis = advanced_analysis.get('geographic_analysis', {})
            if geo_analysis.get('status') == 'success' and len(geo_analysis.get('city_analysis', {})) >= 3:
                confidence_factors.append("diverse geographic data")
            
            # Mileage correlation boosts confidence
            mileage_analysis = advanced_analysis.get('mileage_analysis', {})
            if mileage_analysis.get('status') == 'success':
                correlation = abs(mileage_analysis.get('correlation_coefficient', 0))
                if correlation > 0.5:
                    confidence_factors.append("strong mileage-price correlation")
            
            # Content analysis adds confidence
            content_analysis = advanced_analysis.get('content_analysis', {})
            if content_analysis.get('status') == 'success':
                total_analyzed = content_analysis.get('premium_listings', 0) + content_analysis.get('discount_listings', 0) + content_analysis.get('neutral_listings', 0)
                if total_analyzed >= 5:
                    confidence_factors.append("detailed content analysis")
        
        # Upgrade confidence if we have multiple factors
        if len(confidence_factors) >= 2 and base_confidence == 'medium':
            confidence = 'high'
        elif len(confidence_factors) >= 1 and base_confidence == 'medium':
            confidence = 'medium-high'
        
        note = f"Based on {len(vehicles)} current listings"
        if confidence == 'high':
            note += " - highly reliable estimate"
        elif confidence == 'medium-high':
            note += " - reliable estimate with advanced analysis"
        
        if confidence_factors:
            note += f" ({', '.join(confidence_factors)})"
        
        return {
            'confidence': confidence,
            'estimated_value': f"{q1:,} - {q3:,} ILS",
            'median_market': f"{median_price:,} ILS",
            'note': note,
            'advanced_factors': confidence_factors  # NEW: What made this estimate reliable
        }
    
    def format_analysis_for_user(self, analysis: Dict, hebrew_response: bool = False) -> str:
        """Format analysis in conversational Hebrew/English style"""
        if analysis['status'] != 'success':
            error_msg = analysis.get('message', 'Unable to analyze market data')
            if hebrew_response:
                return f"❌ {self._translate_error_to_hebrew(error_msg)}"
            return f"❌ {error_msg}"
        
        query = analysis['query']
        market = analysis['market_data']
        insights = analysis['insights']
        rec = analysis['recommendation']
        advanced = analysis.get('advanced_analysis', {})
        
        if hebrew_response:
            return self._format_hebrew_response(query, market, insights, rec, advanced)
        else:
            return self._format_english_response(query, market, insights, rec, advanced)
    
    def _format_english_response(self, query, market, insights, rec, advanced=None) -> str:
        """Format English response - ENHANCED with OME-84 advanced analysis"""
        # Header
        result = f"🚗 **{query.get('year')} {query.get('manufacturer')} {query.get('model')} Smart Market Analysis**\n\n"
        
        # Market data  
        result += f"📊 **Current Market** (based on {market['listings_found']} active listings):\n"
        result += f"   💰 Price range: {market['price_range']['min']:,} - {market['price_range']['max']:,} ILS\n"
        result += f"   📈 Average: {market['price_range']['average']:,} ILS\n"
        result += f"   🎯 Median: {market['price_range']['median']:,} ILS\n\n"
        
        # Recommendation
        result += f"🎯 **Smart Valuation**: {rec['estimated_value']}\n"
        result += f"   📊 Market median: {rec['median_market']}\n"
        result += f"   🔍 Confidence: {rec['confidence'].title()}\n"
        result += f"   📝 {rec['note']}\n\n"
        
        # ENHANCED: Advanced Analysis Summary (OME-84)
        if advanced:
            result += f"🧠 **Advanced Analysis Summary**:\n"
            
            # Mileage correlation
            mileage = advanced.get('mileage_analysis', {})
            if mileage.get('status') == 'success':
                correlation = mileage.get('correlation_coefficient', 0)
                result += f"   📏 Mileage impact: {abs(correlation):.2f} correlation coefficient\n"
                
                depreciation = mileage.get('depreciation_per_km', 0)
                if abs(depreciation) > 0.1:
                    result += f"   📉 Depreciation: {abs(depreciation):.2f} ILS per km\n"
            
            # Geographic spread
            geo = advanced.get('geographic_analysis', {})
            if geo.get('status') == 'success':
                cities = geo.get('city_analysis', {})
                if cities:
                    city_count = len(cities)
                    result += f"   🗺️ Geographic spread: {city_count} regions analyzed\n"
            
            # Content analysis
            content = advanced.get('content_analysis', {})
            if content.get('status') == 'success':
                premium_pct = content.get('premium_advantage')
                discount_pct = content.get('discount_impact')
                if premium_pct:
                    result += f"   ✨ Premium features boost: +{premium_pct}%\n"
                if discount_pct:
                    result += f"   ⚠️ Condition issues impact: -{discount_pct}%\n"
            
            result += "\n"
        
        # Insights
        if insights:
            result += f"💡 **Smart Market Insights**:\n"
            for insight in insights:
                result += f"   • {insight}\n"
            result += "\n"
        
        # Sample listings
        if market.get('sample_listings'):
            result += f"📋 **Sample Current Listings**:\n"
            for i, listing in enumerate(market['sample_listings'], 1):
                km_str = f", {listing['km']:,} km" if listing.get('km') else ""
                result += f"   {i}. {listing['price']:,} ILS ({listing.get('year', 'N/A')}{km_str}, {listing.get('city', 'Unknown')})\n"
        
        return result
    
    def _format_hebrew_response(self, query, market, insights, rec, advanced=None) -> str:
        """Format Hebrew response - ENHANCED with OME-84 advanced analysis"""
        manufacturer_hebrew = self._get_hebrew_manufacturer(query.get('manufacturer', ''))
        model_hebrew = self._get_hebrew_model(query.get('model', ''))
        
        # Header
        result = f"🚗 **ניתוח שוק חכם: {manufacturer_hebrew} {model_hebrew} {query.get('year')}**\n\n"
        
        # Market data
        result += f"📊 **שוק נוכחי** (מבוסס על {market['listings_found']} מודעות פעילות):\n"
        result += f"   💰 טווח מחירים: {market['price_range']['min']:,} - {market['price_range']['max']:,} ₪\n"
        result += f"   📈 ממוצע: {market['price_range']['average']:,} ₪\n"
        result += f"   🎯 חציון: {market['price_range']['median']:,} ₪\n\n"
        
        # Recommendation
        confidence_hebrew = self._get_hebrew_confidence(rec['confidence'])
        result += f"🎯 **הערכת שווי חכמה**: {rec['estimated_value'].replace('ILS', '₪')}\n"
        result += f"   📊 חציון השוק: {rec['median_market'].replace('ILS', '₪')}\n"
        result += f"   🔍 רמת ביטחון: {confidence_hebrew}\n"
        result += f"   📝 {self._translate_note_to_hebrew(rec['note'])}\n\n"
        
        # ENHANCED: Advanced Analysis Summary (OME-84)
        if advanced:
            result += f"🧠 **סיכום ניתוח מתקדם**:\n"
            
            # Mileage correlation
            mileage = advanced.get('mileage_analysis', {})
            if mileage.get('status') == 'success':
                correlation = mileage.get('correlation_coefficient', 0)
                result += f"   📏 השפעת קילומטראז': מקדם קורלציה {abs(correlation):.2f}\n"
                
                depreciation = mileage.get('depreciation_per_km', 0)
                if abs(depreciation) > 0.1:
                    result += f"   📉 פחת: {abs(depreciation):.2f} ₪ לקילומטר\n"
            
            # Geographic spread
            geo = advanced.get('geographic_analysis', {})
            if geo.get('status') == 'success':
                cities = geo.get('city_analysis', {})
                if cities:
                    city_count = len(cities)
                    result += f"   🗺️ פיזור גיאוגרפי: {city_count} אזורים נותחו\n"
            
            # Content analysis
            content = advanced.get('content_analysis', {})
            if content.get('status') == 'success':
                premium_pct = content.get('premium_advantage')
                discount_pct = content.get('discount_impact')
                if premium_pct:
                    result += f"   ✨ תוספת פיצ'רים פרמיום: +{premium_pct}%\n"
                if discount_pct:
                    result += f"   ⚠️ השפעת בעיות: -{discount_pct}%\n"
            
            result += "\n"
        
        # Insights (translate to Hebrew)
        if insights:
            result += f"💡 **תובנות שוק חכמות**:\n"
            for insight in insights:
                hebrew_insight = self._translate_insight_to_hebrew(insight)
                result += f"   • {hebrew_insight}\n"
            result += "\n"
        
        # Sample listings
        if market.get('sample_listings'):
            result += f"📋 **דוגמאות מודעות נוכחיות**:\n"
            for i, listing in enumerate(market['sample_listings'], 1):
                km_str = f", {listing['km']:,} ק״מ" if listing.get('km') else ""
                city_hebrew = self._get_hebrew_city(listing.get('city', 'Unknown'))
                result += f"   {i}. {listing['price']:,} ₪ ({listing.get('year', 'לא ידוע')}{km_str}, {city_hebrew})\n"
        
        return result
    
    def _get_hebrew_manufacturer(self, manufacturer: str) -> str:
        """Convert English manufacturer to Hebrew"""
        hebrew_map = {
            'Toyota': 'טויוטה',
            'Honda': 'הונדה', 
            'Hyundai': 'יונדאי',
            'Nissan': 'ניסאן',
            'Mazda': 'מאזדה',
            'Subaru': 'סובארו',
            'Volkswagen': 'פולקסווגן',
            'BMW': 'ב.מ.וו',
            'Mercedes': 'מרצדס',
            'Audi': 'אאודי',
            'Peugeot': 'פז\'ו',
            'Renault': 'רנו',
            'Ford': 'פורד',
            'Chevrolet': 'שברולט',
            'Fiat': 'פיאט',
            'Skoda': 'שקודה',
            'SEAT': 'סיאט',
            'Kia': 'קיה'
        }
        return hebrew_map.get(manufacturer, manufacturer)
    
    def _get_hebrew_model(self, model: str) -> str:
        """Convert English model to Hebrew"""
        hebrew_map = {
            'Corolla': 'קורולה',
            'Camry': 'קמרי',
            'Prius': 'פריוס', 
            'Yaris': 'יאריס',
            'RAV4': 'רב-4',
            'Civic': 'סיוויק',
            'Accord': 'אקורד',
            'CR-V': 'סי-אר-וי',
            'Elantra': 'אלנטרה',
            'Tucson': 'טוסון',
            'Kona': 'קונה',
            'Picanto': 'פיקנטו',
            'Rio': 'ריו',
            'Ceed': 'סיד',
            'Sportage': 'ספורטג\'',
            'Sorento': 'סורנטו',
            'Polo': 'פולו',
            'Golf': 'גולף',
            'Jetta': 'ג\'טה',
            'Passat': 'פאסאט',
            'Tiguan': 'טיגואן',
            'Micra': 'מיקרה',
            'Sentra': 'סנטרה',
            'Qashqai': 'קשקאי',
            'Juke': 'ג\'וק',
            'Series 1': 'סדרה 1',
            'Series 3': 'סדרה 3',
            'Series 5': 'סדרה 5',
            'A-Class': 'מחלקה A',
            'C-Class': 'מחלקה C',
            'E-Class': 'מחלקה E',
            'Ibiza': 'איביזה',
            'Leon': 'ליאון',
            'Ateca': 'אטקה',
            'Fabia': 'פאביה',
            'Octavia': 'אוקטביה',
            'Superb': 'סופרב',
            'Kodiaq': 'קודיאק'
        }
        return hebrew_map.get(model, model)
    
    def _get_hebrew_confidence(self, confidence: str) -> str:
        """Convert confidence level to Hebrew"""
        hebrew_map = {
            'high': 'גבוהה',
            'medium': 'בינונית', 
            'low': 'נמוכה'
        }
        return hebrew_map.get(confidence.lower(), confidence)
    
    def _get_hebrew_city(self, city: str) -> str:
        """Convert English city names to Hebrew"""
        hebrew_map = {
            'Tel Aviv': 'תל אביב',
            'Jerusalem': 'ירושלים',
            'Haifa': 'חיפה',
            'Petah Tikva': 'פתח תקווה',
            'Rishon LeZion': 'ראשון לציון',
            'Ashdod': 'אשדוד',
            'Netanya': 'נתניה',
            'Beer Sheva': 'באר שבע',
            'Holon': 'חולון',
            'Ramat Gan': 'רמת גן',
            'Rosh ha-Ayin': 'ראש העין',
            'Ra\'anana': 'רעננה',
            'Raanana': 'רעננה',
            'Herzliya': 'הרצליה',
            'Kfar Saba': 'כפר סבא',
            'Rehovot': 'רחובות',
            'Unknown': 'לא ידוע'
        }
        return hebrew_map.get(city, city)
    
    def _translate_note_to_hebrew(self, note: str) -> str:
        """Translate recommendation note to Hebrew"""
        if 'current listings' in note and 'highly reliable' in note:
            count = re.search(r'(\d+)', note)
            if count:
                return f"מבוסס על {count.group(1)} מודעות נוכחיות - הערכה אמינה ביותר"
        elif 'current listings' in note:
            count = re.search(r'(\d+)', note)
            if count:
                return f"מבוסס על {count.group(1)} מודעות נוכחיות"
        return note
    
    def _translate_insight_to_hebrew(self, insight: str) -> str:
        """Translate market insights to Hebrew"""
        if 'below market average' in insight and 'expect premium' in insight:
            return insight.replace('Your', 'הקילומטראז\' שלך').replace('km is below market average', 'ק״מ נמוך מהממוצע בשוק').replace('expect premium pricing', 'צפה למחיר גבוה יותר')
        elif 'above market average' in insight and 'expect lower' in insight:
            return insight.replace('Your', 'הקילומטראז\' שלך').replace('km is above market average', 'ק״מ גבוה מהממוצע בשוק').replace('expect lower pricing', 'צפה למחיר נמוך יותר')
        elif 'Rich market data' in insight:
            return "נתוני שוק עשירים - הערכות מחיר אמינות ביותר"
        elif 'Limited market data' in insight:
            return "נתוני שוק מוגבלים - כדאי להרחיב קריטריונים (טווח שנים, אזורים)"
        elif 'Price distribution skews higher' in insight:
            return "התפלגות מחירים נוטה גבוה - יש כמה יוקרתיים בשוק"
        elif 'Price distribution skews lower' in insight:
            return "התפלגות מחירים נוטה נמוך - יש עסקאות טובות זמינות"
        return insight
    
    def _translate_error_to_hebrew(self, error: str) -> str:
        """Translate error messages to Hebrew"""
        if 'No current listings found' in error:
            return error.replace('No current listings found for', 'לא נמצאו מודעות נוכחיות עבור')
        elif 'invalid pricing data' in error:
            return "נמצאו מודעות אבל הן מכילות נתוני מחיר לא תקינים"
        return error
    
    def _format_intent_analysis(self, intent_analysis: Dict, hebrew_response: bool = False) -> str:
        """Format buyer/seller specific analysis - NEW for OME-90"""
        if intent_analysis['analysis']['status'] != 'success':
            return ""
        
        intent_type = intent_analysis['intent']['type']
        specific_price = intent_analysis['intent']['specific_price']
        
        if hebrew_response:
            return self._format_intent_hebrew(intent_analysis, intent_type, specific_price)
        else:
            return self._format_intent_english(intent_analysis, intent_type, specific_price)
    
    def _format_intent_english(self, intent_analysis: Dict, intent_type: str, specific_price: Optional[int]) -> str:
        """Format buyer/seller analysis in English"""
        analysis = intent_analysis['analysis']
        
        if intent_type == 'buying' and specific_price:
            buyer_data = analysis.get('buyer_analysis', {})
            deal_quality = buyer_data.get('deal_quality', {})
            price_vs_market = buyer_data.get('price_vs_market', {})
            negotiation = buyer_data.get('negotiation_advice', {})
            
            result = f"\n🛒 **BUYER ANALYSIS** for {specific_price:,} ILS:\n"
            result += f"   📈 Deal Quality: **{deal_quality.get('rating', 'Unknown').title()}** - {deal_quality.get('description', 'N/A')}\n"
            result += f"   💡 Recommendation: {deal_quality.get('recommendation', 'N/A')}\n"
            
            if price_vs_market:
                diff_pct = price_vs_market.get('difference_percentage', 0)
                if diff_pct > 0:
                    result += f"   📊 Price vs Market: {diff_pct}% ABOVE median ({price_vs_market.get('market_median', 0):,} ILS)\n"
                else:
                    result += f"   📊 Price vs Market: {abs(diff_pct)}% BELOW median ({price_vs_market.get('market_median', 0):,} ILS)\n"
            
            if negotiation.get('should_negotiate', False):
                result += f"   💬 Negotiation: Try for {negotiation.get('target_price_range', 'N/A')}\n"
                points = negotiation.get('negotiation_points', [])
                if points:
                    result += f"   🎯 Key Points: {', '.join(points[:2])}\n"
            
            return result
            
        elif intent_type == 'selling':
            seller_data = analysis.get('seller_analysis', {})
            pricing = seller_data.get('pricing_strategy', {})
            timing = seller_data.get('timing_analysis', {})
            competitive = seller_data.get('competitive_analysis', {})
            
            result = f"\n💰 **SELLER ANALYSIS**:\n"
            
            if pricing:
                result += f"   🎯 **Pricing Recommendations**:\n"
                if 'quick_sale' in pricing:
                    result += f"      💨 Quick Sale: {pricing['quick_sale']['price']:,} ILS ({pricing['quick_sale']['description']})\n"
                if 'market_rate' in pricing:
                    result += f"      📊 Market Rate: {pricing['market_rate']['price']:,} ILS ({pricing['market_rate']['description']})\n"
                if 'optimistic' in pricing:
                    result += f"      🚀 Optimistic: {pricing['optimistic']['price']:,} ILS ({pricing['optimistic']['description']})\n"
            
            if timing:
                result += f"   ⏰ Timing: {timing.get('description', 'N/A')}\n"
                result += f"   📅 Expected Sale Time: {timing.get('expected_time_to_sell', 'N/A')}\n"
            
            if competitive:
                position = competitive.get('position', 'Unknown')
                result += f"   🏆 Competitive Position: {position}\n"
                
                advantages = competitive.get('competitive_advantages', [])
                if advantages:
                    result += f"   ✨ Your Advantages: {', '.join(advantages[:2])}\n"
            
            return result
        
        return ""
    
    def _format_intent_hebrew(self, intent_analysis: Dict, intent_type: str, specific_price: Optional[int]) -> str:
        """Format buyer/seller analysis in Hebrew"""
        analysis = intent_analysis['analysis']
        
        if intent_type == 'buying' and specific_price:
            buyer_data = analysis.get('buyer_analysis', {})
            deal_quality = buyer_data.get('deal_quality', {})
            price_vs_market = buyer_data.get('price_vs_market', {})
            negotiation = buyer_data.get('negotiation_advice', {})
            
            result = f"\n🛒 **ניתוח לקונה** עבור {specific_price:,} ₪:\n"
            
            # Translate deal quality rating to Hebrew
            rating_hebrew = {
                'excellent': 'מעולה',
                'good': 'טוב', 
                'fair': 'הוגן',
                'expensive': 'יקר',
                'overpriced': 'יקר מדי'
            }.get(deal_quality.get('rating', 'unknown'), 'לא ידוע')
            
            result += f"   📈 איכות העסקה: **{rating_hebrew}** - {deal_quality.get('description', 'לא זמין')}\n"
            result += f"   💡 המלצה: {deal_quality.get('recommendation', 'לא זמין')}\n"
            
            if price_vs_market:
                diff_pct = price_vs_market.get('difference_percentage', 0)
                if diff_pct > 0:
                    result += f"   📊 המחיר שלך: {diff_pct}% מעל החציון ({price_vs_market.get('market_median', 0):,} ₪)\n"
                else:
                    result += f"   📊 המחיר שלך: {abs(diff_pct)}% מתחת לחציון ({price_vs_market.get('market_median', 0):,} ₪)\n"
            
            if negotiation.get('should_negotiate', False):
                result += f"   💬 מיקוח: נסה להגיע ל-{negotiation.get('target_price_range', 'לא זמין')}\n"
                points = negotiation.get('negotiation_points', [])
                if points:
                    result += f"   🎯 נקודות מפתח: {', '.join(points[:2])}\n"
            
            return result
            
        elif intent_type == 'selling':
            seller_data = analysis.get('seller_analysis', {})
            pricing = seller_data.get('pricing_strategy', {})
            timing = seller_data.get('timing_analysis', {})
            competitive = seller_data.get('competitive_analysis', {})
            
            result = f"\n💰 **ניתוח למוכר**:\n"
            
            if pricing:
                result += f"   🎯 **המלצות תמחור**:\n"
                if 'quick_sale' in pricing:
                    result += f"      💨 מכירה מהירה: {pricing['quick_sale']['price']:,} ₪ ({pricing['quick_sale']['description']})\n"
                if 'market_rate' in pricing:
                    result += f"      📊 מחיר שוק: {pricing['market_rate']['price']:,} ₪ ({pricing['market_rate']['description']})\n"
                if 'optimistic' in pricing:
                    result += f"      🚀 מחיר אופטימי: {pricing['optimistic']['price']:,} ₪ ({pricing['optimistic']['description']})\n"
            
            if timing:
                # Translate timing recommendation
                timing_desc = timing.get('description', 'לא זמין')
                if 'good time' in timing_desc:
                    timing_desc = timing_desc.replace('זמן טוב למכירה', 'זמן טוב למכירה').replace('יש הרבה עניין', 'יש הרבה עניין')
                
                result += f"   ⏰ עיתוי: {timing_desc}\n"
                result += f"   📅 זמן מכירה משוער: {timing.get('expected_time_to_sell', 'לא ידוע')}\n"
            
            if competitive:
                position = competitive.get('position', 'לא ידוע')
                result += f"   🏆 מיקום תחרותי: {position}\n"
                
                advantages = competitive.get('competitive_advantages', [])
                if advantages:
                    result += f"   ✨ היתרונות שלך: {', '.join(advantages[:2])}\n"
            
            return result
        
        return ""

def analyze_user_query_with_intent(vehicles: List[Dict], user_query_text: str, year: int, manufacturer: str, model: str, km: Optional[int] = None, hebrew_response: bool = False) -> str:
    """
    ENHANCED: Analyze market data with buyer/seller intent detection (OME-90)
    
    Args:
        vehicles: List of vehicle data from scraping  
        user_query_text: The actual user query text for intent detection
        year: Vehicle year
        manufacturer: Car manufacturer
        model: Car model
        km: Optional mileage
        hebrew_response: If True, return Hebrew response
    
    Usage:
        vehicles = api.run_single_query(query)
        result = analyze_user_query_with_intent(
            vehicles, "האם 85,000 ₪ זה מחיר טוב?", 
            2019, "Toyota", "Corolla", 60000, hebrew_response=True
        )
        print(result)
    """
    analyzer = MarketAnalyzer()
    
    vehicle_specs = {
        'year': year,
        'manufacturer': manufacturer,
        'model': model
    }
    
    if km is not None:
        vehicle_specs['km'] = km
    
    # Step 1: Standard market analysis
    analysis = analyzer.analyze_vehicle_listings(vehicles, vehicle_specs)
    
    if analysis['status'] != 'success':
        return analyzer.format_analysis_for_user(analysis, hebrew_response=hebrew_response)
    
    # Step 2: NEW - Buyer/Seller Intent Analysis (OME-90)
    intent_analysis = analyze_buyer_seller_intent(user_query_text, vehicles, analysis, vehicle_specs)
    
    # Step 3: Enhanced formatting with intent-specific advice
    base_response = analyzer.format_analysis_for_user(analysis, hebrew_response=hebrew_response)
    
    # Add buyer/seller specific insights
    if intent_analysis['intent']['type'] in ['buying', 'selling']:
        intent_response = analyzer._format_intent_analysis(intent_analysis, hebrew_response)
        base_response = f"{base_response}\n{intent_response}"
    
    return base_response

def analyze_user_query(vehicles: List[Dict], year: int, manufacturer: str, model: str, km: Optional[int] = None, hebrew_response: bool = False) -> str:
    """
    Main function to analyze market data for user query
    
    Args:
        vehicles: List of vehicle data from scraping
        year: Vehicle year
        manufacturer: Car manufacturer
        model: Car model
        km: Optional mileage
        hebrew_response: If True, return Hebrew response
    
    Usage:
        vehicles = api.run_single_query(query)
        result = analyze_user_query(vehicles, 2019, "Toyota", "Corolla", 60000, hebrew_response=True)
        print(result)
    """
    analyzer = MarketAnalyzer()
    
    user_query = {
        'year': year,
        'manufacturer': manufacturer,
        'model': model
    }
    
    if km is not None:
        user_query['km'] = km
    
    analysis = analyzer.analyze_vehicle_listings(vehicles, user_query)
    return analyzer.format_analysis_for_user(analysis, hebrew_response=hebrew_response)

if __name__ == "__main__":
    # Test with sample data
    sample_vehicles = [
        {'price': 85000, 'year': 2019, 'km': 45000, 'cityEn': 'Tel Aviv'},
        {'price': 92000, 'year': 2019, 'km': 38000, 'cityEn': 'Haifa'},
        {'price': 88000, 'year': 2019, 'km': 52000, 'cityEn': 'Jerusalem'},
    ]
    
    result = analyze_user_query(sample_vehicles, 2019, "Toyota", "Corolla", 50000)
    print(result)