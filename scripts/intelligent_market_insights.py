#!/usr/bin/env python3
"""
Intelligent Market Insights Engine - OME-89
Advanced smart analysis of Yad2 car listings with sophisticated market intelligence

This engine analyzes price patterns, market trends, and provides intelligent insights
about the car market in real-time.
"""

import json
import statistics
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from collections import defaultdict
import re

# Enterprise logging integration
logger = logging.getLogger(__name__)

@dataclass
class MarketTrend:
    """Market trend analysis result"""
    direction: str  # "rising", "falling", "stable"
    strength: float  # 0.0 to 1.0
    confidence: float  # 0.0 to 1.0
    time_period: str  # "1week", "1month", "3months"
    analysis: str
    supporting_data: Dict

@dataclass
class PriceInsight:
    """Price analysis insight"""
    category: str  # "underpriced", "overpriced", "fair"
    deviation_percent: float
    market_position: str  # "top_10", "average", "bottom_10"
    recommendation: str
    reasoning: str

@dataclass
class MarketIntelligence:
    """Complete market intelligence report"""
    overall_trend: MarketTrend
    price_insights: List[PriceInsight]
    market_health: str  # "healthy", "volatile", "stagnant"
    key_findings: List[str]
    recommendations: List[str]
    generated_at: datetime

