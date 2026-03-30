# 🚗 Heinrich Car Valuation Skill

**Real-time Israeli car market valuation with AI-powered analysis**

Heinrich's Car Valuation skill provides instant, accurate car valuations for the Israeli market using live Yad2 data and advanced market intelligence. Perfect for both buyers and sellers in the Israeli automotive market.

## 🎯 Key Features

### 🚀 **NEW: WhatsApp Link Analysis (OME-94)**
- **Instant Link Analysis**: Send any Yad2 car listing URL → Get immediate valuation
- **Smart Detection**: Automatically detects car info from links
- **Bilingual**: Full Hebrew and English support
- **WhatsApp Ready**: Optimized for WhatsApp conversations

### 💡 **Advanced Market Intelligence**
- **Real-Time Data**: Live scraping from Yad2 listings
- **Smart Analysis**: Price correlations, geographic trends, content analysis
- **Buyer/Seller Mode**: Different insights for buyers vs sellers
- **Market Confidence**: Reliability scoring based on data quality

### 🌐 **Bilingual Support**
- **Hebrew Queries**: "כמה שווה טויוטה קורולה 2019 שלי?"
- **English Queries**: "What's my 2019 Toyota Corolla worth?"
- **Mixed Input**: Hebrew car names with English text
- **Smart Response**: Automatically matches query language

## 📱 Usage Examples

### WhatsApp Link Analysis
```
User: "Heinrich, מה דעתך? https://yad2.co.il/ad/toyota-corolla-85000"

Heinrich: "🚗 מצאתי: 2019 Toyota Corolla
💰 מחיר: 85,000 ₪
🛣️ קילומטראז': 60,000 ק״מ
📍 מיקום: תל אביב

🔍 מנתח את השוק עכשיו..."
```

### Market Valuation Queries
```python
# Hebrew Query
"כמה שווה טויוטה קורולה 2019 עם 60 אלף קמ?"

# English Query  
"What's my 2019 Toyota Corolla with 60K km worth?"

# Buyer Query
"האם 85,000 ₪ זה מחיר טוב לטויוטה קורולה 2019?"
→ Heinrich provides negotiation advice and market comparison

# Seller Query
"כמה לבקש עבור הטויוטה קורולה 2019 שלי?"
→ Heinrich provides pricing strategy (quick sale / market rate / optimistic)
```

## 🏗️ Technical Architecture

### Core Components

```
car-valuation/
├── scripts/
│   ├── car_valuation_api.py          # Apify integration & data collection
│   ├── market_analyzer.py            # Market analysis engine
│   ├── advanced_price_analysis.py    # OME-84: Advanced price correlations
│   ├── buyer_seller_intelligence.py  # OME-90: Buyer/seller recommendations
│   ├── yad2_link_analyzer.py         # OME-94: Link scraping & analysis
│   └── whatsapp_integration.py       # OME-94: WhatsApp message processing
├── SKILL.md                          # Heinrich skill definition
└── README.md                         # This file
```

### Data Flow

1. **Input Detection**: Detect car queries, Yad2 links, or general questions
2. **Data Collection**: Real-time Yad2 scraping or link analysis  
3. **Market Analysis**: Advanced price modeling with correlations
4. **Intent Analysis**: Buyer vs seller recommendations
5. **Response Generation**: Bilingual, context-aware responses

## 🚀 Quick Start

### Prerequisites
- **OpenClaw**: This is a Heinrich AI skill for OpenClaw
- **Apify API Token**: For live Yad2 data scraping
- **Python 3.8+**: Required dependencies

### Installation

1. **Clone to OpenClaw skills directory**:
```bash
cd ~/.openclaw/workspace/skills/
git clone https://github.com/omersalomon/heinrich-car-valuation car-valuation
```

2. **Set up Apify API token**:
```bash
export APIFY_API_TOKEN=your_token_here
```

3. **Install dependencies**:
```bash
pip install requests beautifulsoup4 dataclasses
```

4. **Test the installation**:
```python
from car_valuation.scripts.whatsapp_integration import process_whatsapp_car_message

# Test WhatsApp link analysis
result = process_whatsapp_car_message("מה דעתך? https://yad2.co.il/ad/toyota-corolla-85000")
print(result)
```

## 🎯 Core Use Cases

### 1. **WhatsApp Link Analysis**
```python
from scripts.yad2_link_analyzer import analyze_yad2_link

url = "https://yad2.co.il/vehicles/item/12345"
result = analyze_yad2_link(url, hebrew_response=True)

if result['status'] == 'success':
    car = result['listing_data']
    print(f"Found: {car['year']} {car['manufacturer']} {car['model']}")
    print(f"Price: {car['price']:,} ₪")
```

