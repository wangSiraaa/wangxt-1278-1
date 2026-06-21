import { http } from '@/utils/http'
import type {
  User, LoginRequest, LoginResponse,
  Supplier, SparePart, SupplierBatch,
  MaintenanceOrder, Requisition, RequisitionCreate,
  Replenishment, ReplenishmentCreate,
  Settlement, SettlementCreate,
  StockOwnershipConfirmation, MonthlyClosing,
  SafetyStockAlert, DashboardStats,
  RequisitionStatus, ReplenishmentStatus, SettlementStatus,
  ConfirmationStatus
} from '@/types'

export const authApi = {
  login: (data: LoginRequest): Promise<LoginResponse> =>
    http.post('/auth/login', new URLSearchParams(data as any)),
  register: (data: { username: string; password: string; email: string; full_name: string; role: string; supplier_id?: number }): Promise<User> =>
    http.post('/auth/register', data),
  getCurrentUser: (): Promise<User> =>
    http.get('/auth/me'),
  listUsers: (): Promise<User[]> =>
    http.get('/auth/users')
}

export const masterDataApi = {
  createSupplier: (data: Omit<Supplier, 'id' | 'is_active' | 'created_at' | 'updated_at'>): Promise<Supplier> =>
    http.post('/suppliers', data),
  listSuppliers: (): Promise<Supplier[]> =>
    http.get('/suppliers'),
  getSupplier: (id: number): Promise<Supplier> =>
    http.get(`/suppliers/${id}`),
  updateSupplier: (id: number, data: Partial<Supplier>): Promise<Supplier> =>
    http.put(`/suppliers/${id}`, data),

  createSparePart: (data: Omit<SparePart, 'id' | 'is_active' | 'created_at' | 'updated_at'>): Promise<SparePart> =>
    http.post('/spare-parts', data),
  listSpareParts: (): Promise<SparePart[]> =>
    http.get('/spare-parts'),
  getSparePart: (id: number): Promise<SparePart> =>
    http.get(`/spare-parts/${id}`),
  updateSparePart: (id: number, data: Partial<SparePart>): Promise<SparePart> =>
    http.put(`/spare-parts/${id}`, data)
}

export const inventoryApi = {
  createBatch: (data: Omit<SupplierBatch, 'id' | 'available_quantity' | 'is_active' | 'created_at' | 'updated_at'>): Promise<SupplierBatch> =>
    http.post('/batches', data),
  listBatches: (params?: { spare_part_id?: number; supplier_id?: number; available_only?: boolean }): Promise<SupplierBatch[]> =>
    http.get('/batches', { params }),
  getBatch: (id: number): Promise<SupplierBatch> =>
    http.get(`/batches/${id}`),
  updateBatch: (id: number, data: Partial<SupplierBatch>): Promise<SupplierBatch> =>
    http.put(`/batches/${id}`, data),
  confirmOwnership: (batchId: number): Promise<StockOwnershipConfirmation> =>
    http.post(`/batches/${batchId}/confirm-ownership`),

  listOwnershipConfirmations: (params?: { batch_id?: number }): Promise<StockOwnershipConfirmation[]> =>
    http.get('/ownership-confirmations', { params }),
  updateConfirmation: (id: number, data: { status: ConfirmationStatus; comment?: string }): Promise<StockOwnershipConfirmation> =>
    http.put(`/ownership-confirmations/${id}`, data),

  createMaintenanceOrder: (data: Omit<MaintenanceOrder, 'id' | 'is_closed' | 'created_by' | 'created_at' | 'updated_at'>): Promise<MaintenanceOrder> =>
    http.post('/maintenance-orders', data),
  listMaintenanceOrders: (): Promise<MaintenanceOrder[]> =>
    http.get('/maintenance-orders'),
  getMaintenanceOrder: (id: number): Promise<MaintenanceOrder> =>
    http.get(`/maintenance-orders/${id}`),
  updateMaintenanceOrder: (id: number, data: Partial<MaintenanceOrder>): Promise<MaintenanceOrder> =>
    http.put(`/maintenance-orders/${id}`, data)
}

export const requisitionApi = {
  create: (data: RequisitionCreate): Promise<Requisition> =>
    http.post('/requisitions', data),
  list: (params?: { status?: RequisitionStatus; is_settled?: boolean }): Promise<Requisition[]> =>
    http.get('/requisitions', { params }),
  get: (id: number): Promise<Requisition> =>
    http.get(`/requisitions/${id}`),
  submit: (id: number): Promise<Requisition> =>
    http.post(`/requisitions/${id}/submit`),
  approve: (id: number, approved: boolean, comment?: string): Promise<Requisition> =>
    http.post(`/requisitions/${id}/approve`, { approved, comment }),
  deliver: (id: number): Promise<Requisition> =>
    http.post(`/requisitions/${id}/deliver`),
  update: (id: number, data: Partial<Requisition>): Promise<Requisition> =>
    http.put(`/requisitions/${id}`, data)
}

export const replenishmentApi = {
  create: (data: ReplenishmentCreate): Promise<Replenishment> =>
    http.post('/replenishments', data),
  list: (params?: { status?: ReplenishmentStatus }): Promise<Replenishment[]> =>
    http.get('/replenishments', { params }),
  get: (id: number): Promise<Replenishment> =>
    http.get(`/replenishments/${id}`),
  submit: (id: number): Promise<Replenishment> =>
    http.post(`/replenishments/${id}/submit`),
  approve: (id: number, approved: boolean): Promise<Replenishment> =>
    http.post(`/replenishments/${id}/approve?approved=${approved}`),
  receive: (id: number): Promise<Replenishment> =>
    http.post(`/replenishments/${id}/receive`)
}

export const settlementApi = {
  create: (data: SettlementCreate): Promise<Settlement> =>
    http.post('/settlements', data),
  list: (params?: { status?: SettlementStatus; period?: string }): Promise<Settlement[]> =>
    http.get('/settlements', { params }),
  get: (id: number): Promise<Settlement> =>
    http.get(`/settlements/${id}`),
  approve: (id: number, approved: boolean): Promise<Settlement> =>
    http.post(`/settlements/${id}/approve?approved=${approved}`),
  pay: (id: number): Promise<Settlement> =>
    http.post(`/settlements/${id}/pay`)
}

export const systemApi = {
  createMonthlyClosing: (data: { period: string; remark?: string }): Promise<MonthlyClosing> =>
    http.post('/monthly-closings', data),
  listMonthlyClosings: (): Promise<MonthlyClosing[]> =>
    http.get('/monthly-closings'),
  reopenMonthlyClosing: (period: string): Promise<MonthlyClosing> =>
    http.post(`/monthly-closings/${period}/reopen`),
  checkPeriod: (period: string): Promise<{ period: string; is_closed: boolean; closed_at?: string }> =>
    http.get('/check-period', { params: { period } }),
  checkRequisitionPeriod: (requisitionId: number): Promise<{ requisition_id: number; is_period_closed: boolean; period?: string; can_modify: boolean }> =>
    http.post(`/check-requisition-period/${requisitionId}`),

  listSafetyStockAlerts: (params?: { is_processed?: boolean }): Promise<SafetyStockAlert[]> =>
    http.get('/safety-stock-alerts', { params }),
  processAlert: (id: number): Promise<SafetyStockAlert> =>
    http.post(`/safety-stock-alerts/${id}/process`),

  getDashboardStats: (): Promise<DashboardStats> =>
    http.get('/dashboard/stats')
}
