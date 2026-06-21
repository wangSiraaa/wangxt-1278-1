from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine
from app.routers import auth, master_data, inventory, requisitions, transactions, system

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Industrial Spare Parts Consignment Inventory System",
    description="System for managing consignment inventory with equipment department, supplier, and finance confirmation workflows",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(master_data.router, prefix="/api")
app.include_router(inventory.router, prefix="/api")
app.include_router(requisitions.router, prefix="/api")
app.include_router(transactions.router, prefix="/api")
app.include_router(system.router, prefix="/api")


@app.get("/")
def root():
    return {
        "message": "Industrial Spare Parts Consignment Inventory System API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}
