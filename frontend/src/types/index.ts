export type UserRole = 'equipment_engineer' | 'supplier' | 'finance' | 'admin'
export type RequisitionStatus = 'draft' | 'pending' | 'approved' | 'rejected' | 'delivered' | 'settled'
export type ReplenishmentStatus = 'draft' | 'pending' | 'in_transit' | 'received' | 'rejected'
export type SettlementStatus = 'pending' | 'approved' | 'paid' | 'rejected'
export type ConfirmationStatus = 'pending' | 'confirmed' | 'rejected'

export interface User {
  id: number
  username: string
  email: string
  full_name: string
  role: UserRole
  supplier_id?: number
  is_active: boolean
  created_at: string
  updated_at?: string
}

export interface Supplier {
  id: number
  code: string
  name: string
  contact_person?: string
  phone?: string
  email?: string
  address?: string
  is_active: boolean
  created_at: string
  updated_at?: string
}

export interface SparePart {
  id: number
  code: string
  name: string
  specification?: string
  unit: string
  safety_stock: number
  description?: string
  is_active: boolean
  created_at: string
  updated_at?: string
  total_stock?: number
  available_stock?: number
  is_below_safety?: boolean
}

export interface BatchOwnershipStatus {
  equipment_confirmed: boolean
  supplier_confirmed: boolean
  finance_confirmed: boolean
  is_fully_confirmed: boolean
}

export interface SupplierBatch {
  id: number
  batch_no: string
  spare_part_id: number
  supplier_id: number
  quantity: number
  available_quantity: number
  unit_price: number
  production_date?: string
  expiry_date?: string
  location?: string
  is_active: boolean
  created_at: string
  updated_at?: string
  spare_part?: SparePart
  supplier?: Supplier
  ownership_status?: BatchOwnershipStatus
}

export interface MaintenanceOrder {
  id: number
  order_no: string
  equipment_code: string
  equipment_name: string
  description?: string
  is_closed: boolean
  created_by: number
  created_at: string
  updated_at?: string
}

export interface RequisitionItem {
  id: number
  requisition_id: number
  spare_part_id: number
  batch_id: number
  quantity: number
  unit_price: number
  amount: number
  remark?: string
  spare_part?: SparePart
  batch?: SupplierBatch
}

export interface Requisition {
  id: number
  requisition_no: string
  maintenance_order_id: number
  status: RequisitionStatus
  total_amount: number
  remark?: string
  is_settled: boolean
  settlement_id?: number
  created_by: number
  approved_by?: number
  approved_at?: string
  delivered_at?: string
  created_at: string
  updated_at?: string
  items: RequisitionItem[]
  maintenance_order?: MaintenanceOrder
  creator?: User
}

export interface ReplenishmentItem {
  id: number
  replenishment_id: number
  spare_part_id: number
  batch_no: string
  quantity: number
  unit_price: number
  amount: number
  production_date?: string
  expiry_date?: string
  location?: string
  remark?: string
  spare_part?: SparePart
}

export interface Replenishment {
  id: number
  replenishment_no: string
  supplier_id: number
  status: ReplenishmentStatus
  total_amount: number
  remark?: string
  created_by: number
  approved_by?: number
  approved_at?: string
  received_at?: string
  created_at: string
  updated_at?: string
  items: ReplenishmentItem[]
  supplier?: Supplier
  creator?: User
}

export interface Settlement {
  id: number
  settlement_no: string
  supplier_id: number
  period: string
  status: SettlementStatus
  total_amount: number
  remark?: string
  approved_by?: number
  approved_at?: string
  paid_at?: string
  created_at: string
  updated_at?: string
  supplier?: Supplier
  requisitions: Requisition[]
}

export interface StockOwnershipConfirmation {
  id: number
  batch_id: number
  confirmer_id: number
  confirmer_role: UserRole
  status: ConfirmationStatus
  comment?: string
  confirmed_at?: string
  created_at: string
  confirmer?: User
}

export interface MonthlyClosing {
  id: number
  period: string
  is_closed: boolean
  closed_by?: number
  closed_at?: string
  remark?: string
  created_at: string
}

export interface SafetyStockAlert {
  id: number
  spare_part_id: number
  spare_part?: SparePart
  current_stock: number
  safety_stock: number
  shortage: number
  is_processed: boolean
  processed_by?: number
  processed_at?: string
  created_at: string
}

export interface DashboardStats {
  total_spare_parts: number
  total_batches: number
  pending_requisitions: number
  pending_replenishments: number
  pending_settlements: number
  low_stock_alerts: number
  pending_ownership_confirmations: number
  total_stock_value: number
}

export interface ApiResponse<T> {
  data: T
  message?: string
}

export interface LoginRequest {
  username: string
  password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
}

export interface PageQuery {
  skip?: number
  limit?: number
}

export interface RequisitionItemCreate {
  id?: number
  batch_id: number
  spare_part_id?: number
  quantity: number
  unit_price?: number
}

export interface RequisitionCreate {
  maintenance_order_id: number
  items: RequisitionItemCreate[]
  remark?: string
}

export interface ReplenishmentItemCreate {
  spare_part_id: number
  batch_no: string
  quantity: number
  unit_price: number
  production_date?: string
  expiry_date?: string
}

export interface ReplenishmentCreate {
  supplier_id: number
  items: ReplenishmentItemCreate[]
  remark?: string
}

export interface SettlementCreate {
  supplier_id: number
  period: string
  requisition_ids: number[]
  remark?: string
}
