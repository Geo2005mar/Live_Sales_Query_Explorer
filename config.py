import os

from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "127.0.0.1"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "salesroot"),
    "database": os.getenv("DB_NAME", "sales_db"),
}

CATEGORIES = {
    "Electronics": ["Laptop", "Smartphone", "Headphones", "Monitor", "Tablet"],
    "Clothing": ["T-Shirt", "Jeans", "Jacket", "Sneakers", "Hat"],
    "Home & Kitchen": ["Blender", "Vacuum Cleaner", "Cookware Set", "Coffee Maker", "Air Fryer"],
    "Books": ["Novel", "Cookbook", "Biography", "Comic Book", "Textbook"],
    "Sports": ["Yoga Mat", "Dumbbells", "Bicycle", "Running Shoes", "Tennis Racket"],
}

COUNTRIES = [
    "Greece", "Germany", "France", "Italy", "Spain",
    "USA", "United Kingdom", "Netherlands", "Sweden", "Portugal",
]

AMOUNT_MIN = 5.0
AMOUNT_MAX = 2000.0
