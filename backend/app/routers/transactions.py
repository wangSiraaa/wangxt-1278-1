from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.models import User, UserRole, ReplenishmentStatus
from app.security import get_current_active_user, require_supplier, require_engineer, require_admin
from app.schemas import (
    ReplenishmentCreate, ReplenishmentUpdate, ReplenishmentResponse,
    SettlementCreate, SettlementUpdate, SettlementResponse,
    SettlementStatus
)
from app.crud import CRUDRequisition, CRUDReplenishment, CRUDSettlement

router = APIRouter(tags=["Replenishments & Settlements"])


@router.post("/replenishments", response_model=ReplenishmentResponse)
def create_replenishment(
    replenishment_in: ReplenishmentCreate,
    db: Session = Depends(get_db),
    current_user: User = require_supplier
):
    if current_user.supplier_id and current_user.supplier_id != replenishment_in.supplier_id:
        raise HTTPException(status_code=403, detail="Not authorized for this supplier")
    try:
        return CRUDReplenishment.create(db, obj_in=replenishment_in, created_by=current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/replenishments", response_model=list[ReplenishmentResponse])
def list_replenishments(
    skip: int = 0,
    limit: int = 100,
    status: Optional[ReplenishmentStatus] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    supplier_id = None
    if current_user.role == UserRole.SUPPLIER and current_user.supplier_id:
        supplier_id = current_user.supplier_id
    replenishments, _ = CRUDReplenishment.list(
        db, skip=skip, limit=limit,
        status=status,
        supplier_id=supplier_id
    )
    return replenishments


@router.get("/replenishments/{replenishment_id}", response_model=ReplenishmentResponse)
def get_replenishment(
    replenishment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    replenishment = CRUDReplenishment.get_by_id(db, replenishment_id=replenishment_id)
    if not replenishment:
        raise HTTPException(status_code=404, detail="Replenishment not found")
    if (current_user.role == UserRole.SUPPLIER and
            current_user.supplier_id != replenishment.supplier_id):
        raise HTTPException(status_code=403, detail="Not authorized to view this replenishment")
    return replenishment


@router.post("/replenishments/{replenishment_id}/submit", response_model=ReplenishmentResponse)
def submit_replenishment(
    replenishment_id: int,
    db: Session = Depends(get_db),
    current_user: User = require_supplier
):
    replenishment = CRUDReplenishment.get_by_id(db, replenishment_id=replenishment_id)
    if not replenishment:
        raise HTTPException(status_code=404, detail="Replenishment not found")
    if replenishment.status != ReplenishmentStatus.DRAFT:
        raise HTTPException(status_code=400, detail="Only draft replenishments can be submitted")
    if (current_user.supplier_id and
            current_user.supplier_id != replenishment.supplier_id):
        raise HTTPException(status_code=403, detail="Not authorized for this supplier")
    return CRUDReplenishment.update_status(db, db_obj=replenishment, status=ReplenishmentStatus.PENDING)


@router.post("/replenishments/{replenishment_id}/approve", response_model=ReplenishmentResponse)
def approve_replenishment(
    replenishment_id: int,
    approved: bool = Query(True),
    db: Session = Depends(get_db),
    current_user: User = require_engineer
):
    replenishment = CRUDReplenishment.get_by_id(db, replenishment_id=replenishment_id)
    if not replenishment:
        raise HTTPException(status_code=404, detail="Replenishment not found")
    if replenishment.status != ReplenishmentStatus.PENDING:
        raise HTTPException(status_code=400, detail="Only pending replenishments can be approved")

    if approved:
        return CRUDReplenishment.update_status(
            db, db_obj=replenishment,
            status=ReplenishmentStatus.IN_TRANSIT,
            approved_by=current_user.id
        )
    else:
        return CRUDReplenishment.update_status(
            db, db_obj=replenishment,
            status=ReplenishmentStatus.REJECTED
        )


@router.post("/replenishments/{replenishment_id}/receive", response_model=ReplenishmentResponse)
def receive_replenishment(
    replenishment_id: int,
    db: Session = Depends(get_db),
    current_user: User = require_engineer
):
    replenishment = CRUDReplenishment.get_by_id(db, replenishment_id=replenishment_id)
    if not replenishment:
        raise HTTPException(status_code=404, detail="Replenishment not found")
    if replenishment.status != ReplenishmentStatus.IN_TRANSIT:
        raise HTTPException(status_code=400, detail="Only in-transit replenishments can be received")
    return CRUDReplenishment.update_status(db, db_obj=replenishment, status=ReplenishmentStatus.RECEIVED)


@router.post("/settlements", response_model=SettlementResponse)
def create_settlement(
    settlement_in: SettlementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    try:
        return CRUDSettlement.create(db, obj_in=settlement_in, created_by=current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/settlements", response_model=list[SettlementResponse])
def list_settlements(
    skip: int = 0,
    limit: int = 100,
    status: Optional[SettlementStatus] = None,
    period: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    supplier_id = None
    if current_user.role == UserRole.SUPPLIER and current_user.supplier_id:
        supplier_id = current_user.supplier_id
    settlements, _ = CRUDSettlement.list(
        db, skip=skip, limit=limit,
        status=status,
        supplier_id=supplier_id,
        period=period
    )
    return settlements


@router.get("/settlements/{settlement_id}", response_model=SettlementResponse)
def get_settlement(
    settlement_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    settlement = CRUDSettlement.get_by_id(db, settlement_id=settlement_id)
    if not settlement:
        raise HTTPException(status_code=404, detail="Settlement not found")
    if (current_user.role == UserRole.SUPPLIER and
            current_user.supplier_id != settlement.supplier_id):
        raise HTTPException(status_code=403, detail="Not authorized to view this settlement")
    return settlement


@router.post("/settlements/{settlement_id}/approve", response_model=SettlementResponse)
def approve_settlement(
    settlement_id: int,
    approved: bool = Query(True),
    db: Session = Depends(get_db),
    current_user: User = require_admin
):
    settlement = CRUDSettlement.get_by_id(db, settlement_id=settlement_id)
    if not settlement:
        raise HTTPException(status_code=404, detail="Settlement not found")
    if settlement.status != SettlementStatus.PENDING:
        raise HTTPException(status_code=400, detail="Only pending settlements can be approved")

    if approved:
        return CRUDSettlement.update_status(
            db, db_obj=settlement,
            status=SettlementStatus.APPROVED,
            approved_by=current_user.id
        )
    else:
        return CRUDSettlement.update_status(
            db, db_obj=settlement,
            status=SettlementStatus.REJECTED
        )


@router.post("/settlements/{settlement_id}/pay", response_model=SettlementResponse)
def pay_settlement(
    settlement_id: int,
    db: Session = Depends(get_db),
    current_user: User = require_admin
):
    settlement = CRUDSettlement.get_by_id(db, settlement_id=settlement_id)
    if not settlement:
        raise HTTPException(status_code=404, detail="Settlement not found")
    if settlement.status != SettlementStatus.APPROVED:
        raise HTTPException(status_code=400, detail="Only approved settlements can be paid")
    return CRUDSettlement.update_status(db, db_obj=settlement, status=SettlementStatus.PAID)
