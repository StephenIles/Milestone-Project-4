# Recipe Website

A Django-based recipe sharing platform where users can create, share, and discover recipes.

## User Stories

### Authentication & Profile
1. As a new user, I want to create an account so that I can share my recipes
   - **Acceptance Criteria:**
     - User can register with username, email, and password
     - Password must meet minimum security requirements
     - User receives confirmation email after registration
     - User can't register with existing username/email

2. As a registered user, I want to log in to access my personal recipe collection
   - **Acceptance Criteria:**
     - User can log in with username/email and password
     - User is redirected to home page after login
     - User can see their profile link in navigation
     - User remains logged in until they logout

3. As a user, I want to reset my password if I forget it
   - **Acceptance Criteria:**
     - User can request password reset via email
     - Reset link is valid for 24 hours
     - User can set new password after clicking reset link
     - Old password becomes invalid after reset

4. As a user, I want to view and edit my profile information
   - **Acceptance Criteria:**
     - User can view their profile details
     - User can update username and email
     - User can change their password
     - User can see their recipe collection

### Recipe Management
1. As a user, I want to create new recipes with ingredients and instructions
   - **Acceptance Criteria:**
     - User can add recipe title, description, and image
     - User can specify ingredients with quantities and units
     - User can write step-by-step instructions
     - User can set cooking time and servings
     - User can assign category and tags

2. As a user, I want to edit my existing recipes
   - **Acceptance Criteria:**
     - User can modify all recipe details
     - Only recipe owner can edit
     - Changes are saved immediately
     - Edit history is maintained

3. As a user, I want to delete recipes I no longer want to share
   - **Acceptance Criteria:**
     - User can delete their own recipes
     - Confirmation required before deletion
     - Associated comments and ratings are deleted
     - Recipe is removed from all collections

### Recipe Discovery
1. As a visitor, I want to browse all available recipes without logging in
   - **Acceptance Criteria:**
     - Public recipes are visible to all users
     - Recipes display title, image, and basic info
     - Recipes are paginated for easy browsing
     - Recipes show average rating

2. As a user, I want to search for recipes
   - **Acceptance Criteria:**
     - User can search by recipe title
     - User can search by ingredients
     - Search results are relevant and ranked
     - Search works with partial matches

3. As a user, I want to filter recipes
   - **Acceptance Criteria:**
     - Filter by cooking time (quick/medium/long)
     - Filter by number of servings
     - Filter by category
     - Multiple filters can be combined

### Recipe Interaction
1. As a user, I want to rate recipes
   - **Acceptance Criteria:**
     - User can rate from 1-5 stars
     - User can change their rating
     - One rating per user per recipe
     - Average rating is updated immediately

2. As a user, I want to comment on recipes
   - **Acceptance Criteria:**
     - User can write and post comments
     - User can edit their comments
     - User can delete their comments
     - Comments show timestamp and author

3. As a user, I want to save favorite recipes
   - **Acceptance Criteria:**
     - User can mark recipes as favorites
     - User can view all favorite recipes
     - User can remove recipes from favorites
     - Favorites are private to user

### Recipe Organization
1. As a user, I want to categorize my recipes
   - **Acceptance Criteria:**
     - User can assign one category per recipe
     - User can browse recipes by category
     - Categories show recipe count
     - Categories have descriptions

2. As a user, I want to tag my recipes
   - **Acceptance Criteria:**
     - User can add multiple tags to recipes
     - User can create new tags
     - User can remove tags
     - Tags are searchable

### Premium Features

1. As a premium user, I want access to advanced recipe features
   - **Acceptance Criteria:**
     - Scale recipe portions automatically
     - Convert measurements (metric/imperial)
     - View nutritional information for recipes
     - Print recipe cards in premium format
     - Access recipe variation suggestions

2. As a premium user, I want to create recipe collections
   - **Acceptance Criteria:**
     - Create and name custom collections
     - Add recipes to multiple collections
     - Organize recipes by occasion or theme
     - Share collections with other users
     - Export collections as PDF cookbook

3. As a premium user, I want kitchen inventory management
   - **Acceptance Criteria:**
     - Track pantry inventory
     - Add/remove items with quantities
     - Set minimum stock levels
     - Get low stock alerts
     - Suggest recipes based on available ingredients

