# Import necessary libraries
from flask import Flask, render_template, request, redirect, url_for, jsonify
import json
import os

# Initialize the Flask application
# __name__ helps Flask determine the root path of the application
app = Flask(__name__)

# Set a secret key for session management (required for flash messages)
app.secret_key = os.environ.get('SESSION_SECRET', 'dev-secret-key-change-in-production')

# File path for storing product data
PRODUCTS_FILE = 'products.json'

# ========== HELPER FUNCTIONS ==========

def load_products():
    """
    Load products from the JSON file.
    Returns a list of product dictionaries.
    If the file doesn't exist or is empty, returns an empty list.
    """
    try:
        with open(PRODUCTS_FILE, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_products(products):
    """
    Save products to the JSON file.
    Takes a list of product dictionaries and writes them to products.json
    """
    with open(PRODUCTS_FILE, 'w') as file:
        json.dump(products, file, indent=2)

def filter_products(products, search_query='', category='', min_price=0, max_price=999999):
    """
    Filter products based on search query, category, and price range.
    
    Parameters:
    - products: List of all products
    - search_query: Keywords to search in product name, brand, or description
    - category: Product category (mobiles, laptops, earphones, tvs)
    - min_price: Minimum price filter
    - max_price: Maximum price filter
    
    Returns: Filtered list of products
    """
    filtered = products
    
    # Filter by search query (case-insensitive search in name, brand, and description)
    if search_query:
        search_query = search_query.lower()
        filtered = [
            p for p in filtered 
            if search_query in p['name'].lower() 
            or search_query in p['brand'].lower() 
            or search_query in p.get('description', '').lower()
        ]
    
    # Filter by category
    if category:
        filtered = [p for p in filtered if p['category'] == category]
    
    # Filter by price range
    filtered = [
        p for p in filtered 
        if min_price <= p['price'] <= max_price
    ]
    
    return filtered

def get_recommendations(product_id, products, limit=4):
    """
    Get product recommendations based on a given product.
    Recommends products from the same category or similar price range.
    
    Parameters:
    - product_id: ID of the current product
    - products: List of all products
    - limit: Maximum number of recommendations to return
    
    Returns: List of recommended products
    """
    # Find the current product
    current_product = next((p for p in products if p['id'] == product_id), None)
    
    if not current_product:
        return []
    
    # First, try to find products in the same category
    same_category = [
        p for p in products 
        if p['category'] == current_product['category'] 
        and p['id'] != product_id
    ]
    
    # If we have enough recommendations from the same category, return them
    if len(same_category) >= limit:
        return same_category[:limit]
    
    # Otherwise, add products with similar price range (within 20% difference)
    price = current_product['price']
    price_min = price * 0.8
    price_max = price * 1.2
    
    similar_price = [
        p for p in products 
        if price_min <= p['price'] <= price_max 
        and p['id'] != product_id
        and p not in same_category
    ]
    
    # Combine recommendations and limit to the specified number
    recommendations = same_category + similar_price
    return recommendations[:limit]

def get_products_by_category(products, limit_per_category=5):
    """
    Get a limited number of products from each category for the homepage.
    
    Parameters:
    - products: List of all products
    - limit_per_category: Number of products to show per category
    
    Returns: Dictionary with categories as keys and product lists as values
    """
    categories = ['mobiles', 'laptops', 'earphones', 'tvs']
    categorized = {}
    
    for category in categories:
        category_products = [p for p in products if p['category'] == category]
        # Sort by rating (highest first) and limit
        category_products.sort(key=lambda x: x['rating'], reverse=True)
        categorized[category] = category_products[:limit_per_category]
    
    return categorized

# ========== FLASK ROUTES ==========

@app.route('/')
def index():
    """
    Homepage route.
    Displays product categories and top-rated products from each category.
    """
    products = load_products()
    
    # Get 4-5 products per category to display on homepage
    categorized_products = get_products_by_category(products, limit_per_category=5)
    
    # Count total products
    total_products = len(products)
    
    return render_template('index.html', 
                          categorized_products=categorized_products,
                          total_products=total_products)

@app.route('/search', methods=['GET', 'POST'])
def search():
    """
    Search and filter route.
    Handles both GET requests (category filtering) and POST requests (search queries).
    Displays filtered results on the results page.
    """
    products = load_products()
    
    # Get search parameters from either POST form or GET query string
    if request.method == 'POST':
        search_query = request.form.get('search_query', '')
        category = request.form.get('category', '')
    else:
        search_query = request.args.get('q', '')
        category = request.args.get('category', '')
    
    # Get price range filters (optional)
    min_price = request.args.get('min_price', 0, type=int)
    max_price = request.args.get('max_price', 999999, type=int)
    
    # Apply filters
    filtered_products = filter_products(
        products, 
        search_query=search_query,
        category=category,
        min_price=min_price,
        max_price=max_price
    )
    
    # Sort products by rating (highest first)
    filtered_products.sort(key=lambda x: x['rating'], reverse=True)
    
    return render_template('results.html',
                          products=filtered_products,
                          search_query=search_query,
                          category=category,
                          total_results=len(filtered_products))

@app.route('/category/<category_name>')
def category(category_name):
    """
    Category-specific route.
    Displays all products in a specific category.
    """
    products = load_products()
    filtered_products = filter_products(products, category=category_name)
    
    # Sort by rating
    filtered_products.sort(key=lambda x: x['rating'], reverse=True)
    
    return render_template('results.html',
                          products=filtered_products,
                          search_query='',
                          category=category_name,
                          total_results=len(filtered_products))

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    """
    Product detail route with recommendations.
    Shows detailed information about a product and suggests similar products.
    """
    products = load_products()
    
    # Find the specific product
    product = next((p for p in products if p['id'] == product_id), None)
    
    if not product:
        return "Product not found", 404
    
    # Get recommendations
    recommendations = get_recommendations(product_id, products, limit=4)
    
    return render_template('results.html',
                          products=[product],
                          recommendations=recommendations,
                          search_query='',
                          category='',
                          total_results=1,
                          show_recommendations=True)

@app.route('/add-product', methods=['GET', 'POST'])
def add_product():
    """
    Add new product route.
    Allows users to add new products to the catalog.
    GET: Shows the add product form
    POST: Processes the form and adds the product to products.json
    """
    if request.method == 'POST':
        # Load existing products
        products = load_products()
        
        # Generate a new product ID (max existing ID + 1)
        new_id = max([p['id'] for p in products], default=0) + 1
        
        # Create new product from form data
        new_product = {
            'id': new_id,
            'name': request.form.get('name'),
            'category': request.form.get('category'),
            'brand': request.form.get('brand'),
            'price': int(request.form.get('price', 0)),
            'rating': float(request.form.get('rating', 4.0)),
            'description': request.form.get('description', ''),
            'image': request.form.get('image', 'https://via.placeholder.com/300x200?text=New+Product')
        }
        
        # Add to products list
        products.append(new_product)
        
        # Save to file
        save_products(products)
        
        # Redirect to the newly added product's category
        return redirect(url_for('category', category_name=new_product['category']))
    
    # GET request: show the form
    return render_template('add_product.html')

# ========== ERROR HANDLERS ==========

@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors with a custom message"""
    return render_template('results.html', 
                          products=[], 
                          search_query='',
                          category='',
                          total_results=0,
                          error_message="Page not found"), 404

# ========== RUN THE APPLICATION ==========

if __name__ == '__main__':
    # Run the Flask development server
    # host='0.0.0.0' makes the server accessible from outside the container
    # port=5000 is the standard Flask port (Replit requires this)
    # debug=True enables auto-reload and detailed error messages
    app.run(host='0.0.0.0', port=5000, debug=True)
