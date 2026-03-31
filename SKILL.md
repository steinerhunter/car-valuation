---
name: car-valuation  
description: Real-time Israeli car market valuation with full Hebrew and English support. Scrapes live Yad2 data to provide price estimates, market analysis, and insights. Triggers on Hebrew car value queries (כמה שווה ההונדה, מה המחיר של הטויוטה, תעריך לי את הרכב, בכמה נמכר) and English queries ("what's my car worth", "value my Toyota", "how much is worth"). Automatically detects car manufacturers and models in both languages.
---

# Car Valuation

Real-time car valuation for the Israeli market using live Yad2 data scraping.

## Overview

This skill provides OpenClaw AI assistants with the ability to give accurate, current car valuations by scraping real-time data from Yad2 and other Israeli car listing sites. Instead of using stale datasets, it queries live market data and provides intelligent analysis.

**Perfect for user queries like:**

**English:**
- "What's my 2019 Toyota Corolla worth?"
- "How much should I pay for a 2018 Honda Civic?"  
- "Is 85,000 ILS a good price for this car?"
- "Value a 2020 Hyundai i30 with 40K km"

**Hebrew:**
- "כמה שווה טויוטה קורולה 2019 שלי?"
- "מה המחיר של הונדה סיוויק משנת 2018?"
- "תעריך לי יונדאי i30 עם 45 אלף ק״מ"
- "בכמה נמכר ניסאן מיקרה 2017?"

**🚀 NEW: WhatsApp Link Analysis (OME-94):**
- Send any Yad2 car listing link via WhatsApp
- Your AI assistant automatically analyzes the car and provides instant market comparison
- No manual input needed - just paste the link!

**WhatsApp Examples:**
- "What do you think about this car? https://yad2.co.il/ad/toyota-corolla-2019-85000"
- "מה דעתך על זה? https://yad2.co.il/vehicles/item/12345"
- Just paste any Yad2 URL → Instant analysis!

## 🚀 WhatsApp Link Analysis (OME-94 - NEW!)

The AI assistant now automatically detects and analyzes Yad2 car listing links sent via WhatsApp or any chat platform!

### Quick Link Analysis
```python
from scripts.yad2_link_analyzer import analyze_yad2_link

# User sends: "מה דעתך על הרכב הזה? https://yad2.co.il/ad/toyota-corolla-2019-85000"
url = "https://yad2.co.il/ad/toyota-corolla-2019-85000"
result = analyze_yad2_link(url, hebrew_response=True)

if result['status'] == 'success':
    listing = result['listing_data']
    # AI responds: "מצאתי טויוטה קורולה 2019 במחיר 85,000 ₪ - מנתח השוק..."
```

### Automatic Detection
The skill automatically detects Yad2 URLs in messages and triggers analysis without user having to specify car details manually.

**Supported URL formats:**
- `yad2.co.il/vehicles/cars/item/12345`
- `yad2.co.il/ad/67890`
- `m.yad2.co.il/vehicles/item/54321`
- Any Yad2 car listing URL

### Smart Data Extraction
Automatically extracts from Yad2 listings:
- **Car Details**: Manufacturer, model, year, price
- **Specs**: Mileage, city, seller type (private/dealer)
- **Features**: Leather seats, hybrid, sunroof, etc.
- **Market Context**: Ready for instant comparison analysis

## Core Workflow

### 1. Parse User Query
Extract key information:
- **Year**: Vehicle model year
- **Manufacturer**: Car brand (Toyota, Honda, etc.)
- **Model**: Specific model (Corolla, Civic, etc.) 
- **Mileage**: Optional km reading
- **Area**: Optional geographic preference

### 2. Real-Time Market Search
```python
from scripts.car_valuation_api import CarValuationAPI, VehicleQuery
from scripts.market_analyzer import analyze_user_query

# Initialize API (requires Apify token)
api = CarValuationAPI(api_token)

# Create targeted query
query = VehicleQuery(
    manufacturer="Toyota",
    model="Corolla", 
    min_year=2019,
    max_year=2019,
    area="tel aviv",
    max_items=20  # Good sample size
)

# Get live market data
vehicles, error = api.run_single_query(query)
```

### 3. Market Analysis
```python
# Analyze results with user context
result = analyze_user_query(
    vehicles=vehicles,
    year=2019, 
    manufacturer="Toyota",
    model="Corolla",
    km=60000  # User's mileage if provided
)

# Returns formatted analysis with:
# - Price ranges based on current listings
# - Market insights and trends  
# - Personalized valuation estimate
# - Sample current listings
```

## Key Features

**Real-Time Data**: Always current market information  
**Smart Analysis**: Price ranges, market trends, outlier detection  
**Israeli Focus**: Understands local market dynamics  
**Bilingual**: Handles Hebrew and English car names  
**Cost Effective**: ~$0.01-0.05 per valuation query

## Usage Examples

