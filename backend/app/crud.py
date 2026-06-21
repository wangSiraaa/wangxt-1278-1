from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import List, Optional, Tuple
from datetime import datetime
from app.models import (
    User, Supplier, SparePart, SupplierBatch, MaintenanceOrder,
    Requisition, RequisitionItem, Replenishment, ReplenishmentItem,
    Settlement, StockOwnershipConfirmation, MonthlyClosing, SafetyStockAlert,
    UserRole, RequisitionStatus, ReplenishmentStatus, SettlementStatus, ConfirmationStatus
)
from app.schemas import (
    UserCreate, UserUpdate, SupplierCreate, SupplierUpdate,
    SparePartCreate, SparePartUpdate, SupplierBatchCreate, SupplierBatchUpdate,
    MaintenanceOrderCreate, MaintenanceOrderUpdate, RequisitionCreate, RequisitionUpdate,
    ReplenishmentCreate, ReplenishmentUpdate, SettlementCreate, SettlementUpdate,
    StockOwnershipConfirmationCreate, StockOwnershipConfirmationUpdate,
    MonthlyClosingCreate
)
from app.security import hash_password


def generate_no(prefix: str, db: Session) -> str:
    count = db.query(func.count()).select_from(
        db.query(User).subquery() if False else db.query(Requisition).subquery()
    ).scalar() or 0
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"{prefix}{timestamp}{count + 1:04d}"


