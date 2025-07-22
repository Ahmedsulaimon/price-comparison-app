from sqlalchemy import select, exists

def initialize_retailers(db):
    """Initialize retailers table with default data"""
    # Check if retailers table exists and has data
    if db.session.query(
        exists().select_from(db.text("retailers"))
    ).scalar():
        return  # Table already populated
    
    retailers = [
        {'name': 'Sainsbury', 'base_url': 'https://www.sainsburys.co.uk', 'provides_rating': True},
        {'name': 'Iceland', 'base_url': 'https://www.iceland.co.uk', 'provides_rating': True},
        {'name': 'Morrisons', 'base_url': 'https://groceries.morrisons.com', 'provides_rating': True},
        {'name': 'Aldi', 'base_url': 'https://groceries.aldi.co.uk', 'provides_rating': False}
    ]
    
    # Use proper SQLAlchemy ORM pattern
    for retailer in retailers:
        if not db.session.execute(
            select(db.text('1')).where(db.text(f"exists(select 1 from retailers where name = '{retailer['name']}')"))
        ).scalar():
            db.session.execute(
                db.text(
                    "INSERT INTO retailers (name, base_url, provides_rating) "
                    "VALUES (:name, :base_url, :provides_rating)"
                ),
                retailer
            )
    
    db.session.commit()