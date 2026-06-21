from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime, date
from app.models import UserRole, RequisitionStatus, ReplenishmentStatus, SettlementStatus, ConfirmationStatus


class UserBase(BaseModel):
    username: str = Field(..., max_length=50)
    email: EmailStr
    full_name: str = Field(..., max_length=100)
    role: UserRole
    supplier_id: Optional[int] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    supplier_id: Optional[int] = None
    is_active: Optional[bool] = None


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None


class SupplierBase(BaseModel):
    code: str = Field(..., max_length=50)
    name: str = Field(..., max_length=200)
    contact_person: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    address: Optional[str] = None


class SupplierCreate(SupplierBase):
    pass


class SupplierUpdate(BaseModel):
    name: Optional[str] = None
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    is_active: Optional[bool] = None


class SupplierResponse(SupplierBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SparePartBase(BaseModel):
    code: str = Field(..., max_length=50)
    name: str = Field(..., max_length=200)
    specification: Optional[str] = Field(None, max_length=500)
    unit: str = Field(..., max_length=20)
    safety_stock: float = Field(default=0, ge=0)
    description: Optional[str] = None


class SparePartCreate(SparePartBase):
    pass


class SparePartUpdate(BaseModel):
    name: Optional[str] = None
    specification: Optional[str] = None
    unit: Optional[str] = None
    safety_stock: Optional[float] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class SparePartResponse(SparePartBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SparePartStockResponse(SparePartResponse):
    total_stock: float = 0
    available_stock: float = 0
    is_below_safety: bool = False


class SupplierBatchBase(BaseModel):
    batch_no: str = Field(..., max_length=100)
    spare_part_id: int
    supplier_id: int
    quantity: float = Field(..., gt=0)
    unit_price: float = Field(..., gt=0)
    production_date: Optional[date] = None
    expiry_date: Optional[date] = None
    location: Optional[str] = Field(None, max_length=200)


class SupplierBatchCreate(SupplierBatchBase):
    pass


class SupplierBatchUpdate(BaseModel):
    quantity: Optional[float] = None
    unit_price: Optional[float] = None
    production_date: Optional[date] = None
    expiry_date: Optional[date] = None
    location: Optional[str] = None
    is_active: Optional[bool] = None


class SupplierBatchResponse(SupplierBatchBase):
    id: int
    available_quantity: float
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    spare_part: Optional[SparePartResponse] = None
    supplier: Optional[SupplierResponse] = None

    class Config:
        from_attributes = True


class BatchOwnershipStatus(BaseModel):
    equipment_confirmed: bool = False
    supplier_confirmed: bool = False
    finance_confirmed: bool = False
    is_fully_confirmed: bool = False


class SupplierBatchWithOwnershipResponse(SupplierBatchResponse):
    ownership_status: BatchOwnershipStatus


class MaintenanceOrderBase(BaseModel):
    order_no: str = Field(..., max_length=50)
    equipment_code: str = Field(..., max_length=50)
    equipment_name: str = Field(..., max_length=200)
    description: Optional[str] = None


class MaintenanceOrderCreate(MaintenanceOrderBase):
    pass


class MaintenanceOrderUpdate(BaseModel):
    equipment_code: Optional[str] = None
    equipment_name: Optional[str] = None
    description: Optional[str] = None
    is_closed: Optional[bool] = None


class MaintenanceOrderResponse(MaintenanceOrderBase):
    id: int
    is_closed: bool
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class RequisitionItemBase(BaseModel):
    spare_part_id: int
    batch_id: int
    quantity: float = Field(..., gt=0)
    remark: Optional[str] = None


class RequisitionItemCreate(RequisitionItemBase):
    pass


class RequisitionItemResponse(RequisitionItemBase):
    id: int
    unit_price: float
    amount: float
    spare_part: Optional[SparePartResponse] = None
    batch: Optional[SupplierBatchResponse] = None

    class Config:
        from_attributes = True


class RequisitionBase(BaseModel):
    maintenance_order_id: int
    remark: Optional[str] = None


class RequisitionCreate(RequisitionBase):
    items: List[RequisitionItemCreate]


class RequisitionUpdate(BaseModel):
    maintenance_order_id: Optional[int] = None
    remark: Optional[str] = None
    status: Optional[RequisitionStatus] = None


class RequisitionResponse(RequisitionBase):
    id: int
    requisition_no: str
    status: RequisitionStatus
    total_amount: float
    is_settled: bool
    settlement_id: Optional[int] = None
    created_by: int
    approved_by: Optional[int] = None
    approved_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    items: List[RequisitionItemResponse] = []
    maintenance_order: Optional[MaintenanceOrderResponse] = None
    creator: Optional[UserResponse] = None

    class Config:
        from_attributes = True


class RequisitionApprove(BaseModel):
    approved: bool
    comment: Optional[str] = None


class ReplenishmentItemBase(BaseModel):
    spare_part_id: int
    batch_no: str = Field(..., max_length=100)
    quantity: float = Field(..., gt=0)
    unit_price: float = Field(..., gt=0)
    production_date: Optional[date] = None
    expiry_date: Optional[date] = None
    location: Optional[str] = Field(None, max_length=200)
    remark: Optional[str] = None


class ReplenishmentItemCreate(ReplenishmentItemBase):
    pass


class ReplenishmentItemResponse(ReplenishmentItemBase):
    id: int
    amount: float
    spare_part: Optional[SparePartResponse] = None

    class Config:
        from_attributes = True


class ReplenishmentBase(BaseModel):
    supplier_id: int
    remark: Optional[str] = None


class ReplenishmentCreate(ReplenishmentBase):
    items: List[ReplenishmentItemCreate]


class ReplenishmentUpdate(BaseModel):
    remark: Optional[str] = None
    status: Optional[ReplenishmentStatus] = None


class ReplenishmentResponse(ReplenishmentBase):
    id: int
    replenishment_no: str
    status: ReplenishmentStatus
    total_amount: float
    created_by: int
    approved_by: Optional[int] = None
    approved_at: Optional[datetime] = None
    received_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    items: List[ReplenishmentItemResponse] = []
    supplier: Optional[SupplierResponse] = None
    creator: Optional[UserResponse] = None

    class Config:
        from_attributes = True


class SettlementBase(BaseModel):
    supplier_id: int
    period: str = Field(..., max_length=20)
    remark: Optional[str] = None


class SettlementCreate(SettlementBase):
    requisition_ids: List[int]


class SettlementUpdate(BaseModel):
    status: Optional[SettlementStatus] = None
    remark: Optional[str] = None


class SettlementResponse(SettlementBase):
    id: int
    settlement_no: str
    status: SettlementStatus
    total_amount: float
    approved_by: Optional[int] = None
    approved_at: Optional[datetime] = None
    paid_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    supplier: Optional[SupplierResponse] = None
    requisitions: List[RequisitionResponse] = []

    class Config:
        from_attributes = True


class StockOwnershipConfirmationBase(BaseModel):
    batch_id: int


class StockOwnershipConfirmationCreate(StockOwnershipConfirmationBase):
    pass


class StockOwnershipConfirmationUpdate(BaseModel):
    status: ConfirmationStatus
    comment: Optional[str] = None


class StockOwnershipConfirmationResponse(StockOwnershipConfirmationBase):
    id: int
    confirmer_id: int
    confirmer_role: UserRole
    status: ConfirmationStatus
    comment: Optional[str] = None
    confirmed_at: Optional[datetime] = None
    created_at: datetime
    confirmer: Optional[UserResponse] = None

    class Config:
        from_attributes = True


class MonthlyClosingBase(BaseModel):
    period: str = Field(..., max_length=20)
    remark: Optional[str] = None


class MonthlyClosingCreate(MonthlyClosingBase):
    pass


class MonthlyClosingResponse(MonthlyClosingBase):
    id: int
    is_closed: bool
    closed_by: Optional[int] = None
    closed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class SafetyStockAlertResponse(BaseModel):
    id: int
    spare_part_id: int
    spare_part: Optional[SparePartResponse] = None
    current_stock: float
    safety_stock: float
    shortage: float
    is_processed: bool
    processed_by: Optional[int] = None
    processed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class DashboardStats(BaseModel):
    total_spare_parts: int
    total_batches: int
    pending_requisitions: int
    pending_replenishments: int
    pending_settlements: int
    low_stock_alerts: int
    pending_ownership_confirmations: int
    total_stock_value: float
