#!/usr/bin/env python3
"""
🎯 Heinrich Car Intelligence - Quick 2-Minute Demo
הדגמה מהירה של 2 דקות - מושלם לחברים!

Quick showcase of Heinrich's core features
"""

import time
import sys

def quick_header():
    """Quick header"""
    print("\n" + "="*50)
    print("🎩 HEINRICH CAR INTELLIGENCE 🚗")
    print("="*50)
    print("🇮🇱 Israeli Car Market AI Platform")
    print("⚡ Real-time Yad2 Analysis")
    print("📱 WhatsApp Ready")
    print("🤖 Smart Buyer/Seller Intelligence")
    print()

def demo_1_whatsapp_link():
    """Demo 1: WhatsApp link analysis"""
    print("📱 DEMO 1: WhatsApp Link Analysis")
    print("-" * 40)
    
    print("💬 User sends: 'Heinrich, מה דעתך על זה?'")
    print("📎 + Yad2 link: https://yad2.co.il/vehicles/cars/toyota-corolla-85000")
    print()
    
    print("🔍 Heinrich analyzing...")
    time.sleep(1)
    print("   ✅ Car found: 2019 Toyota Corolla")
    print("   ✅ Price: 85,000 ₪, 62K km, Tel Aviv")
    print("   ✅ Market analysis: Fair deal")
    print("   ✅ Recommendation: Try 82,000 ₪")
    print()
    
    print("📤 Heinrich responds in Hebrew:")
    print("   '🚗 מצאתי: טויוטה קורולה 2019'")
    print("   '💰 המחיר: 85,000 ₪ - הוגן אבל יש מקום למיקוח'")
    print("   '🎯 נסה להגיע ל-82,000 ₪'")
    print()

def demo_2_buyer_advice():
    """Demo 2: Smart buyer advice"""
    print("🛒 DEMO 2: Smart Buyer Intelligence")
    print("-" * 40)
    
    print("💬 User asks: 'האם 90,000 ₪ זה מחיר טוב לקורולה 2019?'")
    print()
    
    print("🤖 Heinrich's AI analyzing...")
    time.sleep(1)
    print("   ✅ Intent detected: Buyer seeking advice")
    print("   ✅ Market position: 6% above median")
    print("   ✅ Alternative options: 4 similar cars cheaper")
    print()
    
    print("📤 Heinrich's smart response:")
    print("   '📊 המחיר 6% מעל החציון'")
    print("   '💬 נסה למקח ל-85,500 ₪'") 
    print("   '🎯 יש 4 רכבים דומים זולים יותר'")
    print("   '⏰ זמן טוב לקנות את הדגם הזה'")
    print()

def demo_3_seller_strategy():
    """Demo 3: Smart seller strategy"""
    print("💰 DEMO 3: Smart Seller Strategy")
    print("-" * 40)
    
    print("💬 User asks: 'כמה לבקש עבור הקורולה 2019 שלי?'")
    print()
    
    print("📈 Heinrich calculating strategies...")
    time.sleep(1)
    print("   ✅ Intent detected: Seller seeking strategy")
    print("   ✅ Market timing: Good demand")
    print("   ✅ 3-tier pricing calculated")
    print()
    
    print("📤 Heinrich's strategic advice:")
    print("   '💨 מכירה מהירה: 77,500 ₪ (תוך שבועיים)'")
    print("   '📊 מחיר שוק: 85,000 ₪ (חודש-שניים)'")
    print("   '🚀 מחיר אופטימי: 89,500 ₪ (עד 4 חודשים)'")
    print("   '⏰ זמן טוב למכירה!'")
    print()

def demo_advantages():
    """Demo advantages over competition"""
    print("🥇 WHY HEINRICH ROCKS")
    print("-" * 40)
    
    advantages = [
        ("⚡ Real-time data", "Yad2 live scraping vs static databases"),
        ("📱 WhatsApp native", "Just send a link vs complex forms"),
        ("🇮🇱 Hebrew/English", "Natural bilingual support"),
        ("🤖 AI intelligence", "Smart buyer/seller advice"),
        ("💰 Free tier", "100-500 valuations/month free"),
        ("🎯 Israeli focused", "Built specifically for Israeli market")
    ]
    
    for advantage, description in advantages:
        print(f"   {advantage} {description}")
        time.sleep(0.3)
    print()

def demo_technical():
    """Quick technical demo"""
    print("🔬 TECHNICAL FEATURES")
    print("-" * 40)
    
    features = [
        "📊 Price correlation analysis (-0.70 typical)",
        "📍 Geographic impact modeling (+5% Tel Aviv)",
        "🏷️  Premium feature detection (leather, sunroof)",
        "⏰ Data freshness < 24 hours",
        "🎯 87% average confidence score",
        "🚀 8.3 second average response time"
    ]
    
    for feature in features:
        print(f"   {feature}")
        time.sleep(0.2)
    print()

def demo_installation():
    """Installation demo"""
    print("📦 SUPER EASY SETUP")
    print("-" * 40)
    
    print("🚀 Total time: 3 minutes!")
    print()
    
    steps = [
        "1. 📋 Get free Apify account ($5 credit)",
        "2. 📥 git clone the Heinrich repository", 
        "3. 🔧 pip install requirements",
        "4. 🔑 export APIFY_API_TOKEN=your_token",
        "5. ✅ python3 demo.py"
    ]
    
    for step in steps:
        print(f"   {step}")
        time.sleep(0.4)
    print()
    print("🎉 Ready to analyze cars!")
    print()

def main():
    """Main quick demo"""
    quick_header()
    
    print("🎯 2-MINUTE HEINRICH DEMO")
    print("Let's see Heinrich in action!")
    print()
    
    input("Press ENTER to start demo... ")
    
    demo_1_whatsapp_link()
    input("Press ENTER for next demo... ")
    
    demo_2_buyer_advice()
    input("Press ENTER for next demo... ")
    
    demo_3_seller_strategy()
    input("Press ENTER for advantages... ")
    
    demo_advantages()
    input("Press ENTER for technical features... ")
    
    demo_technical()
    input("Press ENTER for installation... ")
    
    demo_installation()
    
    print("🎉 DEMO COMPLETE!")
    print("="*50)
    print("🎩 Heinrich Car Intelligence Platform")
    print("📱 Ready for real-world use")
    print("🚀 Questions? Let's chat!")
    print("💌 Want to try? We'll help you set it up!")
    print("="*50)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted. Thanks for watching Heinrich! 🎩")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("📞 No worries - let's show you manually!")