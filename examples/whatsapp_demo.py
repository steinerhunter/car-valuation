#!/usr/bin/env python3
"""
Heinrich Car Valuation - WhatsApp Integration Demo
Demonstrates OME-94: WhatsApp Link Analysis functionality
"""

import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from whatsapp_integration import process_whatsapp_car_message

def demo_whatsapp_messages():
    """Demonstrate various WhatsApp message types and Heinrich's responses"""
    
    print("🚗 Heinrich Car Valuation - WhatsApp Demo")
    print("="*60)
    print("Demonstrating OME-94: WhatsApp Link Analysis")
    print()
    
    # Test messages covering different scenarios
    test_messages = [
        # Yad2 Links
        {
            'message': "מה דעתך על זה? https://yad2.co.il/ad/toyota-corolla-2019-85000",
            'description': "Hebrew query with Yad2 link"
        },
        {
            'message': "Heinrich, check this out: https://yad2.co.il/vehicles/item/12345",
            'description': "English query with Yad2 link"  
        },
        
        # Car Valuation Queries
        {
            'message': "כמה שווה טויוטה קורולה 2019 עם 60 אלף קמ?",
            'description': "Hebrew car valuation query"
        },
        {
            'message': "Is 85,000 ILS good for a 2019 Honda Civic with 45K km?",
            'description': "English buying advice query"
        },
        {
            'message': "האם 90,000 ₪ זה מחיר הוגן לטויוטה קורולה 2019?",
            'description': "Hebrew buyer query with specific price"
        },
        {
            'message': "מוכר את הטויוטה קורולה 2019 שלי - איזה מחיר לבקש?",
            'description': "Hebrew seller query"
        },
        
        # General Car Questions
        {
            'message': "אני מחפש רכב עד 90 אלף - יש המלצות?",
            'description': "General car shopping query"
        },
        {
            'message': "What should I look for when buying a used car?",
            'description': "General car advice query"
        },
        
        # Non-car Messages (should return None)
        {
            'message': "Hello, how are you today?",
            'description': "Non-car related message"
        },
        {
            'message': "מה המזג אוויר היום?",
            'description': "Weather query in Hebrew"
        }
    ]
    
    for i, test_case in enumerate(test_messages, 1):
        print(f"📱 **Test {i}: {test_case['description']}**")
        print(f"Message: \"{test_case['message']}\"")
        print("-" * 50)
        
        response = process_whatsapp_car_message(test_case['message'])
        
        if response:
            print("✅ Heinrich Response:")
            print(response)
        else:
            print("❌ No response (not car-related)")
        
        print("\n" + "="*60 + "\n")

def demo_buyer_vs_seller_intelligence():
    """Demonstrate buyer vs seller intelligence detection"""
    
    print("🧠 Buyer vs Seller Intelligence Demo")
    print("="*50)
    
    scenarios = [
        {
            'query': "האם 85,000 ₪ זה מחיר טוב לטויוטה קורולה 2019?",
            'expected': "BUYER - Price evaluation and negotiation advice"
        },
        {
            'query': "כמה שווה הטויוטה קורולה 2019 שלי עם 60K קמ?", 
            'expected': "SELLER - Pricing strategy and market timing"
        },
        {
            'query': "מה המחיר של טויוטה קורולה 2019 בשוק?",
            'expected': "GENERAL - Market overview"
        }
    ]
    
    for scenario in scenarios:
        print(f"Query: {scenario['query']}")
        print(f"Expected: {scenario['expected']}")
        
        response = process_whatsapp_car_message(scenario['query'])
        if response:
            intent_type = "BUYER" if "קונה" in response else ("SELLER" if "מוכר" in response else "GENERAL")
            print(f"Detected: {intent_type}")
            print("✅ Correct!" if intent_type.lower() in scenario['expected'].lower() else "❌ Mismatch")
        else:
            print("❌ No detection")
        
        print("-" * 30)

def demo_language_detection():
    """Demonstrate Hebrew vs English language detection"""
    
    print("🌐 Language Detection Demo") 
    print("="*40)
    
    test_cases = [
        ("כמה שווה טויוטה קורולה?", "Hebrew"),
        ("What's my Toyota Corolla worth?", "English"),
        ("Toyota Corolla 2019 כמה שווה?", "Mixed (should be Hebrew)"),
        ("מה המחיר של Honda Civic?", "Mixed (should be Hebrew)")
    ]
    
    from whatsapp_integration import WhatsAppCarAnalyzer
    analyzer = WhatsAppCarAnalyzer()
    
    for message, expected in test_cases:
        is_hebrew = analyzer._is_hebrew_message(message)
        detected = "Hebrew" if is_hebrew else "English"
        
        print(f"Message: \"{message}\"")
        print(f"Expected: {expected} | Detected: {detected}")
        print("✅ Correct!" if expected.startswith(detected) else "❌ Mismatch")
        print("-" * 30)

if __name__ == "__main__":
    print("🎯 Heinrich Car Valuation - Complete WhatsApp Demo\n")
    
    # Run all demos
    demo_whatsapp_messages()
    
    print("\n" + "🧠 ADVANCED DEMOS" + "\n")
    demo_buyer_vs_seller_intelligence()
    
    print("\n")
    demo_language_detection()
    
    print("\n🎉 Demo Complete!")
    print("💡 Ready to integrate with your WhatsApp bot or OpenClaw instance!")
    print("\n📋 Next Steps:")
    print("1. Set up your Apify API token for live market data")
    print("2. Integrate with your WhatsApp webhook") 
    print("3. Test with real Yad2 links")
    print("4. Customize responses for your use case")