### 2. **Market Valuation**
```python
from scripts.market_analyzer import analyze_user_query_with_intent
from scripts.car_valuation_api import CarValuationAPI, VehicleQuery

# Get live market data
api = CarValuationAPI(apify_token)
query = VehicleQuery("Toyota", "Corolla", 2019, 2019, "tel aviv", 20)
vehicles, _ = api.run_single_query(query)

# Analyze with buyer/seller intelligence
result = analyze_user_query_with_intent(
    vehicles=vehicles,
    user_query_text="כמה שווה הטויוטה קורולה 2019 שלי?",
    year=2019,
    manufacturer="Toyota",
    model="Corolla", 
    km=60000,
    hebrew_response=True
)

print(result)
```

### 3. **Buyer vs Seller Analysis**
```python
# Buyer Query - Price Evaluation
buyer_query = "האם 85,000 ₪ זה מחיר טוב לטויוטה קורולה 2019?"
buyer_result = analyze_user_query_with_intent(vehicles, buyer_query, ...)

# Seller Query - Pricing Strategy  
seller_query = "כמה לבקש עבור הטויוטה קורולה 2019 שלי?"
seller_result = analyze_user_query_with_intent(vehicles, seller_query, ...)
```

## 📊 Advanced Features

### **OME-84: Smart Yad2 Analysis**
- **Price-Mileage Correlations**: Statistical analysis of depreciation rates
- **Geographic Intelligence**: Price variations by city/region  
- **Content Analysis**: Premium feature detection from listings
- **Confidence Scoring**: Multi-factor reliability assessment

### **OME-90: Buyer/Seller Intelligence** 
- **Intent Detection**: Automatically detect if user is buying or selling
- **Deal Quality Assessment**: Rate deals as excellent/good/fair/expensive
- **Negotiation Advice**: Specific strategies and target prices
- **Pricing Strategy**: 3-tier seller recommendations (quick/market/optimistic)

### **OME-94: WhatsApp Link Analysis**
- **Automatic URL Detection**: Finds Yad2 links in messages
- **Smart Data Extraction**: Scrapes car details from listings
- **Instant Analysis**: No manual input required
- **Bilingual Responses**: Matches user's language automatically

## 🌍 Israeli Market Focus

### **Supported Manufacturers**
Hebrew and English names for all major brands:
- **Japanese**: טויוטה (Toyota), הונדה (Honda), ניסאן (Nissan), מאזדה (Mazda)
- **Korean**: יונדאי (Hyundai), קיה (Kia) 
- **German**: ב.מ.וו (BMW), מרצדס (Mercedes), אאודי (Audi), פולקסווגן (Volkswagen)
- **European**: פז'ו (Peugeot), רנו (Renault), פיאט (Fiat), שקודה (Skoda)

### **Geographic Intelligence**
Price analysis across Israeli regions:
- **Center**: תל אביב, פתח תקווה, רמת גן, רעננה
- **North**: חיפה, נתניה, הרצליה, כפר סבא
- **South**: אשדוד, ראשון לציון, רחובות, באר שבע

### **Market Dynamics**
- **Currency**: Israeli Shekel (₪) with proper formatting
- **Regulations**: Israeli annual inspection (בדיקה שנתית) awareness
- **Seasonal Trends**: End-of-year price patterns
- **Import Dynamics**: European vs Japanese car preferences

## 📈 Performance & Cost

### **Speed**
- **Link Analysis**: 2-5 seconds per URL
- **Market Analysis**: 10-30 seconds for fresh data
- **WhatsApp Response**: Near-instant for cached patterns

### **Cost Efficiency**
- **Per Valuation**: $0.01-0.05 (vs $1000+ commercial APIs)
- **Bulk Analysis**: Volume discounts with Apify
- **Smart Caching**: Reduces redundant API calls

### **Accuracy**
- **Live Data**: Always current market conditions
- **Sample Size**: Typically 10-50 comparable listings
- **Confidence Scoring**: Reliability indicators for all estimates

## 🤝 Contributing

We welcome contributions! This skill is part of the Heinrich AI ecosystem.

### **Development Roadmap**
- **OME-95**: Smart Alternative Suggestions
- **OME-96**: Real-Time Market Alerts  
- **OME-97**: Market Timing Intelligence
- **OME-98**: Transaction Assistant
- **OME-99**: Personal Learning & Profiles

### **Priority Features**
1. **Visual Car Recognition** (photos → analysis)
2. **Cross-Platform Shopping** (multiple listing sites)
3. **Finance Integration** (loan calculations)

## 📄 License

MIT License - Feel free to use, modify, and distribute.

## 🙋‍♂️ Support

- **Issues**: GitHub Issues for bug reports
- **Questions**: OpenClaw Discord community
- **Hebrew Support**: Native Hebrew speakers welcome!

---

**Built with ❤️ for the Israeli car market by the Heinrich AI team**

*Last updated: March 2026 | Version: 2.0 (OME-94 Release)*