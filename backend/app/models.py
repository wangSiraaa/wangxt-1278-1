from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text, Enum, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class UserRole(str, enum.Enum):
    EQUIPMENT_ENGINEER = "equipment_engineer"
    SUPPLIER = "supplier"
    FINANCE = "finance"
    ADMIN = "admin"


class RequisitionStatus(str, enum.Enum):
    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    DELIVERED = "delivered"
    SETTLED = "settled"


class ReplenishmentStatus(str, enum.Enum):
    DRAFT = "draft"
    PENDING = "pending"
    IN_TRANSIT = "in_transit"
    RECEIVED = "received"
    REJECTED = "rejected"


class SettlementStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    PAID = "paid"
    REJECTED = "rejected"


class ConfirmationStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    supplier = relationship("Supplier", back_populates="users")
    created_requisitions = relationship("Requisition", foreign_keys="Requisition.created_by", back_populates="creator")
    created_replenishments = relationship("Replenishment", foreign_keys="Replenishment.created_by", back_populates="creator")
    ownership_confirmations = relationship("StockOwnershipConfirmation", back_populates="confirmer")


class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(200), nullable=False)
    contact_person = Column(String(100))
    phone = Column(String(20))
    email = Column(String(100))
    address = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    users = relationship("User", back_populates="supplier")
    batches = relationship("SupplierBatch", back_populates="supplier")
    replenishments = relationship("Replenishment", back_populates="supplier")
    settlements = relationship("Settlement", back_populates="supplier")


class SparePart(Base):
    __tablename__ = "spare_parts"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(200), nullable=False)
    specification = Column(String(500))
    unit = Column(String(20), nullable=False)
    safety_stock = Column(Float, default=0)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    batches = relationship("SupplierBatch", back_populates="spare_part")
    requisition_items = relationship("RequisitionItem", back_populates="spare_part")
    replenishment_items = relationship("ReplenishmentItem", back_populates="spare_part")


class SupplierBatch(Base):
    __tablename__ = "supplier_batches"

    id = Column(Integer, primary_key=True, index=True)
    batch_no = Column(String(100), unique=True, index=True, nullable=False)
    spare_part_id = Column(Integer, ForeignKey("spare_parts.id"), nullable=False)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    quantity = Column(Float, nullable=False, default=0)
    available_quantity = Column(Float, nullable=False, default=0)
    unit_price = Column(Float, nullable=False)
    production_date = Column(Date)
    expiry_date = Column(Date)
    location = Column(String(200))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    spare_part = relationship("SparePart", back_populates="batches")
    supplier = relationship("Supplier", back_populates="batches")
    ownership_confirmations = relationship("StockOwnershipConfirmation", back_populates="batch")
    requisition_items = relationship("RequisitionItem", back_populates="batch")


