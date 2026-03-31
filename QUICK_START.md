# 🚀 Heinrich Car Valuation - Quick Start (3 Minutes)

**Get Heinrich analyzing Israeli car prices in under 3 minutes!**

## ⚡ Super Quick Setup

### Step 1: Get Apify Token (30 seconds)
1. Go to [apify.com](https://apify.com) → Sign up (free)
2. Settings → API tokens → Copy your token

### Step 2: Install Skill (60 seconds)
```bash
# In your terminal:
cd ~/.openclaw/workspace/skills/
git clone https://github.com/omersalomon/heinrich-car-valuation car-valuation
export APIFY_API_TOKEN="paste_your_token_here"
pip install -r car-valuation/requirements.txt
```

### Step 3: Test It! (30 seconds)
```bash
python3 car-valuation/examples/whatsapp_demo.py
```

**See "✅ All systems operational!"?** → **You're ready!**

---

## 🎯 How to Use

### 📱 In WhatsApp with Heinrich:
```
You: "Heinrich, מה דעתך? https://yad2.co.il/ad/corolla-85000"
Heinrich: "🚗 מצאתי: Toyota Corolla 2019 - מנתח השוק..."
```

### 💬 Ask Heinrich about car values:
```
Hebrew: "כמה שווה טויוטה קורולה 2019?"
English: "What's my Honda Civic 2018 worth?"
Buyer: "האם 85,000 ₪ זה מחיר טוב?"
Seller: "כמה לבקש עבור הרכב שלי?"
```

---

## 🆘 Problems?

### ❌ "Token not found"
```bash
export APIFY_API_TOKEN="your_actual_token_here"
echo 'export APIFY_API_TOKEN="your_token"' >> ~/.bashrc
```

### ❌ "Module not found"  
```bash
pip install requests beautifulsoup4
```

### ❌ Heinrich doesn't respond
- Restart OpenClaw after installing
- Try: "Heinrich, כמה שווה טויוטה קורולה 2019?"

---

## 💡 What You Get

✅ **Real-time Yad2 data** (always current prices)
✅ **Smart analysis** (price correlations, trends)  
✅ **Hebrew/English** (automatic language detection)
✅ **Buyer advice** (negotiate or good deal?)
✅ **Seller strategy** (quick sale vs optimistic pricing)
✅ **WhatsApp links** (paste any Yad2 URL → instant analysis)

**🎉 That's it! You now have AI-powered car valuation in Hebrew/English!**

*Questions? Join OpenClaw Discord or create GitHub issue*