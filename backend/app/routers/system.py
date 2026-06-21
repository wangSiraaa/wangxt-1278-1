from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.models import User, UserRole
from app.security import get_current_active_user, require_finance, require_admin
from app.schemas import (
    MonthlyClosingCreate, MonthlyClosingResponse,
    SafetyStockAlertResponse, DashboardStats
)
from app.crud import CRUDMonthlyClosing, CRUDSafetyStockAlert, CRUDDashboard, CRUDRequisition

router = APIRouter(tags=["System & Dashboard"])


@router.post("/monthly-closings", response_model=MonthlyClosingResponse)
def create_monthly_closing(
    closing_in: MonthlyClosingCreate,
    db: Session = Depends(get_db),
    current_user: User = require_finance
):
    try:
        return CRUDMonthlyClosing.create(db, obj_in=closing_in, closed_by=current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/monthly-closings", response_model=list[MonthlyClosingResponse])
def list_monthly_closings(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    closings, _ = CRUDMonthlyClosing.list(db, skip=skip, limit=limit)
    return closings


@router.post("/monthly-closings/{period}/reopen", response_model=MonthlyClosingResponse)
def reopen_monthly_closing(
    period: str,
    db: Session = Depends(get_db),
    current_user: User = require_admin
):
    try:
        return CRUDMonthlyClosing.reopen(db, period=period)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/check-period", response_model=dict)
def check_period_status(
    period: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    closing = CRUDMonthlyClosing.get_by_period(db, period=period)
    return {
        "period": period,
        "is_closed": closing.is_closed if closing else False,
        "closed_at": closing.closed_at if closing else None
    }


@router.get("/safety-stock-alerts", response_model=list[SafetyStockAlertResponse])
def list_safety_stock_alerts(
    skip: int = 0,
    limit: int = 100,
    is_processed: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    CRUDSafetyStockAlert.check_and_create_alerts(db)
    alerts, _ = CRUDSafetyStockAlert.list(db, skip=skip, limit=limit, is_processed=is_processed)
    return alerts


@router.post("/safety-stock-alerts/{alert_id}/process", response_model=SafetyStockAlertResponse)
def process_safety_stock_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = require_admin
):
    alert = CRUDSafetyStockAlert.mark_processed(db, alert_id=alert_id, processed_by=current_user.id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert


@router.get("/dashboard/stats", response_model=DashboardStats)
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    CRUDSafetyStockAlert.check_and_create_alerts(db)
    return CRUDDashboard.get_stats(db)


@router.post("/check-requisition-period/{requisition_id}", response_model=dict)
def check_requisition_period(
    requisition_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    is_closed = CRUDRequisition.is_period_closed(db, requisition_id=requisition_id)
    requisition = CRUDRequisition.get_by_id(db, requisition_id=requisition_id)
    period = requisition.delivered_at.strftime("%Y-%m") if requisition and requisition.delivered_at else None
    return {
        "requisition_id": requisition_id,
        "is_period_closed": is_closed,
        "period": period,
        "can_modify": not is_closed
    }
