#!/usr/bin/env python3
"""
Enhanced Hebrew Parser for Car Valuation
Fixed version with proper year parsing and model recognition
"""

import re

def parse_hebrew_car_query_fixed(user_message: str) -> dict:
    """
    Enhanced parser with Hebrew support - FIXED VERSION
    """
    
    # FIXED: Extract year patterns (Hebrew numerals or English)
    year_patterns = [
        r'משנת\s*(\d{4})',        # Hebrew: משנת 2019
        r'מ[־\-](\d{4})',         # Hebrew: מ-2019  
        r'שנת\s*(\d{4})',         # Hebrew: שנת 2018
        r'ב(\d{4})',              # Hebrew: ב2019
        r'\b((?:19|20)\d{2})\b',  # English: 2019, 2020 (with word boundaries)
    ]
    
    year = None
    for pattern in year_patterns:
        match = re.search(pattern, user_message)
        if match:
            year = int(match.group(1))
            break
    
    # Hebrew to English manufacturer mapping (expanded)
    hebrew_manufacturers = {
        'טויוטה': 'Toyota',
        'הונדה': 'Honda', 
        'יונדאי': 'Hyundai',
        'יונדיי': 'Hyundai',  # Alternative spelling
        'ניסאן': 'Nissan',
        'מאזדה': 'Mazda',
        'סובארו': 'Subaru',
        'פולקסווגן': 'Volkswagen',
        'ב.מ.וו': 'BMW',
        'ב מ וו': 'BMW',
        'ביאמוו': 'BMW',
        'מרצדס': 'Mercedes',
        'מרצדס-בנץ': 'Mercedes',
        'אאודי': 'Audi',
        'פז\'ו': 'Peugeot',
        'פזו': 'Peugeot',
        'רנו': 'Renault',
        'פורד': 'Ford',
        'שברולט': 'Chevrolet',
        'פיאט': 'Fiat',
        'שקודה': 'Skoda',
        'סיאט': 'SEAT',
        'קיה': 'Kia'
    }
    
    # EXPANDED: Hebrew to English model mapping  
    hebrew_models = {
        # Toyota
        'קורולה': 'Corolla',
        'קמרי': 'Camry', 
        'פריוס': 'Prius',
        'יאריס': 'Yaris',
        'רב-4': 'RAV4',
        'רב4': 'RAV4',
        
        # Honda
        'סיוויק': 'Civic',
        'אקורד': 'Accord',
        'סי-אר-וי': 'CR-V',
        
        # Hyundai
        'אלנטרה': 'Elantra',
        'טוסון': 'Tucson',
        'קונה': 'Kona',
        
        # Kia
        'פיקנטו': 'Picanto',
        'ריו': 'Rio',
        'סיד': 'Ceed',
        'ספורטג\'': 'Sportage',
        'סורנטו': 'Sorento',
        
        # Volkswagen
        'פולו': 'Polo',
        'גולף': 'Golf',
        'ג\'טה': 'Jetta',
        'פאסאט': 'Passat',
        'טיגואן': 'Tiguan',
        
        # Nissan
        'מיקרה': 'Micra',
        'סנטרה': 'Sentra',
        'קשקאי': 'Qashqai',
        'ג\'וק': 'Juke',
        
        # BMW  
        'סדרה 1': 'Series 1',
        'סדרה 3': 'Series 3',
        'סדרה 5': 'Series 5',
        'סדרה 7': 'Series 7',
        
        # Mercedes
        'מחלקה A': 'A-Class',
        'מחלקה C': 'C-Class', 
        'מחלקה E': 'E-Class',
        'מחלקה S': 'S-Class',
        
        # Mazda - FIXED
        'מאזדה 3': '3',
        'מאזדה3': '3',
        'מאזדה 6': '6',
        'מאזדה6': '6',
        
        # Others
        'איביזה': 'Ibiza',
        'ליאון': 'Leon',
        'אטקה': 'Ateca',
        'פאביה': 'Fabia',
        'אוקטביה': 'Octavia',
        'סופרב': 'Superb',
        'קודיאק': 'Kodiaq',
        'פנדה': 'Panda',
        'פונטו': 'Punto',
        'טיפו': 'Tipo',
        'פיאסטה': 'Fiesta',
        'פוקוס': 'Focus',
        'מונדיאו': 'Mondeo',
    }
    
    message_lower = user_message.lower()
    
    # Find manufacturer (Hebrew or English)
    manufacturer = None
    for hebrew_name, english_name in hebrew_manufacturers.items():
        if hebrew_name in user_message:
            manufacturer = english_name
            break
    
    # Fallback to English manufacturers
    if not manufacturer:
        english_manufacturers = ['toyota', 'honda', 'hyundai', 'nissan', 'mazda', 'subaru',
                                'volkswagen', 'bmw', 'mercedes', 'audi', 'peugeot', 'renault',
                                'ford', 'chevrolet', 'fiat', 'skoda', 'seat', 'kia']
        
        for mfg in english_manufacturers:
            if mfg in message_lower:
                manufacturer = mfg.title()
                break
    
    # Find model (Hebrew or English) - check longer patterns first
    model = None
    sorted_hebrew_models = sorted(hebrew_models.items(), key=lambda x: len(x[0]), reverse=True)
    
    for hebrew_name, english_name in sorted_hebrew_models:
        if hebrew_name in user_message:
            model = english_name
            break
    
    # Fallback to English models  
    if not model:
        english_models = {
            'corolla': 'Corolla', 'camry': 'Camry', 'prius': 'Prius',
            'civic': 'Civic', 'accord': 'Accord', 'crv': 'CR-V', 'cr-v': 'CR-V',
            'i30': 'i30', 'i20': 'i20', 'elantra': 'Elantra', 'tucson': 'Tucson',
            'golf': 'Golf', 'polo': 'Polo', 'passat': 'Passat'
        }
        
        # Check longer patterns first for English too
        sorted_english_models = sorted(english_models.items(), key=lambda x: len(x[0]), reverse=True)
        for model_key, model_name in sorted_english_models:
            if model_key in message_lower:
                model = model_name
                break
    
    # Extract mileage (Hebrew patterns) - FIXED patterns
    km_patterns = [
        # Hebrew patterns  
        r'(\d+)\s*אלף\s*ק[״מ]*',         # "50 אלף קמ" or "50 אלף ק״מ"
        r'(\d+)[\s,]*k\s*ק[״מ]*',        # "50K קמ" 
        r'(\d+),(\d{3})\s*ק[״מ]*',       # "50,000 קמ"
        r'(\d{4,5})\s*ק[״מ]*',           # "50000 קמ"
        r'עם\s*(\d+)\s*אלף',            # "עם 50 אלף"
        # English patterns (keep existing)
        r'(\d+)[\s,]*k\s*km',            # "45K km"
        r'(\d+),(\d{3})\s*km',           # "45,000 km"
        r'(\d{4,5})\s*km',               # "45000 km"
        r'(\d+)[\s,]*thousand\s*km'      # "45 thousand km"
    ]
    
    km = None
    for pattern in km_patterns:
        match = re.search(pattern, message_lower)
        if match:
            if 'אלף' in pattern or 'k' in pattern or 'thousand' in pattern:
                km = int(match.group(1)) * 1000
            elif ',' in pattern and len(match.groups()) > 1:
                # Handle "50,000" format
                km = int(match.group(1)) * 1000 + int(match.group(2))
            else:
                # Handle simple numbers
                km = int(match.group(1))
            break
    
    return {
        'year': year,
        'manufacturer': manufacturer, 
        'model': model,
        'km': km,
        'original_query': user_message,
        'language': 'hebrew' if any(ord(char) > 127 for char in user_message) else 'english'
    }

