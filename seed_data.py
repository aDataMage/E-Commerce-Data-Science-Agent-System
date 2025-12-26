"""
Seed Data Generator for E-commerce Database.

Generates synthetic data with detectable patterns for:
- A/B Testing: Ad_V1 (~4% conversion) vs Ad_V2 (~8% conversion)
- Segmentation: "Whales" (high frequency/spend) vs "Casuals" (low frequency/spend)
"""
import sqlite3
import random
from datetime import datetime, timedelta
from pathlib import Path


# Configuration
DB_PATH = "ecommerce.db"
RANDOM_SEED = 42

# Volume targets
NUM_SESSIONS = 4000  # Total website sessions
NUM_WHALE_USERS = 50  # High-value users
NUM_CASUAL_USERS = 200  # Low-value users
NUM_REGULAR_USERS = 50  # Medium-value users

# A/B Test configuration
AD_V1_SESSIONS = 2000
AD_V2_SESSIONS = 2000
AD_V1_CONVERSION_RATE = 0.04  # 4%
AD_V2_CONVERSION_RATE = 0.08  # 8%

# Products
PRODUCTS = [
    {"product_id": 1, "product_name": "Premium Widget", "created_at": "2023-01-15"},
    {"product_id": 2, "product_name": "Standard Gadget", "created_at": "2023-02-01"},
    {"product_id": 3, "product_name": "Deluxe Bundle", "created_at": "2023-03-10"},
    {"product_id": 4, "product_name": "Basic Starter Kit", "created_at": "2023-04-20"},
]


