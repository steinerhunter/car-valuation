#!/usr/bin/env python3
"""
Buyer & Seller Intelligence Engine for Car Valuation
Part of OME-90: Yad2 Ultra-Smart Analysis

Provides intelligent analysis for both buyers and sellers:
- Buyers: "Is this price good? Should I negotiate?"
- Sellers: "What should I ask? When to sell?"
"""

import re
import statistics
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from dataclasses import dataclass

@dataclass
class UserIntent:
    """Represents user's buying/selling intent"""
    intent_type: str  # 'buying', 'selling', 'general'
    specific_price: Optional[int] = None  # If user mentions a specific price
    urgency: str = 'normal'  # 'urgent', 'normal', 'flexible'
    context_clues: List[str] = None

    def __post_init__(self):
        if self.context_clues is None:
            self.context_clues = []

class IntentDetector:
    """Detects whether user is buying, selling, or asking general questions"""
    
    def __init__(self):
        # Hebrew and English patterns for intent detection
        self.buying_patterns = [
            # Hebrew buying patterns
            r'כדאי לקנות',
            r'האם.*טוב.*מחיר',
            r'האם.*כדאי',
            r'עסקה טובה',
            r'שווה לקנות',
            r'מחיר הוגן',
            r'לקנות ב',
            r'מציעים.*₪',
            r'מבקשים.*₪',
            r'ראיתי ב.*₪',
            r'מוכר ב',
            r'למכור ב',
            
            # English buying patterns
            r'should I buy',
            r'is.*good price',
            r'worth buying',
            r'good deal',
            r'fair price',
            r'asking.*for',
            r'seller wants',
            r'offering.*for',
            r'negotiate'
        ]
        
        self.selling_patterns = [
            # Hebrew selling patterns
            r'כמה שווה.*שלי',
            r'רכב שלי',
            r'הרכב של',
            r'למכור את',
            r'מוכר את',
            r'מה לבקש',
            r'איזה מחיר לבקש',
            r'כמה לבקש',
            r'שווה הרכב',
            r'מעריך.*רכב',
            
            # English selling patterns  
            r'my car worth',
            r'selling my',
            r'what should I ask',
            r'how much.*my.*worth',
            r'value my',
            r'price my car',
            r'what to ask'
        ]
        
        # Price extraction patterns
        self.price_patterns = [
            r'(\d{1,3}(?:,\d{3})+).*₪',  # Israeli format: 85,000 ₪
            r'₪(\d{1,3}(?:,\d{3})+)',   # Shekel first: ₪85,000
            r'(\d{2,6}).*₪',            # Simple format: 85000 ₪
            r'(\d{2,3})\s*אלף',         # Hebrew thousands: 85 אלף
            r'(\d{1,3}(?:,\d{3})+)\s*שקל',  # Hebrew shekels
            r'(\d{1,3}(?:,\d{3})+)\s*ILS',  # International format
        ]
        
        self.urgency_patterns = {
            'urgent': [r'דחוף', r'מהר', r'בהקדם', r'urgent', r'quickly', r'asap', r'soon'],
            'flexible': [r'זמן', r'לא ממהר', r'בעתיד', r'flexible', r'patient', r'no rush', r'future']
        }
    
    def detect_intent(self, query: str) -> UserIntent:
        """Analyze user query to determine buying/selling intent"""
        query_lower = query.lower()
        
        # Count matches for each intent type
        buying_score = sum(1 for pattern in self.buying_patterns 
                          if re.search(pattern, query_lower))
        selling_score = sum(1 for pattern in self.selling_patterns 
                           if re.search(pattern, query_lower))
        
        # Extract specific price if mentioned
        specific_price = self._extract_price(query)
        
        # Determine urgency
        urgency = self._detect_urgency(query_lower)
        
        # Collect context clues
        context_clues = self._extract_context_clues(query_lower)
        
        # Determine intent type
        if buying_score > selling_score and buying_score > 0:
            intent_type = 'buying'
        elif selling_score > buying_score and selling_score > 0:
            intent_type = 'selling'
        else:
            intent_type = 'general'
        
        return UserIntent(
            intent_type=intent_type,
            specific_price=specific_price,
            urgency=urgency,
            context_clues=context_clues
        )
    
    def _extract_price(self, query: str) -> Optional[int]:
        """Extract specific price mentioned by user"""
        for pattern in self.price_patterns:
            match = re.search(pattern, query)
            if match:
                price_str = match.group(1).replace(',', '')
                try:
                    price = int(price_str)
                    # Handle "אלף" (thousands)
                    if 'אלף' in query.lower():
                        price *= 1000
                    return price
                except ValueError:
                    continue
        return None
    
    def _detect_urgency(self, query: str) -> str:
        """Detect urgency level from query"""
        for urgency_level, patterns in self.urgency_patterns.items():
            if any(re.search(pattern, query) for pattern in patterns):
                return urgency_level
        return 'normal'
    
    def _extract_context_clues(self, query: str) -> List[str]:
        """Extract additional context clues from query"""
        clues = []
        
        # Financial context
        if any(word in query for word in ['משכנתא', 'הלוואה', 'מימון', 'loan', 'finance']):
            clues.append('financing_concern')
        
        if any(word in query for word in ['ראשון', 'שני', 'first car', 'second car']):
            clues.append('experience_level')
        
        if any(word in query for word in ['משפחה', 'ילדים', 'family', 'kids']):
            clues.append('family_use')
        
        if any(word in query for word in ['עבודה', 'business', 'commercial']):
            clues.append('business_use')
        
        return clues