4. As a premium user, I want meal planning and shopping features
   - **Acceptance Criteria:**
     - Create weekly meal plans
     - Generate shopping lists from meal plans
     - Add extra items to shopping list
     - Organize shopping items by category
     - Mark items as purchased

5. As a premium user, I want to access the meal planner system
   - **Acceptance Criteria:**
     - Access the weekly meal planner calendar
     - Assign recipes to meals
     - Add daily notes to meal plans
     - Generate shopping lists from meal plans
     - Export shopping lists as PDF

### Subscription Management
1. As a visitor, I want to understand premium benefits
   - **Acceptance Criteria:**
     - Clear feature comparison (free vs premium)
     - Transparent pricing
     - List of all premium features
     - FAQ section about premium features

2. As a user, I want to manage my premium subscription
   - **Acceptance Criteria:**
     - Subscribe to premium plan
     - View subscription status
     - Cancel subscription
     - View billing history
     - Update payment method

## Current Features

### User Management
- ✅ User registration and authentication
- ✅ Password reset functionality
- ✅ User profiles
- ✅ Secure login/logout system

### Recipe Management
- ✅ Create, read, update, delete (CRUD) recipes
- ✅ Image upload for recipes
- ✅ Structured ingredient storage (JSON-based)
- ✅ Cooking time and servings tracking
- ✅ Category assignment
- ✅ Tag management
- ✅ Favorite recipes system

### Social Features
- ✅ Recipe ratings (1-5 stars)
- ✅ Comment system
- ✅ Author attribution
- ✅ Favorite recipes collection
- ✅ Recipe sharing within platform

### Search & Discovery
- ✅ Advanced search functionality
  - Search by title and description
  - Filter by category
  - Filter by tags
  - Filter by cooking time
  - Filter by rating
- ✅ Category browsing
- ✅ Tag cloud
- ✅ Related recipes by tags

### Organization
- ✅ Recipe categories
- ✅ Recipe tagging system
- ✅ Personal favorites collection

### Premium Features
- ✅ Meal Planning System
  - Weekly meal planning calendar
  - Recipe assignment to meals
  - Daily notes for meal plans
  - Shopping list generation
  - PDF export for shopping lists

## Technologies Used

### Backend
- Python 3.12
- Django 5.0
- SQLite3

### Frontend
- HTML5
- CSS3
- JavaScript
- Responsive Design

## Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd recipe_website
   ```

2. Create and activate virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment:
   Create a `.env` file with:
   ```
   SECRET_KEY=your_secret_key
   DEBUG=True
   ```

5. Setup database:
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

6. Load sample data (optional):
   ```bash
   python manage.py load_recipes
   ```

7. Run development server:
   ```bash
   python manage.py runserver
   ````
## Project Structure
```
recipe_website/
├── recipes/              # Main app
├── static/              # CSS, JS, Images
├── templates/           # HTML templates
│   ├── recipes/        # Recipe templates
│   └── registration/   # Auth templates
├── media/              # User uploads
└── manage.py           # Django management script
```

## Database Structure

### Recipe Model
```python
class Recipe:
    title           : CharField(max_length=200)
    description     : TextField()
    ingredients     : JSONField()
    instructions    : TextField()
    cooking_time    : IntegerField()
    servings        : IntegerField()
    created_at      : DateTimeField(auto_now_add=True)
    updated_at      : DateTimeField(auto_now=True)
    author          : ForeignKey(User)
    image           : ImageField(upload_to='recipe_images/')
    category        : ForeignKey(Category, null=True)
    tags           : ManyToManyField(Tag)
```

### Category Model
```python
class Category:
    name            : CharField(max_length=100)
    slug            : SlugField(unique=True)
    description     : TextField()
    created_at      : DateTimeField(auto_now_add=True)
```

### Tag Model
```python
class Tag:
    name            : CharField(max_length=50)
    slug            : SlugField(unique=True)
    created_at      : DateTimeField(auto_now_add=True)
```

### Favorite Model
```python
class Favorite:
    user            : ForeignKey(User)
    recipe          : ForeignKey(Recipe)
    created_at      : DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['recipe', 'user']  # One favorite per user per recipe
```

