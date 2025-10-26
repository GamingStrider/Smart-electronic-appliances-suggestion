import json
from flask import Flask, render_template, request, jsonify, abort

# Initialize the Flask application
app = Flask(__name__)

# Global list to hold the product data
PRODUCTS = []

# --- Data Loading Function ---
def load_products():
    """Loads product data from products.json."""
    global PRODUCTS
    try:
        # NOTE: Agar aapka products.json file bilkul naye data se bhara hai,
        # aur aapne naye keys (jaise 'storage') add nahi kiye hain, toh
        # ho sakta hai ki yeh data loading mein error de. Dummy keys (storage)
        # ko hum yahan default value de rahe hain taki error na aaye.
        with open('products.json', 'r') as f:
            data = json.load(f)
            # Default values for any missing keys needed by filters
            for p in data:
                p['storage'] = p.get('storage', 'N/A')
                p['processor'] = p.get('processor', 'N/A')
                p['camera'] = p.get('camera', 'N/A')
                p['battery'] = p.get('battery', 'N/A')
            PRODUCTS = data
    except Exception as e:
        print(f"Error loading products.json: {e}. Starting with empty list.")
        PRODUCTS = []

# Load products when the application starts
load_products()

# --- Helper Functions ---

def is_in_price_range(price, price_range_key):
    """Checks if a price falls within a specific predefined range."""
    ranges = {
        'below_20k': (0, 20000),
        '20k_50k': (20000, 50000),
        '50k_100k': (50000, 100000),
        'over_100k': (100000, float('inf'))
    }
    if price_range_key in ranges:
        min_price, max_price = ranges[price_range_key]
        return min_price <= price < max_price
    return False

def matches_filter(product, key, selections):
    """Checks if a product's attribute matches any selected option."""
    if not selections:
        return True
    return product.get(key) in selections

# --- Homepage Route ---
@app.route('/')
def index():
    """Renders the homepage with categories and unique filter options."""
    
    # Dynamically extract unique values for filters
    all_brands = sorted(list(set(p['brand'] for p in PRODUCTS)))
    all_processors = sorted(list(set(p['processor'] for p in PRODUCTS if p['processor'] != 'N/A')))
    all_cameras = sorted(list(set(p['camera'] for p in PRODUCTS if p['camera'] != 'None')))
    all_batteries = sorted(list(set(p['battery'] for p in PRODUCTS if p['battery'] != 'N/A')))
    all_storage = sorted(list(set(p['storage'] for p in PRODUCTS if p['storage'] != 'N/A')))

    price_ranges = {
        'below_20k': 'Below ₹20,000',
        '20k_50k': '₹20,000 - ₹50,000',
        '50k_100k': '₹50,000 - ₹1,00,000',
        'over_100k': 'Over ₹1,00,000'
    }
    
    categories = ['mobile', 'laptop', 'tv', 'earphone']
    
    return render_template('index.html', 
                           categories=categories,
                           brands=all_brands,
                           processors=all_processors,
                           cameras=all_cameras,
                           batteries=all_batteries,
                           storage_options=all_storage,
                           price_ranges=price_ranges)

# --- Product Search/Filter Route (Backend Logic) ---
@app.route('/api/search', methods=['GET'])
@app.route('/results', methods=['GET'])
def search_products():
    """Handles search queries and multi-criteria filtering."""
    
    # Get inputs
    query = request.args.get('query', '').strip().lower()
    # 💥 YAHAN NAYA INPUT AAYEGA 💥
    selected_category = request.args.get('category', '').strip().lower() 
    
    selected_brands = request.args.getlist('brand')
    selected_processors = request.args.getlist('processor')
    selected_cameras = request.args.getlist('camera')
    selected_batteries = request.args.getlist('battery')
    selected_storage = request.args.getlist('storage')
    selected_price_ranges = request.args.getlist('price_range')
    
    is_ajax = request.args.get('is_ajax', 'false').lower() == 'true'

    # Start with all products
    filtered_products = PRODUCTS
    
    # 1. Apply Keyword Search Filter
    if query:
        # Agar query mein category ka naam hai toh hum query ko category mein use kar lenge
        if query in ['mobile', 'laptop', 'tv', 'earphone']:
             selected_category = query
        else:
            filtered_products = [
                p for p in filtered_products 
                if query in p['name'].lower() 
                or query in p['brand'].lower()
                or query in p['category'].lower()
            ]

    # 2. 💥 YAHAN HUM CATEGORY FILTER SABSE PEHLE APPLY KARTE HAIN 💥
    if selected_category:
        filtered_products = [
            p for p in filtered_products 
            if p['category'].lower() == selected_category
        ]

    # 3. Apply Multi-Criteria Filters (Ab yeh filters sirf selected category par lagenge)

    # A. Brand Filter
    filtered_products = [p for p in filtered_products if matches_filter(p, 'brand', selected_brands)]

    # B. Processor Filter
    if selected_processors:
        filtered_products = [
            p for p in filtered_products 
            if p['category'] not in ['tv', 'earphone'] and matches_filter(p, 'processor', selected_processors)
        ]

    # C. Camera Filter (Mobile only)
    if selected_cameras:
        filtered_products = [
            p for p in filtered_products 
            if p['category'] != 'mobile' or matches_filter(p, 'camera', selected_cameras)
        ]
        
    # D. Battery Filter (Mobile only)
    if selected_batteries:
        filtered_products = [
            p for p in filtered_products 
            if p['category'] != 'mobile' or matches_filter(p, 'battery', selected_batteries)
        ]
        
    # E. Storage Filter (Mobile/Laptop)
    if selected_storage:
        filtered_products = [
            p for p in filtered_products 
            if p['category'] not in ['tv', 'earphone'] and matches_filter(p, 'storage', selected_storage)
        ]
        
    # F. Price Range Filter
    if selected_price_ranges:
        filtered_products = [
            p for p in filtered_products
            if any(is_in_price_range(p['price'], pr) for pr in selected_price_ranges)
        ]

    # Decide output format
    if is_ajax:
        return jsonify(filtered_products)
    else:
        return render_template('results.html', 
                               query=query, 
                               products=filtered_products,
                               category=selected_category) # 💥 YEH RETURN KARNA ZAROORI HAI

# --- Product Detail Route ---
@app.route('/product/<int:product_id>')
def product_detail(product_id):
    # ... (No change needed here)
    product = next((p for p in PRODUCTS if p['id'] == product_id), None)
    
    if product is None:
        abort(404)
        
    recommendations = [
        p for p in PRODUCTS 
        if p['category'] == product['category'] and p['id'] != product_id
    ][:4]
        
    return render_template('product_detail.html', 
                           product=product,
                           recommendations=recommendations)

# --- Error Handler for 404 ---
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True)