class CRUDUser:
    @staticmethod
    def create(db: Session, obj_in: UserCreate) -> User:
        db_obj = User(
            username=obj_in.username,
            email=obj_in.email,
            hashed_password=hash_password(obj_in.password),
            full_name=obj_in.full_name,
            role=obj_in.role,
            supplier_id=obj_in.supplier_id
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def get_by_username(db: Session, username: str) -> Optional[User]:
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    def get_by_id(db: Session, user_id: int) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def list(db: Session, skip: int = 0, limit: int = 100) -> Tuple[List[User], int]:
        query = db.query(User)
        total = query.count()
        return query.offset(skip).limit(limit).all(), total

    @staticmethod
    def update(db: Session, db_obj: User, obj_in: UserUpdate) -> User:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj


class CRUDSupplier:
    @staticmethod
    def create(db: Session, obj_in: SupplierCreate) -> Supplier:
        db_obj = Supplier(**obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def get_by_id(db: Session, supplier_id: int) -> Optional[Supplier]:
        return db.query(Supplier).filter(Supplier.id == supplier_id).first()

    @staticmethod
    def list(db: Session, skip: int = 0, limit: int = 100) -> Tuple[List[Supplier], int]:
        query = db.query(Supplier)
        total = query.count()
        return query.offset(skip).limit(limit).all(), total

    @staticmethod
    def update(db: Session, db_obj: Supplier, obj_in: SupplierUpdate) -> Supplier:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj


class CRUDSparePart:
    @staticmethod
    def create(db: Session, obj_in: SparePartCreate) -> SparePart:
        db_obj = SparePart(**obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def get_by_id(db: Session, spare_part_id: int) -> Optional[SparePart]:
        return db.query(SparePart).filter(SparePart.id == spare_part_id).first()

    @staticmethod
    def list(db: Session, skip: int = 0, limit: int = 100) -> Tuple[List[SparePart], int]:
        query = db.query(SparePart)
        total = query.count()
        return query.offset(skip).limit(limit).all(), total

    @staticmethod
    def update(db: Session, db_obj: SparePart, obj_in: SparePartUpdate) -> SparePart:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def get_stock_summary(db: Session, spare_part_id: int) -> dict:
        batches = db.query(SupplierBatch).filter(
            SupplierBatch.spare_part_id == spare_part_id,
            SupplierBatch.is_active == True
        ).all()
        total_stock = sum(b.quantity for b in batches)
        available_stock = sum(b.available_quantity for b in batches)
        spare_part = CRUDSparePart.get_by_id(db, spare_part_id)
        return {
            "total_stock": total_stock,
            "available_stock": available_stock,
            "is_below_safety": available_stock < (spare_part.safety_stock if spare_part else 0)
        }


class CRUDSupplierBatch:
    @staticmethod
    def create(db: Session, obj_in: SupplierBatchCreate) -> SupplierBatch:
        db_obj = SupplierBatch(
            **obj_in.model_dump(),
            available_quantity=obj_in.quantity
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def get_by_id(db: Session, batch_id: int) -> Optional[SupplierBatch]:
        return db.query(SupplierBatch).filter(SupplierBatch.id == batch_id).first()

    @staticmethod
    def get_by_batch_no(db: Session, batch_no: str) -> Optional[SupplierBatch]:
        return db.query(SupplierBatch).filter(SupplierBatch.batch_no == batch_no).first()

    @staticmethod
    def list(db: Session, skip: int = 0, limit: int = 100,
             spare_part_id: Optional[int] = None,
             supplier_id: Optional[int] = None,
             available_only: bool = False) -> Tuple[List[SupplierBatch], int]:
        query = db.query(SupplierBatch)
        if spare_part_id:
            query = query.filter(SupplierBatch.spare_part_id == spare_part_id)
        if supplier_id:
            query = query.filter(SupplierBatch.supplier_id == supplier_id)
        if available_only:
            query = query.filter(SupplierBatch.available_quantity > 0)
        total = query.count()
        return query.offset(skip).limit(limit).all(), total

    @staticmethod
    def update(db: Session, db_obj: SupplierBatch, obj_in: SupplierBatchUpdate) -> SupplierBatch:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def get_ownership_status(db: Session, batch_id: int) -> dict:
        confirmations = db.query(StockOwnershipConfirmation).filter(
            StockOwnershipConfirmation.batch_id == batch_id
        ).all()

        equipment_confirmed = any(
            c.status == ConfirmationStatus.CONFIRMED and c.confirmer_role == UserRole.EQUIPMENT_ENGINEER
            for c in confirmations
        )
        supplier_confirmed = any(
            c.status == ConfirmationStatus.CONFIRMED and c.confirmer_role == UserRole.SUPPLIER
            for c in confirmations
        )
        finance_confirmed = any(
            c.status == ConfirmationStatus.CONFIRMED and c.confirmer_role == UserRole.FINANCE
            for c in confirmations
        )

        return {
            "equipment_confirmed": equipment_confirmed,
            "supplier_confirmed": supplier_confirmed,
            "finance_confirmed": finance_confirmed,
            "is_fully_confirmed": equipment_confirmed and supplier_confirmed and finance_confirmed
        }


class CRUDMaintenanceOrder:
    @staticmethod
    def create(db: Session, obj_in: MaintenanceOrderCreate, created_by: int) -> MaintenanceOrder:
        db_obj = MaintenanceOrder(**obj_in.model_dump(), created_by=created_by)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def get_by_id(db: Session, order_id: int) -> Optional[MaintenanceOrder]:
        return db.query(MaintenanceOrder).filter(MaintenanceOrder.id == order_id).first()

    @staticmethod
    def list(db: Session, skip: int = 0, limit: int = 100) -> Tuple[List[MaintenanceOrder], int]:
        query = db.query(MaintenanceOrder)
        total = query.count()
        return query.offset(skip).limit(limit).all(), total

    @staticmethod
    def update(db: Session, db_obj: MaintenanceOrder, obj_in: MaintenanceOrderUpdate) -> MaintenanceOrder:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj


class CRUDRequisition:
    @staticmethod
    def create(db: Session, obj_in: RequisitionCreate, created_by: int) -> Requisition:
        requisition_no = generate_no("REQ", db)
        db_obj = Requisition(
            requisition_no=requisition_no,
            maintenance_order_id=obj_in.maintenance_order_id,
            remark=obj_in.remark,
            created_by=created_by
        )
        db.add(db_obj)
        db.flush()

        total_amount = 0
        for item_in in obj_in.items:
            batch = CRUDSupplierBatch.get_by_id(db, item_in.batch_id)
            if not batch:
                raise ValueError(f"Batch not found: {item_in.batch_id}")

            ownership_status = CRUDSupplierBatch.get_ownership_status(db, item_in.batch_id)
            if not ownership_status["is_fully_confirmed"]:
                raise ValueError(f"Batch {batch.batch_no} has not been fully confirmed for ownership")

            if batch.available_quantity < item_in.quantity:
                raise ValueError(f"Insufficient available quantity in batch {batch.batch_no}")

            item = RequisitionItem(
                requisition_id=db_obj.id,
                spare_part_id=item_in.spare_part_id,
                batch_id=item_in.batch_id,
                quantity=item_in.quantity,
                unit_price=batch.unit_price,
                amount=item_in.quantity * batch.unit_price,
                remark=item_in.remark
            )
            db.add(item)
            total_amount += item.amount

        db_obj.total_amount = total_amount
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def get_by_id(db: Session, requisition_id: int) -> Optional[Requisition]:
        return db.query(Requisition).filter(Requisition.id == requisition_id).first()

    @staticmethod
    def list(db: Session, skip: int = 0, limit: int = 100,
             status: Optional[RequisitionStatus] = None,
             created_by: Optional[int] = None,
             is_settled: Optional[bool] = None) -> Tuple[List[Requisition], int]:
        query = db.query(Requisition)
        if status:
            query = query.filter(Requisition.status == status)
        if created_by:
            query = query.filter(Requisition.created_by == created_by)
        if is_settled is not None:
            query = query.filter(Requisition.is_settled == is_settled)
        total = query.count()
        return query.order_by(Requisition.created_at.desc()).offset(skip).limit(limit).all(), total

    @staticmethod
    def update_status(db: Session, db_obj: Requisition, status: RequisitionStatus,
                      approved_by: Optional[int] = None) -> Requisition:
        db_obj.status = status
        if status == RequisitionStatus.APPROVED and approved_by:
            db_obj.approved_by = approved_by
            db_obj.approved_at = datetime.utcnow()
        elif status == RequisitionStatus.DELIVERED:
            db_obj.delivered_at = datetime.utcnow()
            for item in db_obj.items:
                batch = CRUDSupplierBatch.get_by_id(db, item.batch_id)
                if batch:
                    batch.available_quantity -= item.quantity
                    batch.quantity -= item.quantity
        db.commit()
        db.refresh(db_obj)
        CRUDSafetyStockAlert.check_and_create_alerts(db)
        return db_obj

    @staticmethod
    def is_period_closed(db: Session, requisition_id: int) -> bool:
        requisition = CRUDRequisition.get_by_id(db, requisition_id)
        if not requisition or not requisition.delivered_at:
            return False
        period = requisition.delivered_at.strftime("%Y-%m")
        closing = db.query(MonthlyClosing).filter(MonthlyClosing.period == period).first()
        return closing.is_closed if closing else False


class CRUDReplenishment:
    @staticmethod
    def create(db: Session, obj_in: ReplenishmentCreate, created_by: int) -> Replenishment:
        replenishment_no = generate_no("RPL", db)
        db_obj = Replenishment(
            replenishment_no=replenishment_no,
            supplier_id=obj_in.supplier_id,
            remark=obj_in.remark,
            created_by=created_by
        )
        db.add(db_obj)
        db.flush()

        total_amount = 0
        for item_in in obj_in.items:
            existing_batch = CRUDSupplierBatch.get_by_batch_no(db, item_in.batch_no)
            if existing_batch:
                raise ValueError(f"Batch number already exists: {item_in.batch_no}")

            item = ReplenishmentItem(
                replenishment_id=db_obj.id,
                **item_in.model_dump(),
                amount=item_in.quantity * item_in.unit_price
            )
            db.add(item)
            total_amount += item.amount

        db_obj.total_amount = total_amount
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def get_by_id(db: Session, replenishment_id: int) -> Optional[Replenishment]:
        return db.query(Replenishment).filter(Replenishment.id == replenishment_id).first()

    @staticmethod
    def list(db: Session, skip: int = 0, limit: int = 100,
             status: Optional[ReplenishmentStatus] = None,
             supplier_id: Optional[int] = None) -> Tuple[List[Replenishment], int]:
        query = db.query(Replenishment)
        if status:
            query = query.filter(Replenishment.status == status)
        if supplier_id:
            query = query.filter(Replenishment.supplier_id == supplier_id)
        total = query.count()
        return query.order_by(Replenishment.created_at.desc()).offset(skip).limit(limit).all(), total

    @staticmethod
    def update_status(db: Session, db_obj: Replenishment, status: ReplenishmentStatus,
                      approved_by: Optional[int] = None) -> Replenishment:
        db_obj.status = status
        if status == ReplenishmentStatus.IN_TRANSIT and approved_by:
            db_obj.approved_by = approved_by
            db_obj.approved_at = datetime.utcnow()
        elif status == ReplenishmentStatus.RECEIVED:
            db_obj.received_at = datetime.utcnow()
            for item in db_obj.items:
                batch = SupplierBatch(
                    batch_no=item.batch_no,
                    spare_part_id=item.spare_part_id,
                    supplier_id=db_obj.supplier_id,
                    quantity=item.quantity,
                    available_quantity=item.quantity,
                    unit_price=item.unit_price,
                    production_date=item.production_date,
                    expiry_date=item.expiry_date,
                    location=item.location
                )
                db.add(batch)
        db.commit()
        db.refresh(db_obj)
        CRUDSafetyStockAlert.check_and_create_alerts(db)
        return db_obj


class CRUDSettlement:
    @staticmethod
    def create(db: Session, obj_in: SettlementCreate, created_by: int) -> Settlement:
        settlement_no = generate_no("SET", db)
        db_obj = Settlement(
            settlement_no=settlement_no,
            supplier_id=obj_in.supplier_id,
            period=obj_in.period,
            remark=obj_in.remark
        )
        db.add(db_obj)
        db.flush()

        total_amount = 0
        for req_id in obj_in.requisition_ids:
            requisition = CRUDRequisition.get_by_id(db, req_id)
            if not requisition:
                raise ValueError(f"Requisition not found: {req_id}")
            if requisition.status != RequisitionStatus.DELIVERED:
                raise ValueError(f"Requisition {requisition.requisition_no} is not delivered")
            if requisition.is_settled:
                raise ValueError(f"Requisition {requisition.requisition_no} is already settled")
            if CRUDRequisition.is_period_closed(db, req_id):
                raise ValueError(f"Requisition {requisition.requisition_no} period is closed")

            requisition.is_settled = True
            requisition.settlement_id = db_obj.id
            requisition.status = RequisitionStatus.SETTLED
            total_amount += requisition.total_amount

        db_obj.total_amount = total_amount
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def get_by_id(db: Session, settlement_id: int) -> Optional[Settlement]:
        return db.query(Settlement).filter(Settlement.id == settlement_id).first()

    @staticmethod
    def list(db: Session, skip: int = 0, limit: int = 100,
             status: Optional[SettlementStatus] = None,
             supplier_id: Optional[int] = None,
             period: Optional[str] = None) -> Tuple[List[Settlement], int]:
        query = db.query(Settlement)
        if status:
            query = query.filter(Settlement.status == status)
        if supplier_id:
            query = query.filter(Settlement.supplier_id == supplier_id)
        if period:
            query = query.filter(Settlement.period == period)
        total = query.count()
        return query.order_by(Settlement.created_at.desc()).offset(skip).limit(limit).all(), total

    @staticmethod
    def update_status(db: Session, db_obj: Settlement, status: SettlementStatus,
                      approved_by: Optional[int] = None) -> Settlement:
        db_obj.status = status
        if status == SettlementStatus.APPROVED and approved_by:
            db_obj.approved_by = approved_by
            db_obj.approved_at = datetime.utcnow()
        elif status == SettlementStatus.PAID:
            db_obj.paid_at = datetime.utcnow()
        db.commit()
        db.refresh(db_obj)
        return db_obj


class CRUDStockOwnershipConfirmation:
    @staticmethod
    def create(db: Session, obj_in: StockOwnershipConfirmationCreate,
               confirmer: User) -> StockOwnershipConfirmation:
        existing = db.query(StockOwnershipConfirmation).filter(
            and_(
                StockOwnershipConfirmation.batch_id == obj_in.batch_id,
                StockOwnershipConfirmation.confirmer_id == confirmer.id
            )
        ).first()
        if existing:
            raise ValueError("Confirmation already exists for this batch and user")

        db_obj = StockOwnershipConfirmation(
            batch_id=obj_in.batch_id,
            confirmer_id=confirmer.id,
            confirmer_role=confirmer.role
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def get_by_id(db: Session, confirmation_id: int) -> Optional[StockOwnershipConfirmation]:
        return db.query(StockOwnershipConfirmation).filter(
            StockOwnershipConfirmation.id == confirmation_id
        ).first()

    @staticmethod
    def list(db: Session, skip: int = 0, limit: int = 100,
             batch_id: Optional[int] = None,
             status: Optional[ConfirmationStatus] = None) -> Tuple[List[StockOwnershipConfirmation], int]:
        query = db.query(StockOwnershipConfirmation)
        if batch_id:
            query = query.filter(StockOwnershipConfirmation.batch_id == batch_id)
        if status:
            query = query.filter(StockOwnershipConfirmation.status == status)
        total = query.count()
        return query.order_by(StockOwnershipConfirmation.created_at.desc()).offset(skip).limit(limit).all(), total

    @staticmethod
    def update(db: Session, db_obj: StockOwnershipConfirmation,
               obj_in: StockOwnershipConfirmationUpdate) -> StockOwnershipConfirmation:
        db_obj.status = obj_in.status
        db_obj.comment = obj_in.comment
        if obj_in.status == ConfirmationStatus.CONFIRMED:
            db_obj.confirmed_at = datetime.utcnow()
        db.commit()
        db.refresh(db_obj)
        return db_obj


class CRUDMonthlyClosing:
    @staticmethod
    def create(db: Session, obj_in: MonthlyClosingCreate, closed_by: int) -> MonthlyClosing:
        existing = db.query(MonthlyClosing).filter(MonthlyClosing.period == obj_in.period).first()
        if existing:
            raise ValueError(f"Monthly closing already exists for period: {obj_in.period}")

        db_obj = MonthlyClosing(
            period=obj_in.period,
            is_closed=True,
            closed_by=closed_by,
            closed_at=datetime.utcnow(),
            remark=obj_in.remark
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def get_by_period(db: Session, period: str) -> Optional[MonthlyClosing]:
        return db.query(MonthlyClosing).filter(MonthlyClosing.period == period).first()

    @staticmethod
    def list(db: Session, skip: int = 0, limit: int = 100) -> Tuple[List[MonthlyClosing], int]:
        query = db.query(MonthlyClosing)
        total = query.count()
        return query.order_by(MonthlyClosing.period.desc()).offset(skip).limit(limit).all(), total

    @staticmethod
    def reopen(db: Session, period: str) -> MonthlyClosing:
        db_obj = CRUDMonthlyClosing.get_by_period(db, period)
        if not db_obj:
            raise ValueError(f"Monthly closing not found for period: {period}")
        db_obj.is_closed = False
        db_obj.closed_by = None
        db_obj.closed_at = None
        db.commit()
        db.refresh(db_obj)
        return db_obj


class CRUDSafetyStockAlert:
    @staticmethod
    def check_and_create_alerts(db: Session) -> None:
        spare_parts = db.query(SparePart).filter(SparePart.is_active == True).all()
        for sp in spare_parts:
            stock_info = CRUDSparePart.get_stock_summary(db, sp.id)
            if stock_info["is_below_safety"] and sp.safety_stock > 0:
                existing = db.query(SafetyStockAlert).filter(
                    and_(
                        SafetyStockAlert.spare_part_id == sp.id,
                        SafetyStockAlert.is_processed == False
                    )
                ).first()
                if not existing:
                    alert = SafetyStockAlert(
                        spare_part_id=sp.id,
                        current_stock=stock_info["available_stock"],
                        safety_stock=sp.safety_stock,
                        shortage=sp.safety_stock - stock_info["available_stock"]
                    )
                    db.add(alert)
        db.commit()

    @staticmethod
    def list(db: Session, skip: int = 0, limit: int = 100,
             is_processed: Optional[bool] = None) -> Tuple[List[SafetyStockAlert], int]:
        query = db.query(SafetyStockAlert)
        if is_processed is not None:
            query = query.filter(SafetyStockAlert.is_processed == is_processed)
        total = query.count()
        return query.order_by(SafetyStockAlert.created_at.desc()).offset(skip).limit(limit).all(), total

    @staticmethod
    def mark_processed(db: Session, alert_id: int, processed_by: int) -> Optional[SafetyStockAlert]:
        alert = db.query(SafetyStockAlert).filter(SafetyStockAlert.id == alert_id).first()
        if alert:
            alert.is_processed = True
            alert.processed_by = processed_by
            alert.processed_at = datetime.utcnow()
            db.commit()
            db.refresh(alert)
        return alert


class CRUDDashboard:
    @staticmethod
    def get_stats(db: Session) -> dict:
        total_spare_parts = db.query(SparePart).count()
        total_batches = db.query(SupplierBatch).filter(SupplierBatch.is_active == True).count()
        pending_requisitions = db.query(Requisition).filter(
            Requisition.status.in_([RequisitionStatus.PENDING, RequisitionStatus.DRAFT])
        ).count()
        pending_replenishments = db.query(Replenishment).filter(
            Replenishment.status.in_([
                ReplenishmentStatus.DRAFT,
                ReplenishmentStatus.PENDING,
                ReplenishmentStatus.IN_TRANSIT
            ])
        ).count()
        pending_settlements = db.query(Settlement).filter(
            Settlement.status.in_([SettlementStatus.PENDING, SettlementStatus.APPROVED])
        ).count()
        low_stock_alerts = db.query(SafetyStockAlert).filter(
            SafetyStockAlert.is_processed == False
        ).count()
        pending_ownership = db.query(StockOwnershipConfirmation).filter(
            StockOwnershipConfirmation.status == ConfirmationStatus.PENDING
        ).count()

        total_stock_value = db.query(
            func.sum(SupplierBatch.available_quantity * SupplierBatch.unit_price)
        ).filter(SupplierBatch.is_active == True).scalar() or 0

        return {
            "total_spare_parts": total_spare_parts,
            "total_batches": total_batches,
            "pending_requisitions": pending_requisitions,
            "pending_replenishments": pending_replenishments,
            "pending_settlements": pending_settlements,
            "low_stock_alerts": low_stock_alerts,
            "pending_ownership_confirmations": pending_ownership,
            "total_stock_value": float(total_stock_value)
        }
