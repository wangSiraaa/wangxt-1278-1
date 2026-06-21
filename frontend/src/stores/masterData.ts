import { defineStore } from 'pinia'
import { ref } from 'vue'
import type {
  Supplier, SparePart, SupplierBatch,
  MaintenanceOrder, StockOwnershipConfirmation
} from '@/types'
import { masterDataApi, inventoryApi } from '@/api'

export const useMasterDataStore = defineStore('masterData', {
  state: () => ({
    suppliers: ref<Supplier[]>([]),
    spareParts: ref<SparePart[]>([]),
    batches: ref<SupplierBatch[]>([]),
    maintenanceOrders: ref<MaintenanceOrder[]>([]),
    ownershipConfirmations: ref<StockOwnershipConfirmation[]>([]),
    loading: ref(false)
  }),
  actions: {
    async fetchSuppliers() {
      this.loading = true
      try {
        this.suppliers = await masterDataApi.listSuppliers()
      } finally {
        this.loading = false
      }
    },
    async createSupplier(data: Omit<Supplier, 'id' | 'is_active' | 'created_at' | 'updated_at'>) {
      const supplier = await masterDataApi.createSupplier(data)
      this.suppliers.push(supplier)
      return supplier
    },
    async updateSupplier(id: number, data: Partial<Supplier>) {
      const updated = await masterDataApi.updateSupplier(id, data)
      const index = this.suppliers.findIndex(s => s.id === id)
      if (index !== -1) {
        this.suppliers[index] = updated
      }
      return updated
    },

    async fetchSpareParts() {
      this.loading = true
      try {
        this.spareParts = await masterDataApi.listSpareParts()
      } finally {
        this.loading = false
      }
    },
    async createSparePart(data: Omit<SparePart, 'id' | 'is_active' | 'created_at' | 'updated_at'>) {
      const part = await masterDataApi.createSparePart(data)
      this.spareParts.push(part)
      return part
    },
    async updateSparePart(id: number, data: Partial<SparePart>) {
      const updated = await masterDataApi.updateSparePart(id, data)
      const index = this.spareParts.findIndex(s => s.id === id)
      if (index !== -1) {
        this.spareParts[index] = updated
      }
      return updated
    },

    async fetchBatches(params?: { spare_part_id?: number; supplier_id?: number; available_only?: boolean }) {
      this.loading = true
      try {
        this.batches = await inventoryApi.listBatches(params)
      } finally {
        this.loading = false
      }
    },
    async createBatch(data: Omit<SupplierBatch, 'id' | 'available_quantity' | 'is_active' | 'created_at' | 'updated_at'>) {
      const batch = await inventoryApi.createBatch(data)
      this.batches.push(batch)
      return batch
    },
    async confirmBatchOwnership(batchId: number) {
      const confirmation = await inventoryApi.confirmOwnership(batchId)
      await this.fetchBatches()
      return confirmation
    },
    async updateConfirmation(id: number, data: { status: any; comment?: string }) {
      const updated = await inventoryApi.updateConfirmation(id, data)
      const index = this.ownershipConfirmations.findIndex(c => c.id === id)
      if (index !== -1) {
        this.ownershipConfirmations[index] = updated
      }
      await this.fetchBatches()
      return updated
    },

    async fetchMaintenanceOrders() {
      this.loading = true
      try {
        this.maintenanceOrders = await inventoryApi.listMaintenanceOrders()
      } finally {
        this.loading = false
      }
    },
    async createMaintenanceOrder(data: Omit<MaintenanceOrder, 'id' | 'is_closed' | 'created_by' | 'created_at' | 'updated_at'>) {
      const order = await inventoryApi.createMaintenanceOrder(data)
      this.maintenanceOrders.push(order)
      return order
    },
    async updateMaintenanceOrder(id: number, data: Partial<MaintenanceOrder>) {
      const updated = await inventoryApi.updateMaintenanceOrder(id, data)
      const index = this.maintenanceOrders.findIndex(o => o.id === id)
      if (index !== -1) {
        this.maintenanceOrders[index] = updated
      }
      return updated
    },

    async fetchOwnershipConfirmations(params?: { batch_id?: number }) {
      this.loading = true
      try {
        this.ownershipConfirmations = await inventoryApi.listOwnershipConfirmations(params)
      } finally {
        this.loading = false
      }
    }
  }
})