class BuyerAnalyzer:
    """Specialized analysis for car buyers"""
    
    def __init__(self):
        self.negotiation_thresholds = {
            'great_deal': -0.15,      # 15% below market median
            'good_deal': -0.08,       # 8% below market median  
            'fair_price': 0.08,       # Within 8% of median
            'overpriced': 0.15,       # 15% above median
            'very_overpriced': 0.25   # 25% above median
        }
    
    def analyze_buyer_query(self, vehicles: List[Dict], market_analysis: Dict, 
                          user_price: int, vehicle_specs: Dict) -> Dict:
        """Provide buyer-specific analysis and recommendations"""
        
        if not vehicles or market_analysis.get('status') != 'success':
            return {
                'status': 'insufficient_data',
                'message': 'Not enough market data for buyer analysis'
            }
        
        market_data = market_analysis['market_data']
        market_median = market_data['price_range']['median']
        
        # Calculate price position relative to market
        price_difference = user_price - market_median
        price_percentage = (price_difference / market_median) * 100
        
        # Determine deal quality
        deal_quality = self._assess_deal_quality(price_percentage)
        
        # Generate negotiation strategy
        negotiation_advice = self._generate_negotiation_advice(
            user_price, market_median, deal_quality, vehicles
        )
        
        # Market competition analysis
        competition_analysis = self._analyze_competition(vehicles, user_price)
        
        # Risk assessment
        risk_factors = self._assess_buyer_risks(vehicles, market_analysis, user_price)
        
        return {
            'status': 'success',
            'buyer_analysis': {
                'deal_quality': deal_quality,
                'price_vs_market': {
                    'user_price': user_price,
                    'market_median': market_median,
                    'difference_ils': price_difference,
                    'difference_percentage': round(price_percentage, 1)
                },
                'negotiation_advice': negotiation_advice,
                'competition_analysis': competition_analysis,
                'risk_factors': risk_factors
            }
        }
    
    def _assess_deal_quality(self, price_percentage: float) -> Dict:
        """Assess quality of the deal based on market position"""
        if price_percentage <= self.negotiation_thresholds['great_deal'] * 100:
            return {
                'rating': 'excellent',
                'description': 'מעולה - מחיר מתחת לשוק',
                'recommendation': 'עסקה מצוינת - כדאי לקפוץ עליה!'
            }
        elif price_percentage <= self.negotiation_thresholds['good_deal'] * 100:
            return {
                'rating': 'good',
                'description': 'טוב - קרוב לממוצע השוק',
                'recommendation': 'עסקה סבירה - אפשר לקנות'
            }
        elif price_percentage <= self.negotiation_thresholds['fair_price'] * 100:
            return {
                'rating': 'fair',
                'description': 'הוגן - באזור ממוצע השוק',
                'recommendation': 'מחיר הוגן - נסה למנץ קלות'
            }
        elif price_percentage <= self.negotiation_thresholds['overpriced'] * 100:
            return {
                'rating': 'expensive',
                'description': 'יקר - מעל ממוצע השוק',
                'recommendation': 'יקרוק - נסה לנמץ או חפש אחר'
            }
        else:
            return {
                'rating': 'overpriced',
                'description': 'יקר מאוד - מעל השוק משמעותית',
                'recommendation': 'יקר מדי - המליצו לחפש אלטרנטיבות'
            }
    
    def _generate_negotiation_advice(self, user_price: int, market_median: int, 
                                   deal_quality: Dict, vehicles: List[Dict]) -> Dict:
        """Generate specific negotiation strategies"""
        advice = {
            'should_negotiate': deal_quality['rating'] in ['fair', 'expensive', 'overpriced'],
            'target_price_range': None,
            'negotiation_points': [],
            'alternatives': []
        }
        
        if advice['should_negotiate']:
            # Calculate target negotiation range
            if deal_quality['rating'] == 'fair':
                target_reduction = 0.05  # Try for 5% reduction
            elif deal_quality['rating'] == 'expensive':
                target_reduction = 0.10  # Try for 10% reduction
            else:  # overpriced
                target_reduction = 0.15  # Try for 15% reduction
            
            target_price = int(user_price * (1 - target_reduction))
            advice['target_price_range'] = f"{target_price:,} - {int(user_price * 0.95):,} ₪"
            
            # Generate negotiation points based on market data
            advice['negotiation_points'] = self._get_negotiation_points(
                vehicles, user_price, market_median
            )
        
        return advice
    
    def _get_negotiation_points(self, vehicles: List[Dict], user_price: int, 
                              market_median: int) -> List[str]:
        """Generate specific points for negotiation"""
        points = []
        
        # Price-based points
        if user_price > market_median:
            difference = user_price - market_median
            points.append(f"המחיר גבוה ב-{difference:,} ₪ מהממוצע בשוק")
        
        # Find cheaper alternatives in current market
        cheaper_cars = [v for v in vehicles if v['price'] < user_price]
        if len(cheaper_cars) > len(vehicles) * 0.3:  # More than 30% are cheaper
            points.append(f"יש {len(cheaper_cars)} רכבים דומים זולים יותר בשוק")
        
        # High mileage cars as examples
        high_mileage_cars = [v for v in vehicles 
                           if v.get('km', 0) > 0 and v['price'] < user_price]
        if high_mileage_cars:
            avg_km = statistics.mean([v.get('km', 0) for v in high_mileage_cars])
            points.append(f"רכבים עם קילומטראז' דומה ({avg_km:,.0f} קמ) נמכרים בפחות")
        
        # Market timing
        points.append("השוק יציב - אין צורך למהר")
        
        return points[:3]  # Max 3 points for negotiation
    
    def _analyze_competition(self, vehicles: List[Dict], user_price: int) -> Dict:
        """Analyze market competition and alternatives"""
        cheaper_alternatives = [v for v in vehicles if v['price'] < user_price]
        similar_priced = [v for v in vehicles 
                         if abs(v['price'] - user_price) / user_price < 0.05]
        
        return {
            'cheaper_alternatives': len(cheaper_alternatives),
            'similar_priced': len(similar_priced),
            'market_position': f"המחיר שלך במקום {len([v for v in vehicles if v['price'] <= user_price])} מתוך {len(vehicles)}",
            'competition_level': 'high' if len(cheaper_alternatives) > len(vehicles) * 0.4 else 'moderate'
        }
    
    def _assess_buyer_risks(self, vehicles: List[Dict], market_analysis: Dict, 
                          user_price: int) -> List[str]:
        """Assess potential risks for the buyer"""
        risks = []
        
        # Price trend risk
        market_data = market_analysis.get('market_data', {})
        price_range = market_data.get('price_range', {})
        
        if price_range.get('max', 0) - price_range.get('min', 0) > price_range.get('average', 1) * 0.3:
            risks.append("פיזור מחירים גדול בשוק - וודא מצב הרכב")
        
        # Market size risk  
        if len(vehicles) < 5:
            risks.append("נתוני שוק מוגבלים - כדאי לחפש במקומות נוספים")
        
        # Price position risk
        market_median = market_data.get('price_range', {}).get('median', 0)
        if user_price > market_median * 1.2:
            risks.append("המחיר גבוה משמעותית - בדוק מה מיוחד ברכב הזה")
        
        return risks