class MaintenanceOrder(Base):
    __tablename__ = "maintenance_orders"

    id = Column(Integer, primary_key=True, index=True)
    order_no = Column(String(50), unique=True, index=True, nullable=False)
    equipment_code = Column(String(50), nullable=False)
    equipment_name = Column(String(200), nullable=False)
    description = Column(Text)
    is_closed = Column(Boolean, default=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    requisitions = relationship("Requisition", back_populates="maintenance_order")


class Requisition(Base):
    __tablename__ = "requisitions"

    id = Column(Integer, primary_key=True, index=True)
    requisition_no = Column(String(50), unique=True, index=True, nullable=False)
    maintenance_order_id = Column(Integer, ForeignKey("maintenance_orders.id"), nullable=False)
    status = Column(Enum(RequisitionStatus), default=RequisitionStatus.DRAFT)
    total_amount = Column(Float, default=0)
    remark = Column(Text)
    is_settled = Column(Boolean, default=False)
    settlement_id = Column(Integer, ForeignKey("settlements.id"), nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    maintenance_order = relationship("MaintenanceOrder", back_populates="requisitions")
    creator = relationship("User", foreign_keys=[created_by], back_populates="created_requisitions")
    items = relationship("RequisitionItem", back_populates="requisition", cascade="all, delete-orphan")
    settlement = relationship("Settlement", back_populates="requisitions")


class RequisitionItem(Base):
    __tablename__ = "requisition_items"

    id = Column(Integer, primary_key=True, index=True)
    requisition_id = Column(Integer, ForeignKey("requisitions.id"), nullable=False)
    spare_part_id = Column(Integer, ForeignKey("spare_parts.id"), nullable=False)
    batch_id = Column(Integer, ForeignKey("supplier_batches.id"), nullable=False)
    quantity = Column(Float, nullable=False)
    unit_price = Column(Float, nullable=False)
    amount = Column(Float, nullable=False)
    remark = Column(Text)

    requisition = relationship("Requisition", back_populates="items")
    spare_part = relationship("SparePart", back_populates="requisition_items")
    batch = relationship("SupplierBatch", back_populates="requisition_items")


class Replenishment(Base):
    __tablename__ = "replenishments"

    id = Column(Integer, primary_key=True, index=True)
    replenishment_no = Column(String(50), unique=True, index=True, nullable=False)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    status = Column(Enum(ReplenishmentStatus), default=ReplenishmentStatus.DRAFT)
    total_amount = Column(Float, default=0)
    remark = Column(Text)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    received_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    supplier = relationship("Supplier", back_populates="replenishments")
    creator = relationship("User", foreign_keys=[created_by], back_populates="created_replenishments")
    items = relationship("ReplenishmentItem", back_populates="replenishment", cascade="all, delete-orphan")


class ReplenishmentItem(Base):
    __tablename__ = "replenishment_items"

    id = Column(Integer, primary_key=True, index=True)
    replenishment_id = Column(Integer, ForeignKey("replenishments.id"), nullable=False)
    spare_part_id = Column(Integer, ForeignKey("spare_parts.id"), nullable=False)
    batch_no = Column(String(100), nullable=False)
    quantity = Column(Float, nullable=False)
    unit_price = Column(Float, nullable=False)
    amount = Column(Float, nullable=False)
    production_date = Column(Date)
    expiry_date = Column(Date)
    location = Column(String(200))
    remark = Column(Text)

    replenishment = relationship("Replenishment", back_populates="items")
    spare_part = relationship("SparePart", back_populates="replenishment_items")


class Settlement(Base):
    __tablename__ = "settlements"

    id = Column(Integer, primary_key=True, index=True)
    settlement_no = Column(String(50), unique=True, index=True, nullable=False)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    period = Column(String(20), nullable=False)
    status = Column(Enum(SettlementStatus), default=SettlementStatus.PENDING)
    total_amount = Column(Float, default=0)
    remark = Column(Text)
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    paid_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    supplier = relationship("Supplier", back_populates="settlements")
    requisitions = relationship("Requisition", back_populates="settlement")


class StockOwnershipConfirmation(Base):
    __tablename__ = "stock_ownership_confirmations"

    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(Integer, ForeignKey("supplier_batches.id"), nullable=False)
    confirmer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    confirmer_role = Column(Enum(UserRole), nullable=False)
    status = Column(Enum(ConfirmationStatus), default=ConfirmationStatus.PENDING)
    comment = Column(Text)
    confirmed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    batch = relationship("SupplierBatch", back_populates="ownership_confirmations")
    confirmer = relationship("User", back_populates="ownership_confirmations")


class MonthlyClosing(Base):
    __tablename__ = "monthly_closings"

    id = Column(Integer, primary_key=True, index=True)
    period = Column(String(20), unique=True, nullable=False)
    is_closed = Column(Boolean, default=False)
    closed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    closed_at = Column(DateTime(timezone=True), nullable=True)
    remark = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class SafetyStockAlert(Base):
    __tablename__ = "safety_stock_alerts"

    id = Column(Integer, primary_key=True, index=True)
    spare_part_id = Column(Integer, ForeignKey("spare_parts.id"), nullable=False)
    current_stock = Column(Float, nullable=False)
    safety_stock = Column(Float, nullable=False)
    shortage = Column(Float, nullable=False)
    is_processed = Column(Boolean, default=False)
    processed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    processed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
