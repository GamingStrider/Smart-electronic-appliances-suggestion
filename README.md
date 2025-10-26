# Smart Electronics Suggestion Website

A beginner-friendly Python Flask web application for electronics product discovery and recommendations. Perfect for B.Tech 2nd-year projects!

## Features

✅ **Search Functionality** - Search products by name, brand, or description  
✅ **Category Browsing** - Browse Mobiles, Laptops, Earphones, and TVs  
✅ **Smart Recommendations** - Get similar product suggestions based on category and price  
✅ **Add Products** - Dynamically add new products to the catalog  
✅ **Responsive Design** - Clean, modern UI using Bootstrap 5  
✅ **Product Filtering** - Filter by keywords, category, and price range  

## Project Structure

```
/project
├── app.py                  # Main Flask application
├── products.json           # Product database
├── requirements.txt        # Python dependencies
├── templates/              # HTML templates
│   ├── index.html         # Homepage
│   ├── results.html       # Search results
│   └── add_product.html   # Add product form
└── static/
    └── style.css          # Custom styles
```

## Running Locally

The Flask app runs automatically on port 5000. Just click the web preview to see your website!

## Deploying to Render

Follow these steps to deploy your website to Render:

### Step 1: Prepare Your Code
1. Make sure all files are pushed to GitHub (or GitLab/Bitbucket)
2. Your repository should include:
   - `app.py`
   - `requirements.txt`
   - `products.json`
   - `templates/` folder
   - `static/` folder

### Step 2: Create a Web Service on Render
1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub/GitLab account
4. Select your repository

### Step 3: Configure Your Service
Fill in the following settings:

- **Name**: `smart-electronics` (or any name you prefer)
- **Environment**: `Python 3`
- **Region**: Choose the closest to your location
- **Branch**: `main` (or your default branch)
- **Build Command**: 
  ```
  pip install -r requirements.txt
  ```
- **Start Command**: 
  ```
  gunicorn app:app --bind 0.0.0.0:$PORT
  ```

### Step 4: Set Environment Variables
1. Scroll down to **Environment Variables**
2. Add a new variable:
   - **Key**: `SESSION_SECRET`
   - **Value**: (generate a random string, e.g., `your-secret-key-here-12345`)

### Step 5: Deploy
1. Click **"Create Web Service"**
2. Wait for Render to build and deploy (usually 2-3 minutes)
3. Once deployed, you'll get a live URL like: `https://smart-electronics.onrender.com`

### Step 6: Access Your Website
Click on the provided URL to see your live website! 🎉

## Important Notes for Render Deployment

- **Free Tier**: Render offers a free tier, but services may spin down after inactivity
- **Database**: Products are stored in `products.json` (file-based storage)
- **HTTPS**: Render automatically provides HTTPS for your website
- **Custom Domain**: You can add a custom domain in Render settings (paid feature)

## Tech Stack

- **Backend**: Python 3.11, Flask 3.0.0
- **Frontend**: HTML5, Bootstrap 5, CSS3
- **Server**: Gunicorn (production WSGI server)
- **Database**: JSON file storage

## Code Structure (For Learning)

The code is heavily commented to help you understand:
- Flask routing and view functions
- Template rendering with Jinja2
- JSON data handling
- Search and filter algorithms
- Recommendation logic based on similarity

## Future Enhancements

- Integrate real electronics API (Fake Store API)
- Add user authentication and wishlists
- Implement shopping cart functionality
- Add product comparison feature
- Use a real database (PostgreSQL, MongoDB)

---

**Created by**: B.Tech Student  
**Framework**: Flask  
**Year**: 2025
