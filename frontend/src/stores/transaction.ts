import { defineStore } from 'pinia'
import { ref } from 'vue'
import type {
  Requisition, Replenishment, Settlement,
  RequisitionStatus, ReplenishmentStatus, SettlementStatus,
  RequisitionCreate, ReplenishmentCreate, SettlementCreate
} from '@/types'
import { requisitionApi, replenishmentApi, settlementApi } from '@/api'

export const useTransactionStore = defineStore('transaction', {
  state: () => ({
    requisitions: ref<Requisition[]>([]),
    replenishments: ref<Replenishment[]>([]),
    settlements: ref<Settlement[]>([]),
    loading: ref(false)
  }),
  actions: {
    async fetchRequisitions(params?: { status?: RequisitionStatus; is_settled?: boolean }) {
      this.loading = true
      try {
        this.requisitions = await requisitionApi.list(params)
      } finally {
        this.loading = false
      }
    },
    async createRequisition(data: RequisitionCreate) {
      const requisition = await requisitionApi.create(data)
      this.requisitions.unshift(requisition)
      return requisition
    },
    async submitRequisition(id: number) {
      const updated = await requisitionApi.submit(id)
      this.updateRequisitionInStore(id, updated)
      return updated
    },
    async approveRequisition(id: number, approved: boolean, comment?: string) {
      const updated = await requisitionApi.approve(id, approved, comment)
      this.updateRequisitionInStore(id, updated)
      return updated
    },
    async deliverRequisition(id: number) {
      const updated = await requisitionApi.deliver(id)
      this.updateRequisitionInStore(id, updated)
      return updated
    },
    async updateRequisition(id: number, data: Partial<Requisition>) {
      const updated = await requisitionApi.update(id, data)
      this.updateRequisitionInStore(id, updated)
      return updated
    },
    updateRequisitionInStore(id: number, updated: Requisition) {
      const index = this.requisitions.findIndex(r => r.id === id)
      if (index !== -1) {
        this.requisitions[index] = updated
      }
    },

    async fetchReplenishments(params?: { status?: ReplenishmentStatus }) {
      this.loading = true
      try {
        this.replenishments = await replenishmentApi.list(params)
      } finally {
        this.loading = false
      }
    },
    async createReplenishment(data: ReplenishmentCreate) {
      const replenishment = await replenishmentApi.create(data)
      this.replenishments.unshift(replenishment)
      return replenishment
    },
    async submitReplenishment(id: number) {
      const updated = await replenishmentApi.submit(id)
      this.updateReplenishmentInStore(id, updated)
      return updated
    },
    async approveReplenishment(id: number, approved: boolean) {
      const updated = await replenishmentApi.approve(id, approved)
      this.updateReplenishmentInStore(id, updated)
      return updated
    },
    async receiveReplenishment(id: number) {
      const updated = await replenishmentApi.receive(id)
      this.updateReplenishmentInStore(id, updated)
      return updated
    },
    updateReplenishmentInStore(id: number, updated: Replenishment) {
      const index = this.replenishments.findIndex(r => r.id === id)
      if (index !== -1) {
        this.replenishments[index] = updated
      }
    },

    async fetchSettlements(params?: { status?: SettlementStatus; period?: string }) {
      this.loading = true
      try {
        this.settlements = await settlementApi.list(params)
      } finally {
        this.loading = false
      }
    },
    async createSettlement(data: SettlementCreate) {
      const settlement = await settlementApi.create(data)
      this.settlements.unshift(settlement)
      return settlement
    },
    async approveSettlement(id: number, approved: boolean) {
      const updated = await settlementApi.approve(id, approved)
      this.updateSettlementInStore(id, updated)
      return updated
    },
    async paySettlement(id: number) {
      const updated = await settlementApi.pay(id)
      this.updateSettlementInStore(id, updated)
      return updated
    },
    updateSettlementInStore(id: number, updated: Settlement) {
      const index = this.settlements.findIndex(s => s.id === id)
      if (index !== -1) {
        this.settlements[index] = updated
      }
    }
  }
})
