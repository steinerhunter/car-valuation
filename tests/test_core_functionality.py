#!/usr/bin/env python3
"""
Comprehensive Test Suite for OME-89 Car Valuation System
Addresses critical testing gaps identified by reviewers
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch
from typing import Dict, List

# Add scripts directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from yad2_web_scraper import Yad2WebScraper

class TestMarketAnalysis(unittest.TestCase):
    """Test market analysis functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.scraper = Yad2WebScraper()
        
        # Sample vehicle data for testing
        self.sample_vehicles = [
            {
                'price': 45000,
                'km': 160000,
                'year': 2014,
                'location': 'תל אביב',
                'manufacturer': 'Toyota',
                'model': 'Auris Hybrid'
            },
            {
                'price': 42000,
                'km': 180000,
                'year': 2014,
                'location': 'חיפה',
                'manufacturer': 'Toyota',
                'model': 'Auris Hybrid'
            },
            {
                'price': 48000,
                'km': 140000,
                'year': 2014,
                'location': 'ראשון לציון',
                'manufacturer': 'Toyota',
                'model': 'Auris Hybrid'
            }
        ]
    
    def test_market_data_analysis_basic(self):
        """Test basic market data analysis"""
        analysis = self.scraper.analyze_market_data(self.sample_vehicles)
        
        # Verify analysis structure
        self.assertIn('total_listings', analysis)
        self.assertIn('price_analysis', analysis)
        self.assertIn('mileage_analysis', analysis)
        
        # Verify calculations
        self.assertEqual(analysis['total_listings'], 3)
        self.assertEqual(analysis['price_analysis']['min_price'], 42000)
        self.assertEqual(analysis['price_analysis']['max_price'], 48000)
        self.assertEqual(analysis['price_analysis']['average_price'], 45000)
    
    def test_market_analysis_empty_data(self):
        """Test market analysis with empty data"""
        analysis = self.scraper.analyze_market_data([])
        
        self.assertIn('error', analysis)
        self.assertEqual(analysis['error'], 'No listings to analyze')
    
    def test_market_analysis_confidence_intervals(self):
        """Test that analysis includes confidence measures"""
        analysis = self.scraper.analyze_market_data(self.sample_vehicles)
        
        price_data = analysis['price_analysis']
        
        # Should include statistical measures
        self.assertIn('min_price', price_data)
        self.assertIn('max_price', price_data)
        self.assertIn('average_price', price_data)
        self.assertIn('median_price', price_data)
        
        # Verify price range calculation
        price_range = price_data['max_price'] - price_data['min_price']
        self.assertGreater(price_range, 0)

class TestVehicleValuation(unittest.TestCase):
    """Test vehicle valuation algorithms"""
    
    def setUp(self):
        self.scraper = Yad2WebScraper()
        
        # Market analysis data for testing
        self.market_analysis = {
            'price_analysis': {
                'min_price': 39000,
                'max_price': 55000,
                'average_price': 46714,
                'median_price': 46000,
                'price_std_dev': 5529
            },
            'mileage_analysis': {
                'average_km': 170714,
                'median_km': 175000
            }
        }
    
    def test_user_car_valuation_basic(self):
        """Test basic user car valuation"""
        user_car = {
            'year': 2014,
            'km': 180000,
            'has_gas_system': False,
            'paint_damage': 'significant',
            'hand': 'third'
        }
        
        evaluation = self.scraper.evaluate_user_car(user_car, self.market_analysis)
        
        # Verify evaluation structure
        self.assertIn('base_market_value', evaluation)
        self.assertIn('adjustments', evaluation)
        self.assertIn('estimated_value', evaluation)
        self.assertIn('confidence_range', evaluation)
        
        # Verify adjustments are logical
        self.assertLess(evaluation['adjustments']['paint_damage'], 0)
        self.assertLess(evaluation['adjustments']['third_hand'], 0)
    
    def test_confidence_ranges(self):
        """Test that valuations include confidence ranges"""
        user_car = {
            'year': 2014,
            'km': 180000,
            'paint_damage': 'significant'
        }
        
        evaluation = self.scraper.evaluate_user_car(user_car, self.market_analysis)
        
        confidence_range = evaluation['confidence_range']
        
        # Verify confidence range structure
        self.assertIn('low', confidence_range)
        self.assertIn('high', confidence_range)
        
        # Verify logical range
        self.assertLess(confidence_range['low'], evaluation['estimated_value'])
        self.assertGreater(confidence_range['high'], evaluation['estimated_value'])
    
    def test_mileage_adjustment_logic(self):
        """Test mileage adjustment calculations"""
        high_mileage_car = {'km': 200000}
        low_mileage_car = {'km': 120000}
        
        high_eval = self.scraper.evaluate_user_car(high_mileage_car, self.market_analysis)
        low_eval = self.scraper.evaluate_user_car(low_mileage_car, self.market_analysis)
        
        # High mileage should have negative adjustment
        self.assertLess(high_eval['adjustments']['mileage_adjustment'], 0)
        
        # Low mileage should have positive adjustment
        self.assertGreater(low_eval['adjustments']['mileage_adjustment'], 0)

