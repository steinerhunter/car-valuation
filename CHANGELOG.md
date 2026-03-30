# Changelog

All notable changes to the Heinrich Car Valuation skill will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-03-30

### 🚀 Major Features Added

#### OME-94: WhatsApp Link Analysis
- **NEW**: Automatic Yad2 link detection and analysis in WhatsApp messages
- **NEW**: `yad2_link_analyzer.py` - Comprehensive link scraping and data extraction
- **NEW**: `whatsapp_integration.py` - Smart message processing for car content
- **NEW**: Instant car valuation from shared Yad2 URLs
- **NEW**: Bilingual link analysis (Hebrew/English responses)

### ✨ Enhanced Features

#### OME-90: Buyer/Seller Intelligence  
- **NEW**: `buyer_seller_intelligence.py` - Advanced user intent analysis
- **NEW**: Automatic detection of buying vs selling queries
- **NEW**: Smart negotiation advice for buyers
- **NEW**: 3-tier pricing strategy for sellers (quick/market/optimistic)
- **NEW**: Deal quality assessment (excellent/good/fair/expensive/overpriced)
- **NEW**: Market competition analysis and risk factors

#### OME-84: Advanced Price Analysis
- **ENHANCED**: `advanced_price_analysis.py` - Statistical correlations  
- **NEW**: Price-mileage correlation analysis with depreciation rates
- **NEW**: Geographic price intelligence across Israeli regions
- **NEW**: Content analysis for premium feature detection
- **NEW**: Multi-factor confidence scoring

### 🔧 Technical Improvements
- **ENHANCED**: `market_analyzer.py` - Integrated with all new analysis engines
- **NEW**: `analyze_user_query_with_intent()` - Intent-aware analysis function
- **IMPROVED**: Hebrew language support throughout all components
- **NEW**: Comprehensive error handling and validation
- **NEW**: Smart data cleaning and outlier detection

### 📚 Documentation
- **NEW**: Comprehensive README.md with usage examples
- **NEW**: GitHub repository preparation
- **UPDATED**: SKILL.md with WhatsApp link analysis examples
- **NEW**: Technical architecture documentation
- **NEW**: Israeli market focus and geographic intelligence

### 🐛 Bug Fixes
- **FIXED**: NoneType error in task_manager.py for assignee/project null handling
- **FIXED**: Linear API limit issues (1000 → 250 records)
- **IMPROVED**: URL parsing and normalization for Yad2 links
- **IMPROVED**: Price extraction from various Hebrew/English formats

## [1.0.0] - 2026-03-15

### 🎯 Initial Release Features

#### Core Car Valuation Engine
- **NEW**: `car_valuation_api.py` - Apify integration for live Yad2 data
- **NEW**: `market_analyzer.py` - Basic market analysis and price estimation
- **NEW**: Real-time data collection from Yad2 listings
- **NEW**: Hebrew and English query support
- **NEW**: Basic price range analysis and confidence scoring

#### Hebrew Language Support
- **NEW**: Hebrew car manufacturer and model recognition
- **NEW**: Hebrew query pattern matching
- **NEW**: Hebrew response formatting
- **NEW**: Mixed Hebrew/English input handling

#### Israeli Market Intelligence  
- **NEW**: Support for major Israeli car manufacturers
- **NEW**: Geographic awareness (Tel Aviv, Haifa, Beer Sheva, etc.)
- **NEW**: Israeli currency formatting (₪)
- **NEW**: Local market dynamics understanding

#### OpenClaw Integration
- **NEW**: SKILL.md integration with Heinrich AI
- **NEW**: WhatsApp message processing capability
- **NEW**: Automatic query detection and response

### 📊 Statistics (v1.0)
- **Supported Manufacturers**: 15+ (Hebrew & English names)
- **Coverage**: Major Israeli cities and regions  
- **Query Types**: Basic valuation and price checking
- **Response Time**: 10-30 seconds for live market data
- **Cost**: ~$0.01-0.05 per valuation

## [Unreleased] - Future Roadmap

### Planned Features (Product Roadmap)
- **OME-93**: 🖼️ Visual Car Recognition (photo analysis)
- **OME-95**: 🎯 Smart Alternative Suggestions
- **OME-96**: ⚡ Real-Time Market Alerts  
- **OME-97**: 📊 Market Timing Intelligence
- **OME-98**: 🔧 Transaction Assistant (checklists & mechanic referrals)
- **OME-99**: 👤 Personal Car Profile & Learning
- **OME-100**: 💰 Finance Integration (loans & insurance)
- **OME-101**: 🌐 Cross-Platform Shopping (multiple listing sites)

### Technical Debt
- [ ] Add comprehensive unit tests
- [ ] Implement caching for frequent queries
- [ ] Add rate limiting for API calls
- [ ] Improve error handling for edge cases
- [ ] Add logging and monitoring

---

**Legend:**
- 🚀 Major new features
- ✨ Enhancements  
- 🔧 Technical improvements
- 📚 Documentation
- 🐛 Bug fixes
- 📊 Statistics & metrics