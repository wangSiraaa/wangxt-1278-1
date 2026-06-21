from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.models import User, UserRole, RequisitionStatus, Requisition
from app.security import get_current_active_user, require_engineer, require_admin, require_finance
from app.schemas import (
    RequisitionCreate, RequisitionUpdate, RequisitionResponse,
    RequisitionApprove
)
from app.crud import CRUDRequisition, CRUDMaintenanceOrder

router = APIRouter(tags=["Requisitions"])


@router.post("/requisitions", response_model=RequisitionResponse)
def create_requisition(
    requisition_in: RequisitionCreate,
    db: Session = Depends(get_db),
    current_user: User = require_engineer
):
    maintenance_order = CRUDMaintenanceOrder.get_by_id(db, order_id=requisition_in.maintenance_order_id)
    if not maintenance_order:
        raise HTTPException(status_code=404, detail="Maintenance order not found")
    if maintenance_order.is_closed:
        raise HTTPException(status_code=400, detail="Maintenance order is already closed")

    try:
        return CRUDRequisition.create(db, obj_in=requisition_in, created_by=current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/requisitions", response_model=list[RequisitionResponse])
def list_requisitions(
    skip: int = 0,
    limit: int = 100,
    status: Optional[RequisitionStatus] = None,
    is_settled: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    created_by = None
    if current_user.role == UserRole.EQUIPMENT_ENGINEER:
        created_by = current_user.id
    requisitions, _ = CRUDRequisition.list(
        db, skip=skip, limit=limit,
        status=status,
        created_by=created_by,
        is_settled=is_settled
    )
    return requisitions


@router.get("/requisitions/{requisition_id}", response_model=RequisitionResponse)
def get_requisition(
    requisition_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    requisition = CRUDRequisition.get_by_id(db, requisition_id=requisition_id)
    if not requisition:
        raise HTTPException(status_code=404, detail="Requisition not found")
    if (current_user.role == UserRole.EQUIPMENT_ENGINEER and
            requisition.created_by != current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to view this requisition")
    return requisition


@router.post("/requisitions/{requisition_id}/submit", response_model=RequisitionResponse)
def submit_requisition(
    requisition_id: int,
    db: Session = Depends(get_db),
    current_user: User = require_engineer
):
    requisition = CRUDRequisition.get_by_id(db, requisition_id=requisition_id)
    if not requisition:
        raise HTTPException(status_code=404, detail="Requisition not found")
    if requisition.status != RequisitionStatus.DRAFT:
        raise HTTPException(status_code=400, detail="Only draft requisitions can be submitted")
    if requisition.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to submit this requisition")
    return CRUDRequisition.update_status(db, db_obj=requisition, status=RequisitionStatus.PENDING)


@router.post("/requisitions/{requisition_id}/approve", response_model=RequisitionResponse)
def approve_requisition(
    requisition_id: int,
    approve_in: RequisitionApprove,
    db: Session = Depends(get_db),
    current_user: User = require_engineer
):
    requisition = CRUDRequisition.get_by_id(db, requisition_id=requisition_id)
    if not requisition:
        raise HTTPException(status_code=404, detail="Requisition not found")
    if requisition.status != RequisitionStatus.PENDING:
        raise HTTPException(status_code=400, detail="Only pending requisitions can be approved")

    if approve_in.approved:
        return CRUDRequisition.update_status(
            db, db_obj=requisition,
            status=RequisitionStatus.APPROVED,
            approved_by=current_user.id
        )
    else:
        return CRUDRequisition.update_status(
            db, db_obj=requisition,
            status=RequisitionStatus.REJECTED
        )


@router.post("/requisitions/{requisition_id}/deliver", response_model=RequisitionResponse)
def deliver_requisition(
    requisition_id: int,
    db: Session = Depends(get_db),
    current_user: User = require_engineer
):
    requisition = CRUDRequisition.get_by_id(db, requisition_id=requisition_id)
    if not requisition:
        raise HTTPException(status_code=404, detail="Requisition not found")
    if requisition.status != RequisitionStatus.APPROVED:
        raise HTTPException(status_code=400, detail="Only approved requisitions can be delivered")

    if CRUDRequisition.is_period_closed(db, requisition_id):
        raise HTTPException(status_code=400, detail="Cannot modify requisition in closed period")

    return CRUDRequisition.update_status(db, db_obj=requisition, status=RequisitionStatus.DELIVERED)


@router.put("/requisitions/{requisition_id}", response_model=RequisitionResponse)
def update_requisition(
    requisition_id: int,
    requisition_in: RequisitionUpdate,
    db: Session = Depends(get_db),
    current_user: User = require_engineer
):
    requisition = CRUDRequisition.get_by_id(db, requisition_id=requisition_id)
    if not requisition:
        raise HTTPException(status_code=404, detail="Requisition not found")
    if requisition.status not in [RequisitionStatus.DRAFT, RequisitionStatus.REJECTED]:
        raise HTTPException(status_code=400, detail="Only draft or rejected requisitions can be modified")
    if requisition.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to modify this requisition")
    if CRUDRequisition.is_period_closed(db, requisition_id):
        raise HTTPException(status_code=400, detail="Cannot modify requisition in closed period")

    return CRUDRequisition.update_status(db, db_obj=requisition, status=requisition_in.status or requisition.status)
