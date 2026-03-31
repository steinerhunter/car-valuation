#!/usr/bin/env python3
"""
OME-95: Smart Alternative Suggestions Engine
===========================================

Intelligent car alternative recommendation system that suggests 3-5 similar vehicles
with better value propositions based on multi-factor analysis.

Author: Heinrich AI
Created: March 31, 2026
Build on: OME-89 enterprise-grade Yad2 analysis system (8.9/10 quality)
"""

import re
import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
import json

@dataclass
class VehicleProfile:
    """Complete vehicle profile for similarity matching"""
    manufacturer: str
    model: str
    year: int
    price: int
    km: int
    fuel_type: str
    hand: str
    location: str
    category: str = ""
    features_score: float = 0.0
    reliability_score: float = 0.0
    value_score: float = 0.0

@dataclass 
class AlternativeSuggestion:
    """Smart alternative recommendation with reasoning"""
    vehicle: VehicleProfile
    value_advantage: str
    price_difference: int
    confidence_score: float
    reasoning: str

class VehicleCategoryClassifier:
    """Classify vehicles into categories for similarity matching"""
    
    def __init__(self):
        # Israeli car market category mappings
        self.category_mappings = {
            # Compact Cars
            "compact": {
                "models": ["corolla", "civic", "elantra", "sentra", "focus", "golf", 
                          "i30", "cerato", "octavia", "megane", "308", "astra"],
                "size_class": "compact",
                "typical_price_range": (40000, 120000),
                "fuel_efficiency": "good"
            },
            
            # Sedans  
            "sedan": {
                "models": ["camry", "accord", "sonata", "altima", "mondeo", "passat",
                          "superb", "laguna", "508", "insignia", "mazda6"],
                "size_class": "medium", 
                "typical_price_range": (60000, 180000),
                "fuel_efficiency": "moderate"
            },
            
            # SUVs
            "suv": {
                "models": ["rav4", "crv", "santa_fe", "rogue", "escape", "tiguan",
                          "kodiaq", "kadjar", "3008", "mokka", "cx5"],
                "size_class": "large",
                "typical_price_range": (80000, 250000), 
                "fuel_efficiency": "low"
            },
            
            # Luxury
            "luxury": {
                "models": ["lexus", "acura", "infiniti", "bmw", "mercedes", "audi",
                          "volvo", "cadillac", "lincoln", "genesis"],
                "size_class": "premium",
                "typical_price_range": (100000, 500000),
                "fuel_efficiency": "varies"
            },
            
            # Economy
            "economy": {
                "models": ["yaris", "micra", "fiesta", "polo", "ibiza", "fabia",
                          "clio", "peugeot_208", "spark", "rio"],
                "size_class": "small",
                "typical_price_range": (25000, 80000),
                "fuel_efficiency": "excellent"
            }
        }
        
    def classify_vehicle(self, manufacturer: str, model: str, price: int) -> str:
        """Classify vehicle into category based on manufacturer, model, and price"""
        manufacturer_lower = manufacturer.lower()
        model_lower = model.lower().replace(" ", "_")
        
        # Check luxury brands first
        luxury_brands = ["lexus", "bmw", "mercedes", "audi", "volvo", "infiniti", "acura"]
        if manufacturer_lower in luxury_brands:
            return "luxury"
        
        # Check model matches
        for category, info in self.category_mappings.items():
            if any(model_name in model_lower for model_name in info["models"]):
                return category
                
        # Fallback to price-based classification
        if price < 80000:
            return "economy"
        elif price < 120000:
            return "compact"
        elif price < 180000:
            return "sedan"
        elif price < 250000:
            return "suv"
        else:
            return "luxury"