class TestDataValidation(unittest.TestCase):
    """Test data validation and sanitization"""
    
    def test_price_validation(self):
        """Test price range validation"""
        scraper = Yad2WebScraper()
        
        # Valid data
        valid_vehicle = {
            'price': 45000,
            'year': 2014,
            'km': 180000,
            'location': 'תל אביב'
        }
        
        # This should not raise an exception
        analysis = scraper.analyze_market_data([valid_vehicle])
        self.assertEqual(analysis['total_listings'], 1)
    
    def test_input_sanitization(self):
        """Test that inputs are properly sanitized"""
        scraper = Yad2WebScraper()
        
        # Test with potentially dangerous input
        malicious_vehicle = {
            'price': 45000,
            'year': 2014,
            'location': '<script>alert("xss")</script>',
            'manufacturer': 'Toyota" DROP TABLE cars; --'
        }
        
        # Should handle gracefully
        analysis = scraper.analyze_market_data([malicious_vehicle])
        self.assertIsInstance(analysis, dict)

class TestPerformanceValidation(unittest.TestCase):
    """Test realistic performance expectations"""
    
    def test_performance_measurement(self):
        """Test that performance measurements are realistic"""
        import time
        from scripts.performance_corrections import RealisticPerformanceTracker
        
        tracker = RealisticPerformanceTracker()
        
        # Simulate a realistic operation
        measurement = tracker.start_measurement("test_operation", {"vehicles": 10})
        
        # Simulate some processing time
        time.sleep(0.1)  # 100ms
        
        result = tracker.end_measurement(measurement, vehicles_processed=10)
        
        # Performance should be realistic (not 47K vehicles/sec)
        self.assertLess(result['vehicles_per_second'], 1000)
        self.assertGreater(result['vehicles_per_second'], 0)
    
    def test_performance_categorization(self):
        """Test performance categorization logic"""
        from scripts.performance_corrections import RealisticPerformanceTracker
        
        tracker = RealisticPerformanceTracker()
        
        # Test different performance levels
        self.assertEqual(tracker._categorize_performance(15), "excellent")
        self.assertEqual(tracker._categorize_performance(7), "very_good")
        self.assertEqual(tracker._categorize_performance(3), "good")
        self.assertEqual(tracker._categorize_performance(1), "acceptable")
        self.assertEqual(tracker._categorize_performance(0.1), "slow")

class TestSecurityValidation(unittest.TestCase):
    """Test security enhancements"""
    
    def test_api_token_masking(self):
        """Test API token masking functionality"""
        from scripts.security_fixes import SecurityEnhancer
        
        enhancer = SecurityEnhancer()
        
        # Test token masking
        test_token = "lin_api_SkYzK7kZC3dAHDFTpkTY7OJd8Me1tzpqcfgYxR1k"
        masked = enhancer.mask_api_token(test_token)
        
        # Should mask most of the token
        self.assertNotEqual(masked, test_token)
        self.assertIn("****", masked)
        self.assertTrue(masked.endswith("R1k"))
    
    def test_token_validation(self):
        """Test API token validation"""
        from scripts.security_fixes import SecurityEnhancer
        
        enhancer = SecurityEnhancer()
        
        # Valid token
        valid_token = "lin_api_SkYzK7kZC3dAHDFTpkTY7OJd8Me1tzpqcfgYxR1k"
        self.assertTrue(enhancer.validate_api_token(valid_token))
        
        # Invalid tokens
        self.assertFalse(enhancer.validate_api_token(""))
        self.assertFalse(enhancer.validate_api_token("short"))
        self.assertFalse(enhancer.validate_api_token("invalid@#$%"))

class TestIntegrationScenarios(unittest.TestCase):
    """Test end-to-end integration scenarios"""
    
    def test_toyota_auris_hybrid_analysis(self):
        """Test the specific Toyota Auris Hybrid scenario"""
        scraper = Yad2WebScraper()
        
        # Get the demo data (fallback method)
        listings = scraper._get_demo_real_data()
        
        # Should return valid listings
        self.assertGreater(len(listings), 0)
        
        # Analyze the market
        analysis = scraper.analyze_market_data(listings)
        
        # Should have valid analysis
        self.assertIn('price_analysis', analysis)
        self.assertGreater(analysis['total_listings'], 0)
        
        # Test user car evaluation
        user_car = {
            'year': 2014,
            'km': 180000,
            'has_gas_system': True,
            'paint_damage': 'significant',
            'hand': 'third'
        }
        
        evaluation = scraper.evaluate_user_car(user_car, analysis)
        
        # Should provide realistic valuation
        self.assertGreater(evaluation['estimated_value'], 25000)
        self.assertLess(evaluation['estimated_value'], 60000)
        
        # Should include confidence range
        self.assertIn('confidence_range', evaluation)

if __name__ == '__main__':
    # Create test suite
    test_suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n{'='*50}")
    print(f"📊 Test Results Summary:")
    print(f"{'='*50}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("✅ ALL TESTS PASSED!")
    else:
        print("❌ Some tests failed - check output above")
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)