class SellerAnalyzer:
    """Specialized analysis for car sellers"""
    
    def analyze_seller_query(self, vehicles: List[Dict], market_analysis: Dict,
                           vehicle_specs: Dict, seller_context: Dict = None) -> Dict:
        """Provide seller-specific analysis and recommendations"""
        
        if not vehicles or market_analysis.get('status') != 'success':
            return {
                'status': 'insufficient_data', 
                'message': 'Not enough market data for seller analysis'
            }
        
        market_data = market_analysis['market_data']
        
        # Generate pricing strategy
        pricing_strategy = self._generate_pricing_strategy(vehicles, market_data, vehicle_specs)
        
        # Market timing analysis
        timing_analysis = self._analyze_market_timing(vehicles, market_analysis)
        
        # Competitive positioning
        competitive_analysis = self._analyze_competitive_position(vehicles, vehicle_specs)
        
        # Optimization suggestions
        optimization_tips = self._generate_optimization_tips(vehicles, vehicle_specs)
        
        return {
            'status': 'success',
            'seller_analysis': {
                'pricing_strategy': pricing_strategy,
                'timing_analysis': timing_analysis,
                'competitive_analysis': competitive_analysis,
                'optimization_tips': optimization_tips
            }
        }
    
    def _generate_pricing_strategy(self, vehicles: List[Dict], market_data: Dict, 
                                 vehicle_specs: Dict) -> Dict:
        """Generate optimal pricing strategy for seller"""
        prices = [v['price'] for v in vehicles]
        
        # Calculate price recommendations
        median_price = statistics.median(prices)
        q1 = statistics.quantiles(prices, n=4)[0]  # 25th percentile
        q3 = statistics.quantiles(prices, n=4)[2]  # 75th percentile
        
        # Adjust based on vehicle-specific factors
        adjustment_factor = self._calculate_seller_adjustment(vehicles, vehicle_specs)
        
        # Price recommendations
        quick_sale_price = int(q1 * adjustment_factor)
        market_price = int(median_price * adjustment_factor)  
        optimistic_price = int(q3 * adjustment_factor)
        
        return {
            'quick_sale': {
                'price': quick_sale_price,
                'description': 'למכירה מהירה (תוך שבועיים)',
                'success_probability': '90%'
            },
            'market_rate': {
                'price': market_price,
                'description': 'מחיר שוק (תוך חודש-חודשיים)',
                'success_probability': '70%'
            },
            'optimistic': {
                'price': optimistic_price,
                'description': 'מחיר אופטימי (עד 3-4 חודשים)',
                'success_probability': '40%'
            },
            'recommended': market_price  # Default recommendation
        }
    
    def _calculate_seller_adjustment(self, vehicles: List[Dict], vehicle_specs: Dict) -> float:
        """Calculate price adjustment factor based on vehicle specifics"""
        base_factor = 1.0
        
        # Adjust based on mileage if provided
        user_km = vehicle_specs.get('km')
        if user_km:
            vehicle_kms = [v.get('km', 0) for v in vehicles if v.get('km', 0) > 0]
            if vehicle_kms:
                avg_market_km = statistics.mean(vehicle_kms)
                if user_km < avg_market_km * 0.8:  # Lower mileage
                    base_factor += 0.05
                elif user_km > avg_market_km * 1.2:  # Higher mileage
                    base_factor -= 0.05
        
        return base_factor
    
    def _analyze_market_timing(self, vehicles: List[Dict], market_analysis: Dict) -> Dict:
        """Analyze market timing for optimal selling"""
        # For now, basic timing analysis
        market_size = len(vehicles)
        
        if market_size > 15:
            timing = {
                'recommendation': 'good_time',
                'description': 'זמן טוב למכירה - יש הרבה עניין בדגם',
                'expected_time_to_sell': '4-6 שבועות'
            }
        elif market_size < 5:
            timing = {
                'recommendation': 'excellent_time',
                'description': 'זמן מעולה למכירה - מעט תחרות',
                'expected_time_to_sell': '2-4 שבועות'
            }
        else:
            timing = {
                'recommendation': 'normal_time',
                'description': 'זמן רגיל למכירה',
                'expected_time_to_sell': '6-8 שבועות'
            }
        
        return timing
    
    def _analyze_competitive_position(self, vehicles: List[Dict], vehicle_specs: Dict) -> Dict:
        """Analyze seller's competitive position"""
        user_km = vehicle_specs.get('km', 0)
        
        # Compare with market
        better_than = 0
        worse_than = 0
        
        for vehicle in vehicles:
            vehicle_km = vehicle.get('km', 0)
            if vehicle_km > 0 and user_km > 0:
                if user_km < vehicle_km:
                    better_than += 1
                elif user_km > vehicle_km:
                    worse_than += 1
        
        total_compared = better_than + worse_than
        
        if total_compared > 0:
            position_percentage = (better_than / total_compared) * 100
            
            if position_percentage > 70:
                position = "חזק - קילומטראז' נמוך יחסית"
            elif position_percentage > 40:
                position = "בינוני - קילומטראז' ממוצע"
            else:
                position = "מאתגר - קילומטראז' גבוה יחסית"
        else:
            position = "לא ניתן להשוות - חסרים נתוני קילומטראז'"
        
        return {
            'position': position,
            'better_than_percent': round(position_percentage, 0) if 'position_percentage' in locals() else None,
            'competitive_advantages': self._identify_advantages(vehicles, vehicle_specs)
        }
    
    def _identify_advantages(self, vehicles: List[Dict], vehicle_specs: Dict) -> List[str]:
        """Identify potential competitive advantages"""
        advantages = []
        
        user_km = vehicle_specs.get('km', 0)
        if user_km > 0:
            market_kms = [v.get('km', 0) for v in vehicles if v.get('km', 0) > 0]
            if market_kms:
                avg_km = statistics.mean(market_kms)
                if user_km < avg_km * 0.8:
                    advantages.append(f"קילומטראז' נמוך ({user_km:,} vs ממוצע {avg_km:,.0f})")
        
        # Could add more advantages based on description analysis, etc.
        return advantages
    
    def _generate_optimization_tips(self, vehicles: List[Dict], vehicle_specs: Dict) -> List[str]:
        """Generate tips to optimize selling success"""
        tips = []
        
        # Basic tips for all sellers
        tips.extend([
            "צלם תמונות איכותיות של הרכב מכל הזוויות",
            "כתוב תיאור מפורט וכנה של מצב הרכב",
            "הכן את כל המסמכים מראש (רישוי, ביטוח, בדיקות)",
            "היה זמין למענה מהיר לפניות"
        ])
        
        # Mileage-specific tips
        user_km = vehicle_specs.get('km', 0)
        if user_km > 0:
            market_kms = [v.get('km', 0) for v in vehicles if v.get('km', 0) > 0]
            if market_kms:
                avg_km = statistics.mean(market_kms)
                if user_km < avg_km * 0.8:
                    tips.append("הדגש בפרסום את הקילומטראז' הנמוך - זה יתרון משמעותי")
                elif user_km > avg_km * 1.2:
                    tips.append("הדגש טיפוח ותחזוקה שוטפת כדי לפצות על קילומטראז' גבוה")
        
        return tips[:5]  # Max 5 tips