class ManufacturerReliabilityDatabase:
    """Israeli market manufacturer reliability and reputation scores"""
    
    def __init__(self):
        # Based on Israeli automotive market reputation and service network
        self.reliability_scores = {
            # Japanese (Highest reliability)
            "toyota": 9.2, "honda": 9.0, "mazda": 8.7, "nissan": 8.5,
            "lexus": 9.4, "acura": 8.8, "infiniti": 8.3,
            
            # Korean (Good value and reliability)
            "hyundai": 8.2, "kia": 8.0, "genesis": 8.4,
            
            # German (Premium but higher maintenance)
            "bmw": 7.8, "mercedes": 7.9, "audi": 7.7, "volkswagen": 7.5,
            "porsche": 8.0, "mini": 7.2,
            
            # American (Mixed reputation in Israel)
            "ford": 7.3, "chevrolet": 7.0, "jeep": 6.8, "chrysler": 6.5,
            "cadillac": 7.4, "buick": 7.1,
            
            # French (Budget but maintenance concerns)
            "renault": 6.9, "peugeot": 6.7, "citroen": 6.5, "ds": 6.8,
            
            # Italian (Style but reliability concerns)
            "fiat": 6.2, "alfa_romeo": 6.4, "lancia": 6.0,
            
            # Other European
            "volvo": 8.1, "skoda": 7.8, "seat": 7.4, "opel": 7.1
        }
        
        # Israeli market specific factors
        self.service_network_scores = {
            "toyota": 9.5, "hyundai": 9.2, "nissan": 9.0, "kia": 8.8,
            "ford": 8.5, "volkswagen": 8.3, "honda": 8.0, "mazda": 7.8,
            "renault": 8.7, "peugeot": 8.2, "citroen": 7.9
        }
        
    def get_reliability_score(self, manufacturer: str) -> float:
        """Get reliability score for manufacturer (0-10 scale)"""
        manufacturer_clean = manufacturer.lower().replace(" ", "_")
        return self.reliability_scores.get(manufacturer_clean, 7.0)  # Default neutral
        
    def get_service_score(self, manufacturer: str) -> float:
        """Get service network accessibility score in Israel"""
        manufacturer_clean = manufacturer.lower().replace(" ", "_")
        return self.service_network_scores.get(manufacturer_clean, 7.0)

class ValuePropositionAnalyzer:
    """Analyze and compare value propositions between vehicles"""
    
    def __init__(self):
        self.reliability_db = ManufacturerReliabilityDatabase()
        
        # Israeli market value factors
        self.value_weights = {
            "price_competitiveness": 0.30,  # Price vs market average
            "reliability_reputation": 0.25,  # Brand reliability
            "fuel_efficiency": 0.20,        # Operating costs  
            "resale_value": 0.15,          # Depreciation resistance
            "service_network": 0.10         # Maintenance accessibility
        }
        
        # Fuel efficiency estimates (km/liter) by category
        self.fuel_efficiency_by_category = {
            "economy": 18.0, "compact": 16.0, "sedan": 14.0, 
            "suv": 12.0, "luxury": 11.0
        }
        
        # Resale value retention (% after 5 years) by manufacturer
        self.resale_value_retention = {
            "toyota": 0.65, "honda": 0.62, "lexus": 0.68, "mazda": 0.58,
            "hyundai": 0.55, "kia": 0.52, "nissan": 0.54,
            "bmw": 0.50, "mercedes": 0.52, "audi": 0.48, "volkswagen": 0.45,
            "ford": 0.42, "renault": 0.38, "peugeot": 0.35
        }
    
    def calculate_value_score(self, vehicle: VehicleProfile, market_avg_price: float) -> float:
        """Calculate comprehensive value score (0-10 scale)"""
        
        # Price competitiveness (lower price = higher score)
        price_ratio = vehicle.price / market_avg_price if market_avg_price > 0 else 1.0
        price_score = max(0, 10 - (price_ratio - 0.8) * 20)  # Best score at 80% of market price
        
        # Reliability score
        reliability_score = self.reliability_db.get_reliability_score(vehicle.manufacturer)
        
        # Service network score
        service_score = self.reliability_db.get_service_score(vehicle.manufacturer)
        
        # Fuel efficiency score (based on category)
        fuel_efficiency = self.fuel_efficiency_by_category.get(vehicle.category, 14.0)
        fuel_score = min(10, fuel_efficiency * 0.5)  # Scale to 0-10
        
        # Resale value score
        manufacturer_clean = vehicle.manufacturer.lower()
        resale_retention = self.resale_value_retention.get(manufacturer_clean, 0.45)
        resale_score = resale_retention * 20  # Scale to 0-10
        
        # Weighted final score
        final_score = (
            price_score * self.value_weights["price_competitiveness"] +
            reliability_score * self.value_weights["reliability_reputation"] +
            fuel_score * self.value_weights["fuel_efficiency"] +
            resale_score * self.value_weights["resale_value"] + 
            service_score * self.value_weights["service_network"]
        )
        
        return round(final_score, 1)
        
    def compare_value_propositions(self, target_vehicle: VehicleProfile, 
                                 alternative: VehicleProfile) -> Tuple[float, str]:
        """Compare two vehicles and return advantage score and reasoning"""
        
        target_score = target_vehicle.value_score
        alt_score = alternative.value_score
        
        advantage = alt_score - target_score
        
        # Generate reasoning based on key differences
        reasons = []
        
        # Price advantage
        price_diff = target_vehicle.price - alternative.price
        if price_diff > 5000:
            reasons.append(f"חוסך {price_diff:,} ₪")
        elif price_diff < -5000:
            reasons.append(f"יותר יקר ב-{abs(price_diff):,} ₪ אבל שווה את זה")
            
        # Reliability advantage
        target_rel = self.reliability_db.get_reliability_score(target_vehicle.manufacturer)
        alt_rel = self.reliability_db.get_reliability_score(alternative.manufacturer)
        if alt_rel > target_rel + 0.5:
            reasons.append("אמינות גבוהה יותר")
            
        # Year advantage  
        year_diff = alternative.year - target_vehicle.year
        if year_diff > 0:
            reasons.append(f"חדש יותר ב-{year_diff} שנים")
        elif year_diff < 0:
            reasons.append(f"ישן יותר אבל מוכח")
            
        # Mileage advantage
        km_diff = target_vehicle.km - alternative.km
        if km_diff > 20000:
            reasons.append(f"פחות קילומטרים ב-{km_diff:,}")
            
        reasoning = " | ".join(reasons) if reasons else "יחס מחיר/איכות מעולה"
        
        return advantage, reasoning