### Relationships
- A Recipe belongs to one User (author)
- A Recipe belongs to one Category (optional)
- A Recipe can have many Tags
- A Recipe can have many Ratings from different Users
- A Recipe can have many Comments from different Users
- A Recipe can be favorited by many Users
- A User can have many Recipes
- A User can have many Ratings on different Recipes
- A User can have many Comments on different Recipes
- A User can have many Favorite Recipes

### Key Features
- JSON storage for ingredients allows flexible ingredient management
- Unique constraint on Rating ensures one rating per user per recipe
- Automatic timestamps for creation and updates
- Image upload support with dedicated media storage
- Built-in user authentication system

### MealPlan Model
```python
class MealPlan:
    user            : ForeignKey(User)
    date            : DateField()
    breakfast       : ForeignKey(Recipe, null=True)
    lunch           : ForeignKey(Recipe, null=True)
    dinner          : ForeignKey(Recipe, null=True)
    notes           : TextField()
    created_at      : DateTimeField(auto_now_add=True)
    updated_at      : DateTimeField(auto_now=True)
```

### WeeklyMealPlan Model
```python
class WeeklyMealPlan:
    user            : ForeignKey(User)
    start_date      : DateField()
    end_date        : DateField()
    daily_plans     : ManyToManyField(MealPlan)
    created_at      : DateTimeField(auto_now_add=True)
    updated_at      : DateTimeField(auto_now=True)
```

## Testing

### Manual Testing

#### User Authentication
- ✅ User registration form validation
- ✅ Login functionality
- ✅ Password reset process
- ✅ Profile updates

#### Recipe CRUD Operations
- ✅ Recipe creation with all fields
- ✅ Image upload functionality
- ✅ Recipe editing
- ✅ Recipe deletion
- ✅ Form validation

#### Social Features
- ✅ Rating system
- ✅ Comment posting
- ✅ Comment editing/deletion
- ✅ Favorite recipe toggling

#### Search and Filters
- ✅ Search functionality
- ✅ Category filtering
- ✅ Tag filtering
- ✅ Combined filters

#### Responsive Design
- ✅ Mobile view
- ✅ Tablet view
- ✅ Desktop view
- ✅ Navigation menu responsiveness

#### Premium Features
- ✅ Meal planner access control
- ✅ Weekly meal plan creation
- ✅ Recipe assignment to meals
- ✅ Shopping list generation
- ✅ PDF download functionality

### Browser Compatibility
- ✅ Chrome
- ✅ Firefox
- ✅ Safari
- ✅ Edge

## Development Issues and Solutions

### Issue 1: Recipe Image Upload
**Problem:** Image uploads were not saving correctly to the media directory.
**Solution:** 
- Added proper media root configuration in settings.py
- Updated file path handling in the Recipe model
- Configured URL patterns for media serving in development

### Issue 2: Search Functionality
**Problem:** Search queries were not returning expected results.
**Solution:**
- Implemented proper Q objects for complex queries
- Added distinct() to prevent duplicate results
- Fixed field lookups in the search view

### Issue 3: Favorite System
**Problem:** Toggle favorite wasn't working due to URL configuration issues.
**Solution:**
- Corrected URL patterns in urls.py
- Updated JavaScript fetch URL
- Added proper error handling in the view

### Issue 4: Category and Tag Implementation
**Problem:** Recipes weren't properly associating with categories and tags.
**Solution:**
- Updated model relationships
- Fixed form handling for tags
- Implemented proper save methods in forms

### Issue 5: Rating System
**Problem:** Users could submit multiple ratings for the same recipe.
**Solution:**
- Added unique_together constraint
- Implemented proper validation in the view
- Added update functionality for existing ratings

### Known Limitations
1. Image file size not restricted
2. No bulk recipe import/export
3. Limited recipe variation support
4. No API endpoints currently available

### Future Improvements
1. Add image compression
2. Implement recipe API
3. Add user following system
4. Enhance search with elasticsearch
5. Add recipe version control

## Performance Considerations
- Database query optimization needed for large recipe sets
- Image optimization for faster loading
- Caching implementation required for frequently accessed data
- Pagination implementation for large lists