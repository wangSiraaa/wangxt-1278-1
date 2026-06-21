import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { DashboardStats, SafetyStockAlert, MonthlyClosing } from '@/types'
import { systemApi } from '@/api'

export const useSystemStore = defineStore('system', {
  state: () => ({
    dashboardStats: ref<DashboardStats | null>(null),
    safetyAlerts: ref<SafetyStockAlert[]>([]),
    monthlyClosings: ref<MonthlyClosing[]>([]),
    loading: ref(false)
  }),
  actions: {
    async fetchDashboardStats() {
      this.loading = true
      try {
        this.dashboardStats = await systemApi.getDashboardStats()
      } finally {
        this.loading = false
      }
    },
    async fetchSafetyAlerts(isProcessed?: boolean) {
      this.loading = true
      try {
        this.safetyAlerts = await systemApi.listSafetyStockAlerts({ is_processed: isProcessed })
      } finally {
        this.loading = false
      }
    },
    async fetchMonthlyClosings() {
      this.loading = true
      try {
        this.monthlyClosings = await systemApi.listMonthlyClosings()
      } finally {
        this.loading = false
      }
    },
    async createMonthlyClosing(period: string, remark?: string) {
      return await systemApi.createMonthlyClosing({ period, remark })
    },
    async reopenMonthlyClosing(period: string) {
      return await systemApi.reopenMonthlyClosing(period)
    },
    async processAlert(alertId: number) {
      return await systemApi.processAlert(alertId)
    }
  }
})