class SmartAlternativesEngine:
    """Main engine for intelligent car alternative suggestions"""
    
    def __init__(self):
        self.classifier = VehicleCategoryClassifier()
        self.value_analyzer = ValuePropositionAnalyzer()
        self.reliability_db = ManufacturerReliabilityDatabase()
        
    def find_alternatives(self, target_vehicle: VehicleProfile, 
                         market_vehicles: List[VehicleProfile],
                         max_alternatives: int = 5) -> List[AlternativeSuggestion]:
        """Find and rank smart alternative suggestions"""
        
        # Step 1: Classify target vehicle
        target_vehicle.category = self.classifier.classify_vehicle(
            target_vehicle.manufacturer, target_vehicle.model, target_vehicle.price
        )
        
        # Step 2: Calculate market average price for category
        category_vehicles = [v for v in market_vehicles if 
                           self.classifier.classify_vehicle(v.manufacturer, v.model, v.price) == target_vehicle.category]
        market_avg_price = sum(v.price for v in category_vehicles) / len(category_vehicles) if category_vehicles else target_vehicle.price
        
        # Step 3: Calculate target vehicle value score
        target_vehicle.value_score = self.value_analyzer.calculate_value_score(target_vehicle, market_avg_price)
        
        # Step 4: Find similar vehicles (same category, similar price range, similar year)
        candidates = []
        price_range = target_vehicle.price * 0.25  # ±25% price range
        year_range = 3  # ±3 years
        
        for vehicle in market_vehicles:
            # Skip if same exact vehicle
            if (vehicle.manufacturer == target_vehicle.manufacturer and 
                vehicle.model == target_vehicle.model and
                vehicle.year == target_vehicle.year and
                abs(vehicle.price - target_vehicle.price) < 5000):
                continue
                
            vehicle.category = self.classifier.classify_vehicle(
                vehicle.manufacturer, vehicle.model, vehicle.price
            )
            
            # Must be same category
            if vehicle.category != target_vehicle.category:
                continue
                
            # Price range filter
            if abs(vehicle.price - target_vehicle.price) > price_range:
                continue
                
            # Year range filter  
            if abs(vehicle.year - target_vehicle.year) > year_range:
                continue
                
            # Calculate value score
            vehicle.value_score = self.value_analyzer.calculate_value_score(vehicle, market_avg_price)
            
            # Only suggest if better value (higher score)
            if vehicle.value_score > target_vehicle.value_score:
                candidates.append(vehicle)
        
        # Step 5: Create suggestions with reasoning
        suggestions = []
        for candidate in candidates:
            advantage, reasoning = self.value_analyzer.compare_value_propositions(
                target_vehicle, candidate
            )
            
            # Confidence based on advantage magnitude and data quality
            confidence = min(0.95, 0.6 + (advantage * 0.1))
            
            suggestion = AlternativeSuggestion(
                vehicle=candidate,
                value_advantage=f"+{advantage:.1f} ערך",
                price_difference=candidate.price - target_vehicle.price,
                confidence_score=confidence,
                reasoning=reasoning
            )
            suggestions.append(suggestion)
            
        # Step 6: Rank by value advantage
        suggestions.sort(key=lambda x: x.vehicle.value_score, reverse=True)
        
        return suggestions[:max_alternatives]
    
    def format_alternatives_response(self, target_vehicle: VehicleProfile,
                                   suggestions: List[AlternativeSuggestion],
                                   language: str = "hebrew") -> str:
        """Format alternative suggestions into natural language response"""
        
        if not suggestions:
            return "לא מצאתי אלטרנטיבות טובות יותר ברגע זה. הרכב שבחרת הוא בחירה סבירה למחיר."
        
        intro = f"הרכב שווה בערך {target_vehicle.price:,} ₪, אבל כדאי לשקול גם:"
        
        alternatives = []
        for i, suggestion in enumerate(suggestions, 1):
            vehicle = suggestion.vehicle
            price_indicator = "יותר זול" if suggestion.price_difference < 0 else "יותר יקר"
            
            alt_text = (f"{i}. **{vehicle.manufacturer} {vehicle.model} {vehicle.year}** "
                       f"({vehicle.price:,} ₪, {price_indicator}) - {suggestion.reasoning}")
            alternatives.append(alt_text)
            
        return intro + "\n\n" + "\n".join(alternatives)

