#!/usr/bin/env python3
"""
Advanced Price Pattern Analysis for Car Valuation
Part of OME-84: Smart Yad2 Listing Analysis
"""

import statistics
import re
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import math

class AdvancedPriceAnalyzer:
    """Advanced analysis of price patterns in Yad2 listings"""
    
    def __init__(self):
        self.depreciation_threshold = 0.05  # 5% correlation threshold
        
    def analyze_price_vs_mileage(self, vehicles: List[Dict]) -> Dict:
        """
        Analyze correlation between mileage and price
        Returns depreciation rate and insights
        """
        if len(vehicles) < 4:
            return {
                'status': 'insufficient_data',
                'message': 'Need at least 4 vehicles for mileage analysis'
            }
        
        # Filter vehicles with valid mileage data
        valid_vehicles = [
            v for v in vehicles 
            if v.get('km') and isinstance(v.get('km'), (int, float)) 
            and v.get('price') and isinstance(v.get('price'), (int, float))
            and v.get('km') > 0
        ]
        
        if len(valid_vehicles) < 3:
            return {
                'status': 'insufficient_mileage_data',
                'message': 'Not enough vehicles with mileage data for analysis'
            }
        
        # Calculate correlation coefficient
        km_values = [v['km'] for v in valid_vehicles]
        price_values = [v['price'] for v in valid_vehicles]
        
        correlation = self._calculate_correlation(km_values, price_values)
        
        # Calculate depreciation per kilometer
        if abs(correlation) > self.depreciation_threshold:
            depreciation_per_km = self._calculate_depreciation_rate(km_values, price_values)
        else:
            depreciation_per_km = 0
        
        # Find mileage brackets
        mileage_brackets = self._analyze_mileage_brackets(valid_vehicles)
        
        return {
            'status': 'success',
            'correlation_coefficient': correlation,
            'depreciation_per_km': depreciation_per_km,
            'mileage_brackets': mileage_brackets,
            'sample_size': len(valid_vehicles),
            'insights': self._generate_mileage_insights(correlation, depreciation_per_km, mileage_brackets)
        }
    
    def analyze_geographic_impact(self, vehicles: List[Dict]) -> Dict:
        """
        Analyze price differences by geographic location
        """
        if len(vehicles) < 5:
            return {
                'status': 'insufficient_data',
                'message': 'Need at least 5 vehicles for geographic analysis'
            }
        
        # Group by city/region
        city_groups = {}
        for vehicle in vehicles:
            city = self._normalize_city_name(vehicle.get('cityEn', vehicle.get('city', 'Unknown')))
            if city not in city_groups:
                city_groups[city] = []
            city_groups[city].append(vehicle['price'])
        
        # Filter cities with at least 2 listings
        significant_cities = {
            city: prices for city, prices in city_groups.items()
            if len(prices) >= 2
        }
        
        if len(significant_cities) < 2:
            return {
                'status': 'insufficient_geographic_spread',
                'message': 'Not enough geographic diversity for location analysis'
            }
        
        # Calculate city statistics
        city_stats = {}
        overall_median = statistics.median([v['price'] for v in vehicles])
        
        for city, prices in significant_cities.items():
            city_median = statistics.median(prices)
            premium_percentage = ((city_median - overall_median) / overall_median) * 100
            
            city_stats[city] = {
                'median_price': int(city_median),
                'listing_count': len(prices),
                'premium_percentage': round(premium_percentage, 1),
                'price_range': f"{min(prices):,} - {max(prices):,}"
            }
        
        # Sort by premium (highest to lowest)
        sorted_cities = sorted(
            city_stats.items(), 
            key=lambda x: x[1]['premium_percentage'], 
            reverse=True
        )
        
        return {
            'status': 'success',
            'overall_median': int(overall_median),
            'city_analysis': dict(sorted_cities),
            'insights': self._generate_geographic_insights(sorted_cities, overall_median)
        }
    
    def analyze_listing_content(self, vehicles: List[Dict]) -> Dict:
        """
        Analyze listing descriptions for premium features and keywords
        """
        if not vehicles:
            return {
                'status': 'no_data',
                'message': 'No vehicles to analyze'
            }
        
        # Keywords that typically indicate premium pricing
        premium_keywords = [
            # Hebrew keywords
            'שמורה', 'יד ראשונה', 'יד שנייה', 'פרטי', 'מטופלת', 'כחדשה',
            'יד 1', 'יד 2', 'שירות', 'מוסך', 'טסט', 'בדיקה', 'אמין',
            'אוטומט', 'שמש', 'מזגן', 'עור', 'ספורט', 'פרימיום',
            
            # English keywords
            'maintained', 'serviced', 'excellent', 'perfect', 'premium',
            'private', 'first hand', 'second hand', 'automatic', 'leather',
            'sunroof', 'sport', 'luxury', 'garage kept'
        ]
        
        discount_keywords = [
            # Hebrew keywords
            'תיקונים', 'פגיעות', 'תאונות', 'צבע', 'זקוק', 'דורש',
            'מכניקה', 'חשמל', 'מנוע', 'תיבה', 'בעיות',
            
            # English keywords  
            'repairs', 'damage', 'accident', 'needs work', 'mechanical',
            'issues', 'problems', 'bodywork', 'engine', 'transmission'
        ]
        
        listings_with_content = [
            v for v in vehicles 
            if v.get('description') or v.get('title')
        ]
        
        if len(listings_with_content) < 3:
            return {
                'status': 'insufficient_content',
                'message': 'Not enough listings with description content'
            }
        
        # Analyze content
        premium_listings = []
        discount_listings = []
        neutral_listings = []
        
        for vehicle in listings_with_content:
            content = f"{vehicle.get('title', '')} {vehicle.get('description', '')}".lower()
            
            premium_score = sum(1 for keyword in premium_keywords if keyword.lower() in content)
            discount_score = sum(1 for keyword in discount_keywords if keyword.lower() in content)
            
            listing_data = {
                'price': vehicle['price'],
                'premium_score': premium_score,
                'discount_score': discount_score,
                'content_snippet': content[:100] + '...' if len(content) > 100 else content
            }
            
            if premium_score > discount_score and premium_score > 0:
                premium_listings.append(listing_data)
            elif discount_score > premium_score and discount_score > 0:
                discount_listings.append(listing_data)
            else:
                neutral_listings.append(listing_data)
        
        # Calculate price differences
        all_prices = [v['price'] for v in listings_with_content]
        overall_median = statistics.median(all_prices)
        
        analysis = {
            'status': 'success',
            'overall_median': int(overall_median),
            'premium_listings': len(premium_listings),
            'discount_listings': len(discount_listings),
            'neutral_listings': len(neutral_listings)
        }
        
        if premium_listings:
            premium_median = statistics.median([l['price'] for l in premium_listings])
            analysis['premium_median'] = int(premium_median)
            analysis['premium_advantage'] = round(((premium_median - overall_median) / overall_median) * 100, 1)
        
        if discount_listings:
            discount_median = statistics.median([l['price'] for l in discount_listings])
            analysis['discount_median'] = int(discount_median)
            analysis['discount_impact'] = round(((overall_median - discount_median) / overall_median) * 100, 1)
        
        analysis['insights'] = self._generate_content_insights(analysis)
        
        return analysis
    
    def _calculate_correlation(self, x_values: List[float], y_values: List[float]) -> float:
        """Calculate Pearson correlation coefficient"""
        if len(x_values) != len(y_values) or len(x_values) < 2:
            return 0.0
        
        n = len(x_values)
        sum_x = sum(x_values)
        sum_y = sum(y_values)
        sum_xy = sum(x * y for x, y in zip(x_values, y_values))
        sum_x2 = sum(x * x for x in x_values)
        sum_y2 = sum(y * y for y in y_values)
        
        numerator = n * sum_xy - sum_x * sum_y
        denominator = math.sqrt((n * sum_x2 - sum_x * sum_x) * (n * sum_y2 - sum_y * sum_y))
        
        if denominator == 0:
            return 0.0
        
        return numerator / denominator
    
    def _calculate_depreciation_rate(self, km_values: List[float], price_values: List[float]) -> float:
        """Calculate depreciation per kilometer using linear regression"""
        n = len(km_values)
        if n < 2:
            return 0
        
        sum_x = sum(km_values)
        sum_y = sum(price_values)
        sum_xy = sum(x * y for x, y in zip(km_values, price_values))
        sum_x2 = sum(x * x for x in km_values)
        
        # Linear regression: y = mx + b, we want m (slope)
        denominator = n * sum_x2 - sum_x * sum_x
        if denominator == 0:
            return 0
            
        slope = (n * sum_xy - sum_x * sum_y) / denominator
        return slope  # This is depreciation per km (negative value expected)
    
    def _analyze_mileage_brackets(self, vehicles: List[Dict]) -> Dict:
        """Analyze price patterns across different mileage brackets"""
        if len(vehicles) < 6:
            return {}
        
        # Sort by mileage
        sorted_vehicles = sorted(vehicles, key=lambda x: x['km'])
        
        # Create brackets
        brackets = {
            'low_mileage': sorted_vehicles[:len(sorted_vehicles)//3],      # Bottom third
            'medium_mileage': sorted_vehicles[len(sorted_vehicles)//3:2*len(sorted_vehicles)//3],  # Middle third
            'high_mileage': sorted_vehicles[2*len(sorted_vehicles)//3:]   # Top third
        }
        
        bracket_stats = {}
        for bracket_name, bracket_vehicles in brackets.items():
            if bracket_vehicles:
                prices = [v['price'] for v in bracket_vehicles]
                mileages = [v['km'] for v in bracket_vehicles]
                
                bracket_stats[bracket_name] = {
                    'avg_price': int(statistics.mean(prices)),
                    'median_price': int(statistics.median(prices)),
                    'avg_mileage': int(statistics.mean(mileages)),
                    'mileage_range': f"{min(mileages):,} - {max(mileages):,}",
                    'count': len(bracket_vehicles)
                }
        
        return bracket_stats
    
    def _normalize_city_name(self, city: str) -> str:
        """Normalize city names for consistent grouping"""
        if not city:
            return 'Unknown'
        city = str(city).strip().title()
        
        # Common variations
        city_mapping = {
            'Petach Tikva': 'Petah Tikva',
            'Petach Tikvah': 'Petah Tikva',
            'Rishon Lezion': 'Rishon LeZion',
            'Rishon Le-Zion': 'Rishon LeZion',
            'Be\'er Sheva': 'Beer Sheva',
            'Beer Sheba': 'Beer Sheva',
            'Ramat-Gan': 'Ramat Gan',
            'Ra\'anana': 'Raanana',
            'Kfar-Saba': 'Kfar Saba',
            'Unknown': 'Unknown'
        }
        
        return city_mapping.get(city, city)
    
    def _generate_mileage_insights(self, correlation: float, depreciation_rate: float, brackets: Dict) -> List[str]:
        """Generate insights about mileage vs price relationship"""
        insights = []
        
        if abs(correlation) > 0.7:
            if correlation < 0:
                insights.append(f"Strong negative correlation ({correlation:.2f}) - higher mileage significantly lowers price")
                if depreciation_rate < 0:
                    insights.append(f"Depreciation rate: {abs(depreciation_rate):.2f} ILS per kilometer")
            else:
                insights.append(f"Unusual positive correlation ({correlation:.2f}) - investigate data quality")
        elif abs(correlation) > 0.3:
            insights.append(f"Moderate correlation ({correlation:.2f}) - mileage has some impact on pricing")
        else:
            insights.append(f"Weak correlation ({correlation:.2f}) - mileage doesn't strongly influence price in this sample")
        
        # Bracket insights
        if 'low_mileage' in brackets and 'high_mileage' in brackets:
            low_price = brackets['low_mileage']['median_price']
            high_price = brackets['high_mileage']['median_price']
            price_diff = low_price - high_price
            percentage_diff = (price_diff / high_price) * 100
            
            if price_diff > 5000:  # Significant difference
                insights.append(f"Low mileage vehicles command {price_diff:,} ILS premium ({percentage_diff:.1f}% more)")
        
        return insights
    
    def _generate_geographic_insights(self, sorted_cities: List[Tuple], overall_median: float) -> List[str]:
        """Generate insights about geographic price variations"""
        insights = []
        
        if len(sorted_cities) < 2:
            return insights
        
        highest_city, highest_data = sorted_cities[0]
        lowest_city, lowest_data = sorted_cities[-1]
        
        premium_diff = highest_data['premium_percentage'] - lowest_data['premium_percentage']
        
        if premium_diff > 15:  # Significant geographic spread
            insights.append(f"{highest_city} commands {highest_data['premium_percentage']:+.1f}% premium vs market")
            insights.append(f"{lowest_city} offers {abs(lowest_data['premium_percentage']):.1f}% discount vs market")
            insights.append(f"Geographic spread: {premium_diff:.1f}% price difference between regions")
        elif premium_diff > 8:
            insights.append(f"Moderate geographic price variation: {premium_diff:.1f}% spread between regions")
        else:
            insights.append("Minimal geographic price variation - location has little impact")
        
        # Find cities with most listings
        cities_by_volume = sorted(sorted_cities, key=lambda x: x[1]['listing_count'], reverse=True)
        if cities_by_volume:
            top_city, top_data = cities_by_volume[0]
            insights.append(f"Most active market: {top_city} ({top_data['listing_count']} listings)")
        
        return insights
    
    def _generate_content_insights(self, analysis: Dict) -> List[str]:
        """Generate insights about listing content impact"""
        insights = []
        
        total_analyzed = analysis['premium_listings'] + analysis['discount_listings'] + analysis['neutral_listings']
        
        if analysis.get('premium_advantage'):
            insights.append(f"Premium keywords boost price by {analysis['premium_advantage']:+.1f}%")
        
        if analysis.get('discount_impact'):
            insights.append(f"Condition issues reduce price by {analysis['discount_impact']:.1f}%")
        
        premium_ratio = (analysis['premium_listings'] / total_analyzed) * 100
        discount_ratio = (analysis['discount_listings'] / total_analyzed) * 100
        
        insights.append(f"Market composition: {premium_ratio:.0f}% premium, {discount_ratio:.0f}% discounted listings")
        
        if premium_ratio > 40:
            insights.append("High-quality market - many well-maintained vehicles available")
        elif discount_ratio > 30:
            insights.append("Caution advised - significant portion of listings mention issues")
        
        return insights

def enhance_market_analysis(vehicles: List[Dict]) -> Dict:
    """
    Main function to run advanced price analysis
    Enhances the basic market analysis with sophisticated insights
    """
    analyzer = AdvancedPriceAnalyzer()
    
    enhanced_analysis = {
        'mileage_analysis': analyzer.analyze_price_vs_mileage(vehicles),
        'geographic_analysis': analyzer.analyze_geographic_impact(vehicles),
        'content_analysis': analyzer.analyze_listing_content(vehicles),
        'analysis_timestamp': datetime.now().isoformat(),
        'sample_size': len(vehicles)
    }
    
    return enhanced_analysis

if __name__ == "__main__":
    # Test the advanced analysis
    sample_vehicles = [
        {'price': 85000, 'year': 2019, 'km': 45000, 'cityEn': 'Tel Aviv', 'description': 'שמורה מטופלת יד שנייה'},
        {'price': 92000, 'year': 2019, 'km': 38000, 'cityEn': 'Ramat Gan', 'description': 'יד ראשונה אוטומט מזגן'},
        {'price': 88000, 'year': 2019, 'km': 52000, 'cityEn': 'Petah Tikva', 'description': 'מצב טוב זקוק תיקונים קלים'},
        {'price': 78000, 'year': 2019, 'km': 67000, 'cityEn': 'Ashdod', 'description': 'בעיות מכניקה דורש השקעה'},
        {'price': 90000, 'year': 2019, 'km': 41000, 'cityEn': 'Herzliya', 'description': 'פרטי מוסך אמין בדיקות'},
    ]
    
    result = enhance_market_analysis(sample_vehicles)
    print("Enhanced Analysis Result:")
    for key, value in result.items():
        print(f"{key}: {value}")