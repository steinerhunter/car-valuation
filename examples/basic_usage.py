#!/usr/bin/env python3
"""
Heinrich Car Valuation - Basic Usage Examples
Demonstrates core car valuation functionality
"""

import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scripts'))

def example_1_basic_valuation():
    """Example 1: Basic car valuation using market data"""
    print("📊 Example 1: Basic Car Valuation")
    print("-" * 40)
    
    # This would require real Apify API token and live data
    # For demo, we'll show the code structure
    
    print("""
# Import the main components
from car_valuation_api import CarValuationAPI, VehicleQuery
from market_analyzer import analyze_user_query

# Set up API (requires APIFY_API_TOKEN environment variable)
api = CarValuationAPI(os.getenv('APIFY_API_TOKEN'))

# Create a query for Toyota Corolla 2019 in Tel Aviv
query = VehicleQuery(
    manufacturer="Toyota",
    model="Corolla",
    min_year=2019,
    max_year=2019,
    area="tel aviv",
    max_items=20
)

# Get live market data
vehicles, error = api.run_single_query(query)

if not error:
    # Analyze the market data
    result = analyze_user_query(
        vehicles=vehicles,
        year=2019,
        manufacturer="Toyota", 
        model="Corolla",
        km=60000,  # User's car has 60K km
        hebrew_response=True  # Hebrew response
    )
    
    print(result)
else:
    print(f"Error: {error}")
""")

def example_2_link_analysis():
    """Example 2: Yad2 link analysis"""  
    print("🔗 Example 2: Yad2 Link Analysis")
    print("-" * 40)
    
    print("""
# Import the link analyzer
from yad2_link_analyzer import analyze_yad2_link

# Analyze a Yad2 listing URL
url = "https://yad2.co.il/vehicles/item/12345"
result = analyze_yad2_link(url, hebrew_response=True)

if result['status'] == 'success':
    car = result['listing_data']
    print(f"Found: {car['year']} {car['manufacturer']} {car['model']}")
    print(f"Price: {car['price']:,} ₪")
    print(f"Mileage: {car['km']:,} km") 
    print(f"Location: {car['city']}")
else:
    print(f"Analysis failed: {result['message']}")
""")

def example_3_buyer_seller_intelligence():
    """Example 3: Advanced buyer/seller analysis"""
    print("🧠 Example 3: Buyer/Seller Intelligence") 
    print("-" * 40)
    
    print("""
# Import advanced analysis
from market_analyzer import analyze_user_query_with_intent

# Sample market data (normally from live API)
sample_vehicles = [
    {'price': 79000, 'year': 2019, 'km': 58000, 'cityEn': 'Tel Aviv'},
    {'price': 85000, 'year': 2019, 'km': 42000, 'cityEn': 'Haifa'},
    {'price': 91000, 'year': 2019, 'km': 35000, 'cityEn': 'Petah Tikva'},
]

# BUYER QUERY: Evaluate a specific price
buyer_query = "האם 85,000 ₪ זה מחיר טוב לטויוטה קורולה 2019?"
buyer_result = analyze_user_query_with_intent(
    vehicles=sample_vehicles,
    user_query_text=buyer_query,
    year=2019,
    manufacturer="Toyota",
    model="Corolla", 
    hebrew_response=True
)

print("🛒 BUYER ANALYSIS:")
print(buyer_result)

# SELLER QUERY: Get pricing strategy
seller_query = "כמה שווה הטויוטה קורולה 2019 שלי עם 60K קמ?"
seller_result = analyze_user_query_with_intent(
    vehicles=sample_vehicles,
    user_query_text=seller_query,
    year=2019,
    manufacturer="Toyota",
    model="Corolla",
    km=60000,
    hebrew_response=True
)

print("\\n💰 SELLER ANALYSIS:")
print(seller_result)
""")

def example_4_whatsapp_integration():
    """Example 4: WhatsApp message processing"""
    print("📱 Example 4: WhatsApp Integration")
    print("-" * 40)
    
    print("""
# Import WhatsApp integration
from whatsapp_integration import process_whatsapp_car_message

# Process different types of WhatsApp messages
test_messages = [
    "מה דעתך על זה? https://yad2.co.il/ad/toyota-corolla-85000",
    "כמה שווה טויוטה קורולה 2019 עם 60 אלף קמ?",
    "Is 85,000 ILS good for this Honda Civic?",
    "אני מחפש רכב עד 90 אלף"
]

for message in test_messages:
    print(f"\\nUser: {message}")
    
    response = process_whatsapp_car_message(message)
    if response:
        print(f"Heinrich: {response[:100]}...")  # First 100 chars
    else:
        print("Heinrich: (no car-related response)")
""")

def show_code_statistics():
    """Show code statistics and features"""
    print("📊 Heinrich Car Valuation - Code Statistics")
    print("=" * 50)
    
    # Count lines of code
    import glob
    
    script_dir = os.path.join(os.path.dirname(__file__), '..', 'scripts')
    python_files = glob.glob(os.path.join(script_dir, '*.py'))
    
    total_lines = 0
    file_stats = []
    
    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = len(f.readlines())
                total_lines += lines
                file_stats.append((os.path.basename(file_path), lines))
        except:
            pass
    
    print(f"📁 Total Python files: {len(file_stats)}")
    print(f"📝 Total lines of code: {total_lines:,}")
    print()
    
    print("📋 File breakdown:")
    for filename, lines in sorted(file_stats, key=lambda x: x[1], reverse=True):
        print(f"  {filename:30} {lines:4,} lines")
    
    print()
    print("🎯 Key Features:")
    features = [
        "Real-time Yad2 data scraping",
        "Advanced price correlation analysis", 
        "Buyer/seller intelligence",
        "WhatsApp link analysis",
        "Hebrew/English bilingual support",
        "Geographic price intelligence",
        "Content analysis & feature detection",
        "Confidence scoring",
        "Intent detection",
        "Negotiation advice"
    ]
    
    for feature in features:
        print(f"  ✅ {feature}")

if __name__ == "__main__":
    print("🚗 Heinrich Car Valuation - Usage Examples\n")
    
    # Show all examples
    example_1_basic_valuation()
    print("\n" + "="*60 + "\n")
    
    example_2_link_analysis()
    print("\n" + "="*60 + "\n")
    
    example_3_buyer_seller_intelligence() 
    print("\n" + "="*60 + "\n")
    
    example_4_whatsapp_integration()
    print("\n" + "="*60 + "\n")
    
    show_code_statistics()
    
    print("\n🎉 Examples Complete!")
    print("\n💡 To run these examples with real data:")
    print("1. Set environment variable: export APIFY_API_TOKEN=your_token")
    print("2. Install requirements: pip install -r requirements.txt")
    print("3. Run: python examples/basic_usage.py")
    print("\n🔗 More info: https://github.com/omersalomon/heinrich-car-valuation")