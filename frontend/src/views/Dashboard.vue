<template>
  <div>
    <div class="page-header">
      <h1 class="page-title">仪表盘</h1>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      <div class="stat-card">
        <div class="stat-icon primary">
          <i class="pi pi-box"></i>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stats?.total_spare_parts || 0 }}</div>
          <div class="stat-label">备件总数</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon info">
          <i class="pi pi-tags"></i>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stats?.total_batches || 0 }}</div>
          <div class="stat-label">库存批次</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon warning">
          <i class="pi pi-shopping-cart"></i>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stats?.pending_requisitions || 0 }}</div>
          <div class="stat-label">待处理领用</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon success">
          <i class="pi pi-refresh"></i>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stats?.pending_replenishments || 0 }}</div>
          <div class="stat-label">待处理补货</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon info">
          <i class="pi pi-money-bill"></i>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stats?.pending_settlements || 0 }}</div>
          <div class="stat-label">待处理结算</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon danger">
          <i class="pi pi-exclamation-triangle"></i>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stats?.low_stock_alerts || 0 }}</div>
          <div class="stat-label">安全库存预警</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon warning">
          <i class="pi pi-check-circle"></i>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stats?.pending_ownership_confirmations || 0 }}</div>
          <div class="stat-label">待归属确认</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon success">
          <i class="pi pi-dollar"></i>
        </div>
        <div class="stat-content">
          <div class="stat-value amount-positive">¥{{ formatNumber(stats?.total_stock_value || 0) }}</div>
          <div class="stat-label">库存总价值</div>
        </div>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div class="card">
        <h3 class="text-lg font-semibold mb-4">安全库存预警</h3>
        <PDataTable
          :value="lowStockAlerts"
          :loading="loading"
          :paginator="true"
          :rows="5"
          emptyMessage="暂无预警信息"
        >
          <Column field="spare_part.code" header="备件编码">
            <template #body="{ data }">
              {{ data.spare_part?.code }}
            </template>
          </Column>
          <Column field="spare_part.name" header="备件名称">
            <template #body="{ data }">
              {{ data.spare_part?.name }}
            </template>
          </Column>
          <Column field="current_stock" header="当前库存" :sortable="true" />
          <Column field="safety_stock" header="安全库存" />
          <Column field="shortage" header="短缺数量">
            <template #body="{ data }">
              <span class="stock-low">{{ data.shortage }}</span>
            </template>
          </Column>
          <Column header="状态">
            <template #body="{ data }">
              <PBadge
                :value="data.is_processed ? '已处理' : '待处理'"
                :severity="data.is_processed ? 'success' : 'warning'"
              />
            </template>
          </Column>
        </PDataTable>
      </div>

      <div class="card">
        <h3 class="text-lg font-semibold mb-4">最近领用记录</h3>
        <PDataTable
          :value="recentRequisitions"
          :loading="loading"
          :paginator="true"
          :rows="5"
          emptyMessage="暂无领用记录"
        >
          <Column field="requisition_no" header="领用单号" />
          <Column field="maintenance_order.order_no" header="维修单号">
            <template #body="{ data }">
              {{ data.maintenance_order?.order_no }}
            </template>
          </Column>
          <Column field="total_amount" header="金额">
            <template #body="{ data }">
              ¥{{ formatNumber(data.total_amount) }}
            </template>
          </Column>
          <Column field="status" header="状态">
            <template #body="{ data }">
              <PBadge :value="getStatusText(data.status)" :severity="getStatusSeverity(data.status)" />
            </template>
          </Column>
          <Column field="created_at" header="创建时间">
            <template #body="{ data }">
              {{ formatDate(data.created_at) }}
            </template>
          </Column>
        </PDataTable>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useSystemStore, useTransactionStore } from '@/stores'
import type { RequisitionStatus } from '@/types'
import Column from 'primevue/column'

const systemStore = useSystemStore()
const transactionStore = useTransactionStore()

const loading = ref(false)

const stats = computed(() => systemStore.dashboardStats)
const lowStockAlerts = computed(() => systemStore.safetyAlerts.filter(a => !a.is_processed).slice(0, 10))
const recentRequisitions = computed(() => transactionStore.requisitions.slice(0, 10))

const formatNumber = (num: number) => {
  return num.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

const formatDate = (date: string) => {
  return new Date(date).toLocaleString('zh-CN')
}

const getStatusText = (status: RequisitionStatus) => {
  const map: Record<RequisitionStatus, string> = {
    draft: '草稿',
    pending: '待审批',
    approved: '已审批',
    rejected: '已拒绝',
    delivered: '已出库',
    settled: '已结算'
  }
  return map[status] || status
}

const getStatusSeverity = (status: RequisitionStatus) => {
  const map: Record<RequisitionStatus, any> = {
    draft: 'secondary',
    pending: 'warning',
    approved: 'info',
    rejected: 'danger',
    delivered: 'success',
    settled: 'success'
  }
  return map[status] || 'secondary'
}

const loadData = async () => {
  loading.value = true
  try {
    await Promise.all([
      systemStore.fetchDashboardStats(),
      systemStore.fetchSafetyAlerts(false),
      transactionStore.fetchRequisitions()
    ])
  } finally {
    loading.value = false
  }
}

onMounted(loadData)
</script>