# Test and validation functions
def test_smart_alternatives_engine():
    """Test the smart alternatives engine with sample data"""
    engine = SmartAlternativesEngine()
    
    # Target vehicle: Toyota Corolla 2019, 85K
    target = VehicleProfile(
        manufacturer="Toyota",
        model="Corolla", 
        year=2019,
        price=85000,
        km=80000,
        fuel_type="בנזין",
        hand="יד שנייה",
        location="תל אביב"
    )
    
    # Market alternatives
    market = [
        VehicleProfile("Honda", "Civic", 2019, 79000, 75000, "בנזין", "יד שנייה", "חיפה"),
        VehicleProfile("Nissan", "Sentra", 2020, 77000, 60000, "בנזין", "יד שנייה", "ירושלים"),
        VehicleProfile("Hyundai", "Elantra", 2019, 81000, 85000, "בנזין", "יד שלישית", "תל אביב"),
        VehicleProfile("Mazda", "3", 2018, 72000, 95000, "בנזין", "יד שנייה", "באר שבע"),
        VehicleProfile("Kia", "Cerato", 2020, 74000, 55000, "בנזין", "יד ראשונה", "נתניה")
    ]
    
    # Find alternatives
    suggestions = engine.find_alternatives(target, market, max_alternatives=3)
    
    # Format response
    response = engine.format_alternatives_response(target, suggestions)
    
    print("🧪 SMART ALTERNATIVES ENGINE TEST")
    print("=================================")
    print(f"Target Vehicle: {target.manufacturer} {target.model} {target.year} - {target.price:,} ₪")
    print(f"Target Value Score: {target.value_score:.1f}/10")
    print()
    print("Generated Response:")
    print(response)
    print()
    print("Detailed Suggestions:")
    for i, suggestion in enumerate(suggestions, 1):
        vehicle = suggestion.vehicle  
        print(f"{i}. {vehicle.manufacturer} {vehicle.model} {vehicle.year}")
        print(f"   Price: {vehicle.price:,} ₪ (difference: {suggestion.price_difference:+,} ₪)")
        print(f"   Value Score: {vehicle.value_score:.1f}/10 ({suggestion.value_advantage})")
        print(f"   Confidence: {suggestion.confidence_score:.1%}")
        print(f"   Reasoning: {suggestion.reasoning}")
        print()

if __name__ == "__main__":
    test_smart_alternatives_engine()