def test_fixed_hebrew_parsing():
    """Test the fixed Hebrew parsing"""
    
    print("🔧 **FIXED HEBREW PARSING TESTS**")
    print("="*60)
    
    test_queries = [
        "כמה שווה טויוטה קורולה 2019 שלי?",          # Should get 2019, not 20
        "מה המחיר של הונדה סיוויק משנת 2018?",        # Should get 2018
        "כמה יכול לעלות מאזדה 3 מ-2020?",            # Should recognize Mazda 3
        "בכמה נמכר ניסאן מיקרה 2017 עם 40,000 ק״מ?", # Should get full mileage
        "תעריך ב.מ.וו סדרה 3 מ-2018",                # Should recognize BMW Series 3
        "מרצדס-בנץ מחלקה C שנת 2019",                # Should recognize Mercedes C-Class
        "טויוטה קורולה ב2019 עם 60 אלף ק״מ",        # Should get year and mileage
    ]
    
    print("\n📝 **Fixed Parsing Results:**")
    for i, query in enumerate(test_queries, 1):
        parsed = parse_hebrew_car_query_fixed(query)
        
        # Format result
        result_parts = []
        if parsed['year']: result_parts.append(str(parsed['year']))
        if parsed['manufacturer']: result_parts.append(parsed['manufacturer'])
        if parsed['model']: result_parts.append(parsed['model'])
        if parsed['km']: result_parts.append(f"{parsed['km']:,} km")
        
        result_str = " ".join(result_parts) if result_parts else "❌ Parse failed"
        
        print(f"\n{i}. {query}")
        print(f"    → {result_str}")
        
        # Check if parsing improved
        if parsed['year'] and parsed['manufacturer'] and parsed['model']:
            print(f"    ✅ Complete parsing successful!")
        elif parsed['year'] and len(str(parsed['year'])) == 4:
            print(f"    ✅ Year parsing fixed!")

if __name__ == "__main__":
    test_fixed_hebrew_parsing()