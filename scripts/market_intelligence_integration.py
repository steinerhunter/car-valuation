#!/usr/bin/env python3
"""
Market Intelligence Integration - OME-89
Integration layer between Intelligent Market Insights and existing Yad2 systems

This module connects the new intelligence engine with existing car valuation tools
"""

import json
import logging
from typing import Dict, List, Optional
from datetime import datetime
import sys
import os

# Add current directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from intelligent_market_insights import IntelligentMarketInsights, MarketIntelligence
    from yad2_link_analyzer import Yad2LinkAnalyzer, CarListingData
    from advanced_price_analysis import AdvancedPriceAnalyzer
except ImportError as e:
    print(f"⚠️ Import warning: {e}")
    print("🔧 Some modules may not be available - running in limited mode")

logger = logging.getLogger(__name__)

class MarketIntelligenceIntegration:
    """
    Integration layer that combines:
    1. Yad2 data collection and parsing
    2. Intelligent market insights analysis  
    3. Advanced price analysis
    4. Comprehensive reporting
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialize component systems
        try:
            self.market_insights = IntelligentMarketInsights()
            self.yad2_analyzer = Yad2LinkAnalyzer()
            self.price_analyzer = AdvancedPriceAnalyzer()
            
            self.logger.info("🔗 Market Intelligence Integration initialized successfully")
            self.components_available = True
            
        except Exception as e:
            self.logger.warning(f"⚠️ Some components not available: {e}")
            self.components_available = False
    
    def analyze_yad2_listings_with_intelligence(self, yad2_urls: List[str]) -> Dict:
        """
        Complete analysis pipeline:
        1. Extract data from Yad2 URLs
        2. Run market intelligence analysis
        3. Generate comprehensive insights
        4. Provide actionable recommendations
        """
        self.logger.info(f"🔍 Starting comprehensive analysis of {len(yad2_urls)} Yad2 listings")
        
        analysis_start = datetime.now()
        
        try:
            # Step 1: Extract listing data
            listing_data = self._extract_listing_data(yad2_urls)
            
            if not listing_data:
                return {
                    'success': False,
                    'error': 'Failed to extract any listing data',
                    'analysis_time': 0
                }
            
            # Step 2: Convert to market analysis format
            market_vehicles = self._convert_to_market_format(listing_data)
            
            # Step 3: Run intelligent market analysis
            market_intelligence = None
            if self.components_available and hasattr(self, 'market_insights'):
                market_intelligence = self.market_insights.analyze_market_intelligence(market_vehicles)
            
            # Step 4: Run advanced price analysis
            price_analysis = self._run_price_analysis(market_vehicles)
            
            # Step 5: Generate integrated report
            integrated_report = self._generate_integrated_report(
                listing_data, market_intelligence, price_analysis
            )
            
            analysis_duration = (datetime.now() - analysis_start).total_seconds()
            
            self.logger.info(f"✅ Comprehensive analysis completed in {analysis_duration:.2f}s")
            
            return {
                'success': True,
                'listings_analyzed': len(listing_data),
                'market_intelligence': market_intelligence,
                'price_analysis': price_analysis,
                'integrated_report': integrated_report,
                'analysis_time': analysis_duration,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Comprehensive analysis failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'analysis_time': (datetime.now() - analysis_start).total_seconds()
            }
    
    def _extract_listing_data(self, yad2_urls: List[str]) -> List[Dict]:
        """Extract structured data from Yad2 URLs"""
        self.logger.debug(f"📋 Extracting data from {len(yad2_urls)} URLs")
        
        listings = []
        
        for url in yad2_urls:
            try:
                if hasattr(self, 'yad2_analyzer'):
                    # Use real Yad2 analyzer if available
                    listing = self.yad2_analyzer.analyze_listing_url(url)
                    if listing:
                        listings.append(self._convert_listing_to_dict(listing))
                else:
                    # Fallback: simulate data extraction
                    listing = self._simulate_listing_data(url)
                    listings.append(listing)
                    
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to extract data from {url}: {e}")
        
        self.logger.debug(f"✅ Successfully extracted {len(listings)} listings")
        return listings
    
    def _convert_to_market_format(self, listings: List[Dict]) -> List[Dict]:
        """Convert listing data to format expected by market intelligence"""
        market_vehicles = []
        
        for listing in listings:
            vehicle = {
                'price': listing.get('price', 0),
                'year': listing.get('year', 0),
                'km': listing.get('km', 0),
                'manufacturer': listing.get('manufacturer', ''),
                'model': listing.get('model', ''),
                'city': listing.get('city', ''),
                'seller_type': listing.get('seller_type', ''),
                'listing_url': listing.get('url', ''),
                'listing_id': listing.get('listing_id', ''),
                'description': listing.get('description', ''),
                'features': listing.get('features', [])
            }
            market_vehicles.append(vehicle)
        
        return market_vehicles
    
    def _run_price_analysis(self, vehicles: List[Dict]) -> Optional[Dict]:
        """Run advanced price analysis if available"""
        if not hasattr(self, 'price_analyzer'):
            return None
        
        try:
            # Run mileage vs price analysis
            mileage_analysis = self.price_analyzer.analyze_price_vs_mileage(vehicles)
            
            # Additional analysis methods can be added here
            return {
                'mileage_analysis': mileage_analysis,
                'analysis_type': 'advanced_price_patterns'
            }
            
        except Exception as e:
            self.logger.warning(f"⚠️ Price analysis failed: {e}")
            return None
    
    def _generate_integrated_report(self, listings: List[Dict], 
                                  market_intelligence: Optional[Dict],
                                  price_analysis: Optional[Dict]) -> Dict:
        """Generate comprehensive integrated report"""
        
        report = {
            'summary': {
                'total_listings': len(listings),
                'analysis_components': []
            },
            'key_insights': [],
            'recommendations': [],
            'detailed_findings': {}
        }
        
        # Add listings summary
        if listings:
            prices = [l.get('price', 0) for l in listings if l.get('price')]
            if prices:
                report['summary'].update({
                    'price_range': f"₪{min(prices):,} - ₪{max(prices):,}",
                    'average_price': f"₪{sum(prices)/len(prices):,.0f}",
                    'total_listings': len(listings)
                })
        
        # Integrate market intelligence insights
        if market_intelligence:
            report['summary']['analysis_components'].append('Market Intelligence')
            
            # Add market insights
            if hasattr(market_intelligence, 'key_findings'):
                report['key_insights'].extend(market_intelligence.key_findings)
            
            if hasattr(market_intelligence, 'recommendations'):
                report['recommendations'].extend(market_intelligence.recommendations)
            
            # Add trend information
            if hasattr(market_intelligence, 'overall_trend'):
                trend = market_intelligence.overall_trend
                report['detailed_findings']['market_trend'] = {
                    'direction': trend.direction,
                    'strength': f"{trend.strength:.1%}",
                    'confidence': f"{trend.confidence:.1%}",
                    'analysis': trend.analysis
                }
        
        # Integrate price analysis
        if price_analysis:
            report['summary']['analysis_components'].append('Advanced Price Analysis')
            report['detailed_findings']['price_analysis'] = price_analysis
        
        # Add integration-specific insights
        integration_insights = self._generate_integration_insights(
            listings, market_intelligence, price_analysis
        )
        report['key_insights'].extend(integration_insights)
        
        return report
    
    def _generate_integration_insights(self, listings: List[Dict], 
                                     market_intelligence: Optional[Dict],
                                     price_analysis: Optional[Dict]) -> List[str]:
        """Generate insights from integrated analysis"""
        insights = []
        
        # Cross-analysis insights
        if listings and market_intelligence:
            insights.append(f"🔬 Integrated analysis of {len(listings)} listings with market intelligence")
        
        if price_analysis and market_intelligence:
            insights.append("📊 Combined price patterns with market trend analysis")
        
        # Data quality insights
        complete_listings = [l for l in listings if l.get('price') and l.get('year') and l.get('km')]
        if len(complete_listings) != len(listings):
            missing_data = len(listings) - len(complete_listings)
            insights.append(f"⚠️ {missing_data} listings have incomplete data - consider manual verification")
        
        return insights
    
    def _convert_listing_to_dict(self, listing: 'CarListingData') -> Dict:
        """Convert CarListingData object to dictionary"""
        return {
            'url': listing.url,
            'listing_id': listing.listing_id,
            'manufacturer': listing.manufacturer,
            'model': listing.model,
            'year': listing.year,
            'price': listing.price,
            'km': listing.km,
            'city': listing.city,
            'description': listing.description,
            'features': listing.features,
            'seller_type': listing.seller_type,
            'phone_number': listing.phone_number,
            'image_urls': listing.image_urls,
            'last_updated': listing.last_updated
        }
    
    def _simulate_listing_data(self, url: str) -> Dict:
        """Simulate listing data when real analyzer not available"""
        # Extract listing ID from URL for simulation
        import re
        listing_id_match = re.search(r'/(\d+)/?', url)
        listing_id = listing_id_match.group(1) if listing_id_match else "unknown"
        
        # Simulate realistic car data
        manufacturers = ["Toyota", "Honda", "Mazda", "Hyundai", "Kia", "Volkswagen"]
        models = ["Corolla", "Civic", "CX-5", "Tucson", "Sportage", "Golf"]
        years = [2018, 2019, 2020, 2021, 2022]
        
        import random
        random.seed(hash(url) % 10000)  # Consistent data for same URL
        
        return {
            'url': url,
            'listing_id': listing_id,
            'manufacturer': random.choice(manufacturers),
            'model': random.choice(models),
            'year': random.choice(years),
            'price': random.randint(70000, 150000),
            'km': random.randint(20000, 120000),
            'city': random.choice(["תל אביב", "חיפה", "ירושלים", "פתח תקווה"]),
            'description': f"רכב במצב טוב, שמור ומתוחזק",
            'features': ["מערכת ניווט", "חישני חניה"],
            'seller_type': random.choice(["private", "dealer"]),
            'phone_number': None,
            'image_urls': [],
            'last_updated': datetime.now().isoformat()
        }

def demo_integration():
    """Demo function to test the integrated analysis"""
    print("🔗 Market Intelligence Integration Demo")
    print("=" * 50)
    
    # Sample Yad2 URLs for testing
    sample_urls = [
        "https://www.yad2.co.il/vehicles/cars/toyota/corolla/123456",
        "https://www.yad2.co.il/vehicles/cars/honda/civic/234567", 
        "https://www.yad2.co.il/vehicles/cars/mazda/cx5/345678",
        "https://www.yad2.co.il/vehicles/cars/hyundai/tucson/456789"
    ]
    
    # Initialize integration system
    integration = MarketIntelligenceIntegration()
    
    # Run comprehensive analysis
    result = integration.analyze_yad2_listings_with_intelligence(sample_urls)
    
    # Display results
    if result['success']:
        print(f"\n✅ ANALYSIS SUCCESSFUL!")
        print(f"📊 Listings analyzed: {result['listings_analyzed']}")
        print(f"⏱️ Analysis time: {result['analysis_time']:.2f}s")
        
        report = result['integrated_report']
        print(f"\n📋 INTEGRATED REPORT:")
        print(f"Total listings: {report['summary']['total_listings']}")
        print(f"Components: {', '.join(report['summary']['analysis_components'])}")
        
        if report['key_insights']:
            print(f"\n🔑 KEY INSIGHTS:")
            for insight in report['key_insights'][:5]:  # Show first 5
                print(f"  • {insight}")
        
        if report['recommendations']:
            print(f"\n💡 RECOMMENDATIONS:")
            for rec in report['recommendations'][:3]:  # Show first 3
                print(f"  • {rec}")
                
        if 'market_trend' in report['detailed_findings']:
            trend = report['detailed_findings']['market_trend']
            print(f"\n📈 MARKET TREND:")
            print(f"  Direction: {trend['direction']}")
            print(f"  Strength: {trend['strength']}")
            print(f"  Analysis: {trend['analysis']}")
    else:
        print(f"\n❌ Analysis failed: {result['error']}")

if __name__ == "__main__":
    demo_integration()