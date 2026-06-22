from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.models import User, UserRole
from app.security import get_current_active_user, require_admin, require_engineer, require_supplier
from app.schemas import (
    SupplierBatchCreate, SupplierBatchUpdate, SupplierBatchResponse, SupplierBatchWithOwnershipResponse,
    MaintenanceOrderCreate, MaintenanceOrderUpdate, MaintenanceOrderResponse,
    StockOwnershipConfirmationCreate, StockOwnershipConfirmationUpdate, StockOwnershipConfirmationResponse,
    BatchOwnershipStatus
)
from app.crud import CRUDSupplierBatch, CRUDMaintenanceOrder, CRUDStockOwnershipConfirmation

router = APIRouter(tags=["Inventory & Batches"])


@router.post("/batches", response_model=SupplierBatchResponse)
def create_batch(
    batch_in: SupplierBatchCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    existing = CRUDSupplierBatch.get_by_batch_no(db, batch_no=batch_in.batch_no)
    if existing:
        raise HTTPException(status_code=400, detail="Batch number already exists")
    return CRUDSupplierBatch.create(db, obj_in=batch_in)


@router.get("/batches", response_model=list[SupplierBatchWithOwnershipResponse])
def list_batches(
    skip: int = 0,
    limit: int = 100,
    spare_part_id: Optional[int] = None,
    supplier_id: Optional[int] = None,
    available_only: bool = Query(False, description="Only show batches with available stock"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    batches, _ = CRUDSupplierBatch.list(
        db, skip=skip, limit=limit,
        spare_part_id=spare_part_id,
        supplier_id=supplier_id,
        available_only=available_only
    )
    result = []
    for batch in batches:
        ownership_status = CRUDSupplierBatch.get_ownership_status(db, batch.id)
        batch_dict = batch.__dict__.copy()
        batch_dict["ownership_status"] = BatchOwnershipStatus(**ownership_status)
        result.append(SupplierBatchWithOwnershipResponse(**batch_dict))
    return result


@router.get("/batches/{batch_id}", response_model=SupplierBatchWithOwnershipResponse)
def get_batch(
    batch_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    batch = CRUDSupplierBatch.get_by_id(db, batch_id=batch_id)
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    ownership_status = CRUDSupplierBatch.get_ownership_status(db, batch_id)
    batch_dict = batch.__dict__.copy()
    batch_dict["ownership_status"] = BatchOwnershipStatus(**ownership_status)
    return SupplierBatchWithOwnershipResponse(**batch_dict)


@router.put("/batches/{batch_id}", response_model=SupplierBatchResponse)
def update_batch(
    batch_id: int,
    batch_in: SupplierBatchUpdate,
    db: Session = Depends(get_db),
    current_user: User = require_admin
):
    db_batch = CRUDSupplierBatch.get_by_id(db, batch_id=batch_id)
    if not db_batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    return CRUDSupplierBatch.update(db, db_obj=db_batch, obj_in=batch_in)


@router.post("/batches/{batch_id}/confirm-ownership", response_model=StockOwnershipConfirmationResponse)
def confirm_ownership(
    batch_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.role not in [UserRole.EQUIPMENT_ENGINEER, UserRole.SUPPLIER, UserRole.FINANCE, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Not authorized to confirm ownership")

    batch = CRUDSupplierBatch.get_by_id(db, batch_id=batch_id)
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")

    confirmation_in = StockOwnershipConfirmationCreate(batch_id=batch_id)
    try:
        return CRUDStockOwnershipConfirmation.create(db, obj_in=confirmation_in, confirmer=current_user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/batches/{batch_id}/ownership-status", response_model=BatchOwnershipStatus)
def get_batch_ownership_status(
    batch_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    batch = CRUDSupplierBatch.get_by_id(db, batch_id=batch_id)
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    return CRUDSupplierBatch.get_ownership_status(db, batch_id)


@router.get("/ownership-confirmations", response_model=list[StockOwnershipConfirmationResponse])
def list_ownership_confirmations(
    skip: int = 0,
    limit: int = 100,
    batch_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    confirmations, _ = CRUDStockOwnershipConfirmation.list(
        db, skip=skip, limit=limit, batch_id=batch_id
    )
    return confirmations


@router.put("/ownership-confirmations/{confirmation_id}", response_model=StockOwnershipConfirmationResponse)
def update_confirmation_status(
    confirmation_id: int,
    confirmation_in: StockOwnershipConfirmationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_confirmation = CRUDStockOwnershipConfirmation.get_by_id(db, confirmation_id=confirmation_id)
    if not db_confirmation:
        raise HTTPException(status_code=404, detail="Confirmation not found")
    if db_confirmation.confirmer_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized to update this confirmation")
    return CRUDStockOwnershipConfirmation.update(db, db_obj=db_confirmation, obj_in=confirmation_in)


@router.post("/maintenance-orders", response_model=MaintenanceOrderResponse)
def create_maintenance_order(
    order_in: MaintenanceOrderCreate,
    db: Session = Depends(get_db),
    current_user: User = require_engineer
):
    return CRUDMaintenanceOrder.create(db, obj_in=order_in, created_by=current_user.id)


@router.get("/maintenance-orders", response_model=list[MaintenanceOrderResponse])
def list_maintenance_orders(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    orders, _ = CRUDMaintenanceOrder.list(db, skip=skip, limit=limit)
    return orders


@router.get("/maintenance-orders/{order_id}", response_model=MaintenanceOrderResponse)
def get_maintenance_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    order = CRUDMaintenanceOrder.get_by_id(db, order_id=order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Maintenance order not found")
    return order


@router.put("/maintenance-orders/{order_id}", response_model=MaintenanceOrderResponse)
def update_maintenance_order(
    order_id: int,
    order_in: MaintenanceOrderUpdate,
    db: Session = Depends(get_db),
    current_user: User = require_engineer
):
    db_order = CRUDMaintenanceOrder.get_by_id(db, order_id=order_id)
    if not db_order:
        raise HTTPException(status_code=404, detail="Maintenance order not found")
    return CRUDMaintenanceOrder.update(db, db_obj=db_order, obj_in=order_in)