def create_database(db_path: str = DB_PATH):
    """Create the SQLite database with schema."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Drop existing tables
    cursor.execute("DROP TABLE IF EXISTS order_items")
    cursor.execute("DROP TABLE IF EXISTS orders")
    cursor.execute("DROP TABLE IF EXISTS website_sessions")
    cursor.execute("DROP TABLE IF EXISTS products")
    
    # Create products table
    cursor.execute("""
        CREATE TABLE products (
            product_id INTEGER PRIMARY KEY,
            product_name TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    
    # Create website_sessions table
    cursor.execute("""
        CREATE TABLE website_sessions (
            session_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            utm_source TEXT,
            utm_campaign TEXT,
            utm_content TEXT,
            device_type TEXT,
            created_at TEXT NOT NULL
        )
    """)
    
    # Create orders table
    cursor.execute("""
        CREATE TABLE orders (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            user_id INTEGER NOT NULL,
            price_usd REAL NOT NULL,
            cogs_usd REAL NOT NULL
        )
    """)
    
    # Create order_items table
    cursor.execute("""
        CREATE TABLE order_items (
            order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            price_usd REAL NOT NULL,
            cogs_usd REAL NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(order_id),
            FOREIGN KEY (product_id) REFERENCES products(product_id)
        )
    """)
    
    conn.commit()
    return conn


def seed_products(conn):
    """Insert product data."""
    cursor = conn.cursor()
    for p in PRODUCTS:
        cursor.execute(
            "INSERT INTO products (product_id, product_name, created_at) VALUES (?, ?, ?)",
            (p["product_id"], p["product_name"], p["created_at"])
        )
    conn.commit()
    print(f"  ✓ Inserted {len(PRODUCTS)} products")


def seed_website_sessions(conn):
    """
    Generate website sessions with A/B test pattern.
    Ad_V1: ~4% conversion, Ad_V2: ~8% conversion
    """
    cursor = conn.cursor()
    random.seed(RANDOM_SEED)
    
    base_date = datetime(2024, 1, 1)
    sessions = []
    
    utm_sources = ["google", "facebook", "twitter", "email", "organic"]
    devices = ["desktop", "mobile", "tablet"]
    
    # Assign users to ad variants
    # We'll track which users saw which ad for conversion logic
    user_campaigns = {}
    
    # Generate Ad_V1 sessions
    for i in range(AD_V1_SESSIONS):
        user_id = random.randint(1, 300)  # Total unique users pool
        user_campaigns[user_id] = "Ad_V1"
        
        session_date = base_date + timedelta(
            days=random.randint(0, 180),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
        
        sessions.append((
            user_id,
            random.choice(utm_sources),
            "Ad_V1",
            "version_1",
            random.choice(devices),
            session_date.isoformat()
        ))
    
    # Generate Ad_V2 sessions
    for i in range(AD_V2_SESSIONS):
        user_id = random.randint(301, 600)  # Different user pool for clean A/B
        user_campaigns[user_id] = "Ad_V2"
        
        session_date = base_date + timedelta(
            days=random.randint(0, 180),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
        
        sessions.append((
            user_id,
            random.choice(utm_sources),
            "Ad_V2",
            "version_2",
            random.choice(devices),
            session_date.isoformat()
        ))
    
    cursor.executemany(
        """INSERT INTO website_sessions 
           (user_id, utm_source, utm_campaign, utm_content, device_type, created_at)
           VALUES (?, ?, ?, ?, ?, ?)""",
        sessions
    )
    conn.commit()
    print(f"  ✓ Inserted {len(sessions)} website sessions")
    return user_campaigns


def seed_orders_and_items(conn, user_campaigns: dict):
    """
    Generate orders with segmentation and A/B conversion patterns.
    
    Segmentation:
    - Whales: Users 1-50, 5-15 orders each, $80-150 per order
    - Regulars: Users 51-100, 2-4 orders each, $40-80 per order  
    - Casuals: Users 101-300, 1-2 orders each, $15-40 per order
    
    A/B Conversions:
    - Ad_V1 users: ~4% convert (80 orders from 2000 sessions)
    - Ad_V2 users: ~8% convert (160 orders from 2000 sessions)
    """
    cursor = conn.cursor()
    random.seed(RANDOM_SEED + 1)  # Different seed for variety
    
    base_date = datetime(2024, 1, 1)
    orders = []
    order_items = []
    order_id = 1
    
    # --- Segmentation: Whale users (1-50) ---
    whale_users = list(range(1, NUM_WHALE_USERS + 1))
    for user_id in whale_users:
        num_orders = random.randint(5, 15)
        for _ in range(num_orders):
            order_date = base_date + timedelta(
                days=random.randint(0, 180),
                hours=random.randint(0, 23)
            )
            order_price = round(random.uniform(80, 150), 2)
            order_cogs = round(order_price * random.uniform(0.3, 0.5), 2)
            
            orders.append((
                order_date.isoformat(),
                user_id,
                order_price,
                order_cogs
            ))
            
            # Add 1-3 items per order
            num_items = random.randint(1, 3)
            for _ in range(num_items):
                product = random.choice(PRODUCTS)
                item_price = round(order_price / num_items, 2)
                item_cogs = round(item_price * random.uniform(0.3, 0.5), 2)
                order_items.append((
                    order_id,
                    product["product_id"],
                    item_price,
                    item_cogs
                ))
            
            order_id += 1
    
    # --- Segmentation: Regular users (51-100) ---
    regular_users = list(range(51, 51 + NUM_REGULAR_USERS))
    for user_id in regular_users:
        num_orders = random.randint(2, 4)
        for _ in range(num_orders):
            order_date = base_date + timedelta(
                days=random.randint(0, 180),
                hours=random.randint(0, 23)
            )
            order_price = round(random.uniform(40, 80), 2)
            order_cogs = round(order_price * random.uniform(0.3, 0.5), 2)
            
            orders.append((
                order_date.isoformat(),
                user_id,
                order_price,
                order_cogs
            ))
            
            # Add 1-2 items per order
            num_items = random.randint(1, 2)
            for _ in range(num_items):
                product = random.choice(PRODUCTS)
                item_price = round(order_price / num_items, 2)
                item_cogs = round(item_price * random.uniform(0.3, 0.5), 2)
                order_items.append((
                    order_id,
                    product["product_id"],
                    item_price,
                    item_cogs
                ))
            
            order_id += 1
    
    # --- Segmentation: Casual users (101-300) ---
    casual_users = list(range(101, 101 + NUM_CASUAL_USERS))
    for user_id in casual_users:
        num_orders = random.randint(1, 2)
        for _ in range(num_orders):
            order_date = base_date + timedelta(
                days=random.randint(0, 180),
                hours=random.randint(0, 23)
            )
            order_price = round(random.uniform(15, 40), 2)
            order_cogs = round(order_price * random.uniform(0.3, 0.5), 2)
            
            orders.append((
                order_date.isoformat(),
                user_id,
                order_price,
                order_cogs
            ))
            
            # Single item per order
            product = random.choice(PRODUCTS)
            order_items.append((
                order_id,
                product["product_id"],
                order_price,
                order_cogs
            ))
            
            order_id += 1
    
    # --- A/B Test Conversions ---
    # Ad_V1: Convert ~4% of users (80 conversions from users 1-300)
    ad_v1_converters = random.sample(range(1, 301), int(AD_V1_SESSIONS * AD_V1_CONVERSION_RATE))
    for user_id in ad_v1_converters:
        if user_id > 100:  # Skip users already covered by segmentation
            order_date = base_date + timedelta(days=random.randint(0, 180))
            order_price = round(random.uniform(25, 60), 2)
            order_cogs = round(order_price * 0.4, 2)
            
            orders.append((order_date.isoformat(), user_id, order_price, order_cogs))
            product = random.choice(PRODUCTS)
            order_items.append((order_id, product["product_id"], order_price, order_cogs))
            order_id += 1
    
    # Ad_V2: Convert ~8% of users (160 conversions from users 301-600)
    ad_v2_converters = random.sample(range(301, 601), int(AD_V2_SESSIONS * AD_V2_CONVERSION_RATE))
    for user_id in ad_v2_converters:
        order_date = base_date + timedelta(days=random.randint(0, 180))
        order_price = round(random.uniform(25, 60), 2)
        order_cogs = round(order_price * 0.4, 2)
        
        orders.append((order_date.isoformat(), user_id, order_price, order_cogs))
        product = random.choice(PRODUCTS)
        order_items.append((order_id, product["product_id"], order_price, order_cogs))
        order_id += 1
    
    # Insert all orders
    cursor.executemany(
        """INSERT INTO orders (created_at, user_id, price_usd, cogs_usd)
           VALUES (?, ?, ?, ?)""",
        orders
    )
    
    # Insert all order items
    cursor.executemany(
        """INSERT INTO order_items (order_id, product_id, price_usd, cogs_usd)
           VALUES (?, ?, ?, ?)""",
        order_items
    )
    
    conn.commit()
    print(f"  ✓ Inserted {len(orders)} orders")
    print(f"  ✓ Inserted {len(order_items)} order items")


def print_summary(conn):
    """Print a summary of the generated data."""
    cursor = conn.cursor()
    
    print("\n" + "="*50)
    print("DATABASE SUMMARY")
    print("="*50)
    
    # Table counts
    tables = ["products", "website_sessions", "orders", "order_items"]
    for table in tables:
        count = cursor.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"  {table}: {count} rows")
    
    # A/B Test summary
    print("\n" + "-"*50)
    print("A/B TEST DATA")
    print("-"*50)
    
    ab_query = """
        SELECT 
            ws.utm_campaign,
            COUNT(DISTINCT ws.session_id) as sessions,
            COUNT(DISTINCT o.order_id) as conversions
        FROM website_sessions ws
        LEFT JOIN orders o ON ws.user_id = o.user_id
        WHERE ws.utm_campaign IN ('Ad_V1', 'Ad_V2')
        GROUP BY ws.utm_campaign
    """
    results = cursor.execute(ab_query).fetchall()
    for campaign, sessions, conversions in results:
        rate = (conversions / sessions * 100) if sessions > 0 else 0
        print(f"  {campaign}: {sessions} sessions, {conversions} conversions ({rate:.2f}%)")
    
    # Segmentation summary
    print("\n" + "-"*50)
    print("SEGMENTATION DATA (User Groups)")
    print("-"*50)
    
    seg_query = """
        SELECT 
            CASE 
                WHEN user_id <= 50 THEN 'Whales (1-50)'
                WHEN user_id <= 100 THEN 'Regular (51-100)'
                ELSE 'Casual (101+)'
            END as segment,
            COUNT(DISTINCT user_id) as users,
            COUNT(*) as orders,
            ROUND(AVG(price_usd), 2) as avg_order_value,
            ROUND(SUM(price_usd), 2) as total_revenue
        FROM orders
        WHERE user_id <= 300
        GROUP BY segment
        ORDER BY avg_order_value DESC
    """
    results = cursor.execute(seg_query).fetchall()
    for segment, users, orders, aov, revenue in results:
        print(f"  {segment}: {users} users, {orders} orders, ${aov} AOV, ${revenue} revenue")


def main():
    """Main function to seed the database."""
    print("="*50)
    print("E-COMMERCE DATABASE SEEDER")
    print("="*50)
    print(f"\nCreating database: {DB_PATH}")
    
    # Create and seed
    conn = create_database(DB_PATH)
    
    print("\nSeeding data...")
    seed_products(conn)
    user_campaigns = seed_website_sessions(conn)
    seed_orders_and_items(conn, user_campaigns)
    
    # Print summary
    print_summary(conn)
    
    conn.close()
    print("\n✓ Database seeding complete!")
    print(f"  Database saved to: {Path(DB_PATH).absolute()}")


if __name__ == "__main__":
    main()
