from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.models import User
from app.security import get_current_active_user, require_admin
from app.schemas import (
    SupplierCreate, SupplierUpdate, SupplierResponse,
    SparePartCreate, SparePartUpdate, SparePartResponse, SparePartStockResponse
)
from app.crud import CRUDSupplier, CRUDSparePart

router = APIRouter(tags=["Master Data"])


@router.post("/suppliers", response_model=SupplierResponse)
def create_supplier(
    supplier_in: SupplierCreate,
    db: Session = Depends(get_db),
    current_user: User = require_admin
):
    return CRUDSupplier.create(db, obj_in=supplier_in)


@router.get("/suppliers", response_model=list[SupplierResponse])
def list_suppliers(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    suppliers, _ = CRUDSupplier.list(db, skip=skip, limit=limit)
    return suppliers


@router.get("/suppliers/{supplier_id}", response_model=SupplierResponse)
def get_supplier(
    supplier_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    supplier = CRUDSupplier.get_by_id(db, supplier_id=supplier_id)
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return supplier


@router.put("/suppliers/{supplier_id}", response_model=SupplierResponse)
def update_supplier(
    supplier_id: int,
    supplier_in: SupplierUpdate,
    db: Session = Depends(get_db),
    current_user: User = require_admin
):
    db_supplier = CRUDSupplier.get_by_id(db, supplier_id=supplier_id)
    if not db_supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return CRUDSupplier.update(db, db_obj=db_supplier, obj_in=supplier_in)


@router.post("/spare-parts", response_model=SparePartResponse)
def create_spare_part(
    spare_part_in: SparePartCreate,
    db: Session = Depends(get_db),
    current_user: User = require_admin
):
    return CRUDSparePart.create(db, obj_in=spare_part_in)


@router.get("/spare-parts", response_model=list[SparePartStockResponse])
def list_spare_parts(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    spare_parts, _ = CRUDSparePart.list(db, skip=skip, limit=limit)
    result = []
    for sp in spare_parts:
        stock_info = CRUDSparePart.get_stock_summary(db, sp.id)
        sp_dict = sp.__dict__.copy()
        sp_dict.update(stock_info)
        result.append(SparePartStockResponse(**sp_dict))
    return result


@router.get("/spare-parts/{spare_part_id}", response_model=SparePartStockResponse)
def get_spare_part(
    spare_part_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    spare_part = CRUDSparePart.get_by_id(db, spare_part_id=spare_part_id)
    if not spare_part:
        raise HTTPException(status_code=404, detail="Spare part not found")
    stock_info = CRUDSparePart.get_stock_summary(db, spare_part_id)
    sp_dict = spare_part.__dict__.copy()
    sp_dict.update(stock_info)
    return SparePartStockResponse(**sp_dict)


@router.put("/spare-parts/{spare_part_id}", response_model=SparePartResponse)
def update_spare_part(
    spare_part_id: int,
    spare_part_in: SparePartUpdate,
    db: Session = Depends(get_db),
    current_user: User = require_admin
):
    db_spare_part = CRUDSparePart.get_by_id(db, spare_part_id=spare_part_id)
    if not db_spare_part:
        raise HTTPException(status_code=404, detail="Spare part not found")
    return CRUDSparePart.update(db, db_obj=db_spare_part, obj_in=spare_part_in)