### Basic Car Valuation
```python
# User: "What's my 2019 Toyota Corolla worth?"
api = CarValuationAPI(apify_token)
query = VehicleQuery("Toyota", "Corolla", 2019, 2019, "tel aviv", 15)
vehicles, _ = api.run_single_query(query)
result = analyze_user_query(vehicles, 2019, "Toyota", "Corolla")
```

### With Mileage Context
```python
# User: "Value a 2018 Honda Civic with 45K km"  
query = VehicleQuery("Honda", "Civic", 2018, 2018, "center", 15)
vehicles, _ = api.run_single_query(query)
result = analyze_user_query(vehicles, 2018, "Honda", "Civic", km=45000)
```

### Broader Market Search
```python
# User: "What do 2017-2019 Hyundai i30s cost?"
query = VehicleQuery("Hyundai", "i30", 2017, 2019, "tel aviv", 25)  
vehicles, _ = api.run_single_query(query)
result = analyze_user_query(vehicles, 2018, "Hyundai", "i30")  # Use middle year
```

## References

- **israeli_manufacturers.md**: Complete list of car brands/models in Israeli market
- **areas.md**: Valid geographic regions for searching (tel aviv, center, haifa, etc.)

## Cost & Performance

**Per Query Cost**: $0.01-0.05 (vs $1000+ for commercial APIs)  
**Response Time**: 10-30 seconds for fresh market data  
**Coverage**: 20,000+ daily listings across Israeli market  
**Accuracy**: Based on real current market activity

## Error Handling

**No Results Found**: Suggest expanding search (year range, different areas)  
**Invalid Manufacturer/Model**: Reference israeli_manufacturers.md for corrections  
**API Failures**: Graceful degradation with explanation  
**Cost Limits**: Built-in query optimization to minimize API usage

## Hebrew Language Support

### Hebrew Query Parsing
The skill automatically detects and parses Hebrew queries:

```python
# Hebrew queries automatically parsed
hebrew_queries = [
    "כמה שווה טויוטה קורולה 2019 שלי?",  # "What's my 2019 Toyota Corolla worth?"
    "מה המחיר של הונדה סיוויק משנת 2018 עם 45 אלף ק״מ?",  # With mileage
    "תעריך לי יונדאי i30 מ-2020",  # "Value my 2020 Hyundai i30"
    "בכמה נמכר BMW סדרה 3 2018?"  # BMW with Hebrew model name
]

# All automatically convert to English API calls
# But return Hebrew responses when Hebrew input detected
```

### Hebrew Response Example
```
🚗 **ניתוח שוק: טויוטה קורולה 2019**

📊 **שוק נוכחי** (מבוסס על 12 מודעות פעילות):
   💰 טווח מחירים: 82,000 - 95,000 ₪
   📈 ממוצע: 88,500 ₪
   🎯 חציון: 87,000 ₪

🎯 **הערכת שווי**: 84,000 - 92,000 ₪
   📊 מחיר חציון בשוק: 87,000 ₪
   🔍 רמת ביטחון: גבוהה

💡 **תובנות שוק**:
   • נתוני שוק עשירים - הערכות מחיר אמינות ביותר

📋 **דוגמאות מודעות נוכחיות**:
   1. 82,000 ₪ (2019, 89,000 ק״מ, פתח תקווה)
   2. 87,000 ₪ (2019, 67,000 ק״מ, תל אביב)
```

### Hebrew Features
- **Hebrew car names**: טויוטה קורולה, הונדה סיוויק, יונדאי i30
- **Hebrew query patterns**: כמה שווה, מה המחיר, תעריך לי
- **Hebrew mileage**: 45 אלף ק״מ, 60,000 ק״מ
- **Hebrew cities**: תל אביב, פתח תקווה, רעננה
- **Israeli currency**: ₪ (Shekel symbol)
- **Mixed Hebrew/English**: "כמה שווה Toyota Corolla 2019?"

## Advanced Usage

### Multiple Area Search
```python
areas = ["tel aviv", "center", "haifa"]
all_vehicles = []

for area in areas:
    query = VehicleQuery(manufacturer, model, year, year, area, 10)
    vehicles, _ = api.run_single_query(query)
    all_vehicles.extend(vehicles)

# Analyze with Hebrew response option
result = analyze_user_query(all_vehicles, year, manufacturer, model, km, hebrew_response=True)
```

### Price Comparison
```python
# User: "Is 85,000 ILS good for this 2019 Corolla?"
vehicles, _ = api.run_single_query(query)
analysis = analyze_user_query(vehicles, 2019, "Toyota", "Corolla")

# Include specific price comparison in response
user_price = 85000
market_median = analysis['market_data']['price_range']['median'] 

if user_price < market_median:
    comparison = "This is below market median - a good deal!"
elif user_price > market_median * 1.1:
    comparison = "This is above market median - consider negotiating"
else:
    comparison = "This is close to market median - fair pricing"
```

This skill transforms Heinrich into an authoritative source for Israeli car valuations with real-time market intelligence and full Hebrew language support.