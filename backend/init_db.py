from sqlalchemy.orm import Session
from app.database import SessionLocal, Base, engine
from app.models import User, UserRole, Supplier, SparePart
from app.security import hash_password

Base.metadata.create_all(bind=engine)

def init_data():
    db = SessionLocal()
    try:
        if not db.query(User).filter(User.username == "admin").first():
            admin = User(
                username="admin",
                email="admin@example.com",
                hashed_password=hash_password("admin123"),
                full_name="System Administrator",
                role=UserRole.ADMIN,
                is_active=True
            )
            db.add(admin)

        if not db.query(User).filter(User.username == "engineer1").first():
            engineer = User(
                username="engineer1",
                email="engineer1@example.com",
                hashed_password=hash_password("engineer123"),
                full_name="Equipment Engineer",
                role=UserRole.EQUIPMENT_ENGINEER,
                is_active=True
            )
            db.add(engineer)

        if not db.query(Supplier).filter(Supplier.code == "SUP001").first():
            supplier = Supplier(
                code="SUP001",
                name="Industrial Parts Supplier Co., Ltd.",
                contact_person="John Supplier",
                phone="1234567890",
                email="supplier@example.com",
                address="123 Industrial Park",
                is_active=True
            )
            db.add(supplier)
            db.flush()

            supplier_user = User(
                username="supplier1",
                email="supplier1@example.com",
                hashed_password=hash_password("supplier123"),
                full_name="Supplier Manager",
                role=UserRole.SUPPLIER,
                supplier_id=supplier.id,
                is_active=True
            )
            db.add(supplier_user)

        if not db.query(User).filter(User.username == "finance1").first():
            finance = User(
                username="finance1",
                email="finance1@example.com",
                hashed_password=hash_password("finance123"),
                full_name="Finance Officer",
                role=UserRole.FINANCE,
                is_active=True
            )
            db.add(finance)

        if not db.query(SparePart).filter(SparePart.code == "SP001").first():
            sp1 = SparePart(
                code="SP001",
                name="Bearing Type A",
                specification="6205-2RS",
                unit="piece",
                safety_stock=50,
                description="Standard deep groove ball bearing",
                is_active=True
            )
            db.add(sp1)

            sp2 = SparePart(
                code="SP002",
                name="Mechanical Seal",
                specification="Type 21 - 1 inch",
                unit="set",
                safety_stock=20,
                description="Pump mechanical seal assembly",
                is_active=True
            )
            db.add(sp2)

            sp3 = SparePart(
                code="SP003",
                name="Hydraulic Filter",
                specification="10 micron",
                unit="piece",
                safety_stock=30,
                description="High pressure hydraulic filter",
                is_active=True
            )
            db.add(sp3)

        db.commit()
        print("Initial data created successfully!")
        print("Default accounts:")
        print("  admin / admin123 (Administrator)")
        print("  engineer1 / engineer123 (Equipment Engineer)")
        print("  supplier1 / supplier123 (Supplier)")
        print("  finance1 / finance123 (Finance)")
    except Exception as e:
        print(f"Error creating initial data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_data()