def analyze_buyer_seller_intent(query: str, vehicles: List[Dict], market_analysis: Dict,
                               vehicle_specs: Dict) -> Dict:
    """
    Main function to provide buyer/seller specific analysis
    
    Args:
        query: User's question/request
        vehicles: Market data from Yad2
        market_analysis: Existing market analysis
        vehicle_specs: Vehicle specifications (year, manufacturer, model, km, etc.)
    
    Returns:
        Analysis tailored for buyers or sellers
    """
    
    # Detect user intent
    detector = IntentDetector()
    intent = detector.detect_intent(query)
    
    result = {
        'intent': {
            'type': intent.intent_type,
            'specific_price': intent.specific_price,
            'urgency': intent.urgency,
            'context_clues': intent.context_clues
        },
        'analysis': None
    }
    
    if intent.intent_type == 'buying' and intent.specific_price:
        # Buyer analysis
        buyer_analyzer = BuyerAnalyzer()
        buyer_analysis = buyer_analyzer.analyze_buyer_query(
            vehicles, market_analysis, intent.specific_price, vehicle_specs
        )
        result['analysis'] = buyer_analysis
        
    elif intent.intent_type == 'selling':
        # Seller analysis
        seller_analyzer = SellerAnalyzer()
        seller_analysis = seller_analyzer.analyze_seller_query(
            vehicles, market_analysis, vehicle_specs
        )
        result['analysis'] = seller_analysis
        
    else:
        # General analysis - use existing market analysis
        result['analysis'] = {
            'status': 'general',
            'message': 'General market analysis provided',
            'suggestion': 'For more specific advice, tell me if you\'re buying or selling'
        }
    
    return result

if __name__ == "__main__":
    # Test intent detection
    detector = IntentDetector()
    
    test_queries = [
        "כמה שווה הטויוטה קורולה 2019 שלי עם 60 אלף קמ?",
        "האם 85,000 שקל זה מחיר טוב לטויוטה קורולה 2019?",
        "ראיתי קורולה 2019 במחיר 90,000 ₪ - האם זה כדאי?",
        "רוצה לקנות קורולה 2019, מה המחיר בשוק?"
    ]
    
    print("🧪 Testing Intent Detection:")
    for query in test_queries:
        intent = detector.detect_intent(query)
        print(f"Query: {query}")
        print(f"Intent: {intent.intent_type}, Price: {intent.specific_price}")
        print(f"Context: {intent.context_clues}")
        print("---")