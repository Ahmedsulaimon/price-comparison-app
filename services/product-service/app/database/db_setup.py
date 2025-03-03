from app import create_app
from app.database import db
#Initializes database tables (usually only run once)
app = create_app()

def setup_database():
    with app.app_context():
        db.create_all()
        print("Database tables created!")

if __name__ == '__main__':
    setup_database()