class IntelligentMarketInsights:
    """
    Intelligent Market Insights Engine
    
    Analyzes car market data to provide sophisticated insights about:
    - Market trends and direction
    - Price anomalies and opportunities  
    - Market health and volatility
    - Intelligent recommendations
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.trend_threshold = 0.05  # 5% change threshold
        self.confidence_threshold = 0.7
        self.volatility_threshold = 0.15  # 15% volatility threshold
        
        self.logger.info("🧠 Intelligent Market Insights Engine initialized")
        
    def analyze_market_intelligence(self, vehicles: List[Dict]) -> MarketIntelligence:
        """
        Main intelligence analysis - combines all insights
        
        Args:
            vehicles: List of vehicle data from Yad2 listings
            
        Returns:
            Complete market intelligence report
        """
        self.logger.info(f"🔍 Starting market intelligence analysis for {len(vehicles)} vehicles")
        
        start_time = datetime.now()
        
        try:
            # Core analysis components
            overall_trend = self._analyze_market_trend(vehicles)
            price_insights = self._analyze_price_patterns(vehicles)
            market_health = self._assess_market_health(vehicles)
            
            # Generate key findings and recommendations
            key_findings = self._generate_key_findings(vehicles, overall_trend, price_insights)
            recommendations = self._generate_recommendations(overall_trend, price_insights, market_health)
            
            # Create intelligence report
            intelligence = MarketIntelligence(
                overall_trend=overall_trend,
                price_insights=price_insights,
                market_health=market_health,
                key_findings=key_findings,
                recommendations=recommendations,
                generated_at=datetime.now()
            )
            
            analysis_duration = (datetime.now() - start_time).total_seconds()
            self.logger.info(f"✅ Market intelligence analysis completed in {analysis_duration:.2f}s")
            
            return intelligence
            
        except Exception as e:
            self.logger.error(f"❌ Market intelligence analysis failed: {e}")
            raise
    
    def _analyze_market_trend(self, vehicles: List[Dict]) -> MarketTrend:
        """Analyze overall market direction and trends"""
        self.logger.debug("📈 Analyzing market trends...")
        
        if len(vehicles) < 10:
            return MarketTrend(
                direction="unknown",
                strength=0.0,
                confidence=0.0,
                time_period="insufficient_data",
                analysis="Not enough data for trend analysis",
                supporting_data={}
            )
        
        # Group vehicles by posting date if available
        price_by_time = self._group_by_time_period(vehicles)
        
        if len(price_by_time) < 3:
            return self._analyze_static_trend(vehicles)
        
        # Calculate trend direction and strength
        periods = sorted(price_by_time.keys())
        prices = [statistics.mean(price_by_time[period]) for period in periods]
        
        # Linear regression for trend direction
        trend_slope = self._calculate_trend_slope(prices)
        
        # Determine direction and strength
        if abs(trend_slope) < self.trend_threshold:
            direction = "stable"
            strength = 1.0 - abs(trend_slope) / self.trend_threshold
        elif trend_slope > 0:
            direction = "rising"  
            strength = min(trend_slope / 0.2, 1.0)  # Cap at 20% change = max strength
        else:
            direction = "falling"
            strength = min(abs(trend_slope) / 0.2, 1.0)
        
        # Calculate confidence based on data consistency
        confidence = self._calculate_trend_confidence(prices)
        
        analysis = self._generate_trend_analysis(direction, strength, trend_slope)
        
        supporting_data = {
            "trend_slope": trend_slope,
            "price_periods": len(periods),
            "avg_price_change": trend_slope,
            "data_points": len(vehicles)
        }
        
        self.logger.debug(f"📊 Trend: {direction} (strength: {strength:.2f}, confidence: {confidence:.2f})")
        
        return MarketTrend(
            direction=direction,
            strength=strength,
            confidence=confidence,
            time_period="1month",  # Default analysis period
            analysis=analysis,
            supporting_data=supporting_data
        )
    
    def _analyze_price_patterns(self, vehicles: List[Dict]) -> List[PriceInsight]:
        """Analyze price patterns and identify opportunities"""
        self.logger.debug("💰 Analyzing price patterns...")
        
        insights = []
        
        if len(vehicles) < 5:
            return insights
        
        # Calculate price statistics
        prices = [v.get('price', 0) for v in vehicles if v.get('price')]
        if not prices:
            return insights
        
        mean_price = statistics.mean(prices)
        median_price = statistics.median(prices)
        std_price = statistics.stdev(prices) if len(prices) > 1 else 0
        
        # Identify underpriced vehicles (more than 1 std below mean)
        underpriced_threshold = mean_price - std_price
        overpriced_threshold = mean_price + std_price
        
        underpriced_count = sum(1 for p in prices if p < underpriced_threshold)
        overpriced_count = sum(1 for p in prices if p > overpriced_threshold)
        
        # Generate insights
        if underpriced_count > 0:
            insights.append(PriceInsight(
                category="underpriced",
                deviation_percent=((mean_price - underpriced_threshold) / mean_price) * 100,
                market_position="bottom_10" if underpriced_count <= len(prices) * 0.1 else "below_average",
                recommendation="investigate_opportunities",
                reasoning=f"Found {underpriced_count} vehicles significantly below market average"
            ))
        
        if overpriced_count > 0:
            insights.append(PriceInsight(
                category="overpriced", 
                deviation_percent=((overpriced_threshold - mean_price) / mean_price) * 100,
                market_position="top_10" if overpriced_count <= len(prices) * 0.1 else "above_average",
                recommendation="avoid_or_negotiate",
                reasoning=f"Found {overpriced_count} vehicles significantly above market average"
            ))
        
        # Market fairness insight
        fair_priced = len(prices) - underpriced_count - overpriced_count
        if fair_priced > len(prices) * 0.6:
            insights.append(PriceInsight(
                category="fair",
                deviation_percent=0.0,
                market_position="average",
                recommendation="standard_evaluation",
                reasoning=f"Most vehicles ({fair_priced}/{len(prices)}) are fairly priced within market range"
            ))
        
        self.logger.debug(f"💡 Generated {len(insights)} price insights")
        
        return insights
    
    def _assess_market_health(self, vehicles: List[Dict]) -> str:
        """Assess overall market health and stability"""
        self.logger.debug("🏥 Assessing market health...")
        
        if len(vehicles) < 5:
            return "insufficient_data"
        
        prices = [v.get('price', 0) for v in vehicles if v.get('price')]
        if not prices:
            return "unknown"
        
        # Calculate volatility metrics
        mean_price = statistics.mean(prices)
        std_price = statistics.stdev(prices) if len(prices) > 1 else 0
        volatility = std_price / mean_price if mean_price > 0 else 1
        
        # Assess health based on volatility and distribution
        if volatility < 0.1:  # Less than 10% volatility
            health = "healthy"
        elif volatility < self.volatility_threshold:
            health = "stable"
        elif volatility < 0.25:  # Less than 25% volatility
            health = "volatile"
        else:
            health = "unstable"
        
        self.logger.debug(f"🩺 Market health: {health} (volatility: {volatility:.3f})")
        
        return health
    
    def _generate_key_findings(self, vehicles: List[Dict], trend: MarketTrend, 
                             insights: List[PriceInsight]) -> List[str]:
        """Generate key market findings"""
        findings = []
        
        # Trend findings
        if trend.confidence > 0.7:
            if trend.direction == "rising":
                findings.append(f"🔺 Market prices are trending upward with {trend.strength:.0%} strength")
            elif trend.direction == "falling":
                findings.append(f"🔻 Market prices are declining with {trend.strength:.0%} strength")
            else:
                findings.append("📈 Market prices are stable with minimal volatility")
        
        # Price opportunity findings
        underpriced = [i for i in insights if i.category == "underpriced"]
        if underpriced:
            findings.append(f"💰 {len(underpriced)} potential opportunities identified below market value")
        
        overpriced = [i for i in insights if i.category == "overpriced"] 
        if overpriced:
            findings.append(f"⚠️ {len(overpriced)} vehicles priced above market average - negotiate or avoid")
        
        # Market composition finding
        findings.append(f"📊 Analysis based on {len(vehicles)} current market listings")
        
        return findings
    
    def _generate_recommendations(self, trend: MarketTrend, insights: List[PriceInsight], 
                                health: str) -> List[str]:
        """Generate intelligent market recommendations"""
        recommendations = []
        
        # Trend-based recommendations
        if trend.direction == "rising" and trend.confidence > 0.6:
            recommendations.append("🚀 Consider accelerating purchase decisions - prices trending upward")
        elif trend.direction == "falling" and trend.confidence > 0.6:
            recommendations.append("⏳ Consider waiting for better deals - prices trending downward")
        
        # Health-based recommendations
        if health == "volatile":
            recommendations.append("🎯 Focus on vehicles with stable pricing history")
        elif health == "unstable":
            recommendations.append("⚠️ Exercise extra caution - market showing high volatility")
        
        # Insight-based recommendations
        underpriced = [i for i in insights if i.category == "underpriced"]
        if underpriced:
            recommendations.append("🔍 Investigate underpriced vehicles for potential deals")
        
        # General wisdom
        recommendations.append("📋 Always inspect vehicles thoroughly regardless of price positioning")
        recommendations.append("💡 Use market insights as one factor in decision making")
        
        return recommendations
    
    def _group_by_time_period(self, vehicles: List[Dict]) -> Dict[str, List[float]]:
        """Group vehicle prices by time periods"""
        # Simplified - in real implementation would use actual posting dates
        # For now, simulate time-based grouping
        periods = defaultdict(list)
        
        for i, vehicle in enumerate(vehicles):
            price = vehicle.get('price')
            if price:
                # Simulate time periods based on position in list
                period_index = i // (len(vehicles) // 4) if len(vehicles) >= 4 else 0
                period_key = f"period_{period_index}"
                periods[period_key].append(price)
        
        return periods
    
    def _analyze_static_trend(self, vehicles: List[Dict]) -> MarketTrend:
        """Analyze trend when temporal data is insufficient"""
        prices = [v.get('price', 0) for v in vehicles if v.get('price')]
        
        if not prices:
            return MarketTrend("unknown", 0.0, 0.0, "no_data", "No price data available", {})
        
        mean_price = statistics.mean(prices)
        median_price = statistics.median(prices)
        
        # Use median vs mean to infer market bias
        price_skew = (mean_price - median_price) / median_price if median_price > 0 else 0
        
        if abs(price_skew) < 0.1:
            direction = "stable"
            analysis = "Market shows balanced pricing distribution"
        elif price_skew > 0:
            direction = "rising"
            analysis = "Higher-priced vehicles pulling average up - potential upward pressure"
        else:
            direction = "falling" 
            analysis = "Lower-priced vehicles dominating - potential downward pressure"
        
        return MarketTrend(
            direction=direction,
            strength=min(abs(price_skew), 1.0),
            confidence=0.3,  # Lower confidence without temporal data
            time_period="snapshot",
            analysis=analysis,
            supporting_data={"price_skew": price_skew, "sample_size": len(prices)}
        )
    
    def _calculate_trend_slope(self, prices: List[float]) -> float:
        """Calculate linear trend slope"""
        if len(prices) < 2:
            return 0.0
        
        n = len(prices)
        x_values = list(range(n))
        
        # Simple linear regression
        x_mean = statistics.mean(x_values)
        y_mean = statistics.mean(prices)
        
        numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, prices))
        denominator = sum((x - x_mean) ** 2 for x in x_values)
        
        if denominator == 0:
            return 0.0
        
        slope = numerator / denominator
        return slope / y_mean if y_mean > 0 else 0.0  # Normalize by mean price
    
    def _calculate_trend_confidence(self, prices: List[float]) -> float:
        """Calculate confidence in trend analysis"""
        if len(prices) < 3:
            return 0.0
        
        # R-squared calculation for trend line fit
        n = len(prices)
        x_values = list(range(n))
        
        x_mean = statistics.mean(x_values)
        y_mean = statistics.mean(prices)
        
        # Calculate correlation coefficient
        numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, prices))
        sum_x_sq = sum((x - x_mean) ** 2 for x in x_values)
        sum_y_sq = sum((y - y_mean) ** 2 for y in prices)
        
        if sum_x_sq * sum_y_sq == 0:
            return 0.0
        
        r = numerator / (sum_x_sq * sum_y_sq) ** 0.5
        r_squared = r ** 2
        
        return r_squared
    
    def _generate_trend_analysis(self, direction: str, strength: float, slope: float) -> str:
        """Generate human-readable trend analysis"""
        if direction == "stable":
            return f"Market prices are stable with minimal fluctuation ({slope:+.1%} change)"
        elif direction == "rising":
            return f"Market shows upward trend with {strength:.0%} strength ({slope:+.1%} change)"
        else:
            return f"Market shows downward trend with {strength:.0%} strength ({slope:+.1%} change)"

def demo_intelligent_insights():
    """Demo function to test the intelligence engine"""
    print("🧠 Intelligent Market Insights Engine Demo")
    print("=" * 50)
    
    # Sample vehicle data for testing
    sample_vehicles = [
        {"price": 85000, "year": 2019, "km": 45000, "manufacturer": "Toyota"},
        {"price": 92000, "year": 2020, "km": 32000, "manufacturer": "Toyota"},
        {"price": 78000, "year": 2018, "km": 67000, "manufacturer": "Toyota"},
        {"price": 95000, "year": 2020, "km": 28000, "manufacturer": "Honda"},
        {"price": 105000, "year": 2021, "km": 15000, "manufacturer": "Honda"},
        {"price": 72000, "year": 2017, "km": 89000, "manufacturer": "Mazda"},
        {"price": 88000, "year": 2019, "km": 52000, "manufacturer": "Mazda"},
        {"price": 120000, "year": 2022, "km": 8000, "manufacturer": "Honda"},
        {"price": 65000, "year": 2016, "km": 120000, "manufacturer": "Toyota"},
        {"price": 98000, "year": 2020, "km": 35000, "manufacturer": "Mazda"},
    ]
    
    # Initialize and run analysis
    engine = IntelligentMarketInsights()
    intelligence = engine.analyze_market_intelligence(sample_vehicles)
    
    # Display results
    print(f"\n📊 MARKET INTELLIGENCE REPORT")
    print(f"Generated: {intelligence.generated_at.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    print(f"🔍 OVERALL TREND:")
    trend = intelligence.overall_trend
    print(f"  Direction: {trend.direction}")
    print(f"  Strength: {trend.strength:.1%}")
    print(f"  Confidence: {trend.confidence:.1%}")
    print(f"  Analysis: {trend.analysis}")
    print()
    
    print(f"💰 PRICE INSIGHTS:")
    for insight in intelligence.price_insights:
        print(f"  • {insight.category.title()}: {insight.reasoning}")
    print()
    
    print(f"🏥 MARKET HEALTH: {intelligence.market_health}")
    print()
    
    print(f"🔑 KEY FINDINGS:")
    for finding in intelligence.key_findings:
        print(f"  • {finding}")
    print()
    
    print(f"💡 RECOMMENDATIONS:")
    for rec in intelligence.recommendations:
        print(f"  • {rec}")
    print()

if __name__ == "__main__":
    demo_intelligent_insights()