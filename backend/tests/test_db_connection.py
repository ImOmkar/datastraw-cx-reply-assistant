from sqlalchemy import text
from backend.app.db.session import engine

def test_database_connetion():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        assert result.scalar() == 1
        
        
        
if __name__ == "__main__":
    test_database_connetion()
    print("DATABASE Connection successfull")
    
