<template>
  <div>
    <div class="page-header">
      <h1 class="page-title">结算管理</h1>
      <PButton
        v-if="canCreate"
        label="新增结算"
        icon="pi pi-plus"
        @click="router.push('/settlements/new')"
      />
    </div>

    <div class="card">
      <div class="table-toolbar">
        <div class="toolbar-left">
          <PSelect
            v-model="filterStatus"
            :options="statusOptions"
            placeholder="全部状态"
            class="w-40"
            @change="loadData()"
          />
          <InputText
            v-model="filterPeriod"
            placeholder="按期间筛选 (如 2024-01)"
            class="w-48"
            @keyup.enter="loadData()"
          />
        </div>
      </div>

      <PDataTable
        :value="store.settlements"
        :loading="store.loading"
        :paginator="true"
        :rows="10"
        emptyMessage="暂无结算数据"
      >
        <Column field="settlement_no" header="结算单号" :sortable="true" />
        <Column field="period" header="期间" />
        <Column field="supplier.name" header="供应商">
          <template #body="{ data }">
            {{ data.supplier?.name }}
          </template>
        </Column>
        <Column field="total_amount" header="结算金额">
          <template #body="{ data }">
            ¥{{ data.total_amount.toFixed(2) }}
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
        <Column header="操作">
          <template #body="{ data }">
            <template v-if="data.status === 'pending' && canApprove">
              <PButton
                icon="pi pi-check"
                size="small"
                severity="success"
                class="mr-2"
                @click="approveSettlement(data.id, true)"
                v-tooltip.top="'审批通过'"
              />
              <PButton
                icon="pi pi-times"
                size="small"
                severity="danger"
                class="mr-2"
                @click="approveSettlement(data.id, false)"
                v-tooltip.top="'驳回'"
              />
            </template>
            <template v-if="data.status === 'approved' && canPay">
              <PButton
                icon="pi pi-money-bill"
                size="small"
                severity="success"
                @click="paySettlement(data.id)"
                v-tooltip.top="'确认付款'"
              />
            </template>
          </template>
        </Column>
      </PDataTable>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useTransactionStore, useAuthStore } from '@/stores'
import { useToast } from 'primevue/usetoast'
import type { SettlementStatus } from '@/types'
import Column from 'primevue/column'
import InputText from 'primevue/inputtext'

const store = useTransactionStore()
const authStore = useAuthStore()
const router = useRouter()
const toast = useToast()

const filterStatus = ref<SettlementStatus | null>(null)
const filterPeriod = ref('')

const statusOptions = [
  { label: '待审批', value: 'pending' },
  { label: '已审批', value: 'approved' },
  { label: '已付款', value: 'paid' },
  { label: '已拒绝', value: 'rejected' }
]

const canCreate = computed(() => authStore.hasRole(['admin', 'finance']))
const canApprove = computed(() => authStore.hasRole(['admin']))
const canPay = computed(() => authStore.hasRole(['admin', 'finance']))

const getStatusText = (status: SettlementStatus) => {
  const map: Record<SettlementStatus, string> = {
    pending: '待审批',
    approved: '已审批',
    paid: '已付款',
    rejected: '已拒绝'
  }
  return map[status] || status
}

const getStatusSeverity = (status: SettlementStatus) => {
  const map: Record<SettlementStatus, any> = {
    pending: 'warning',
    approved: 'info',
    paid: 'success',
    rejected: 'danger'
  }
  return map[status] || 'secondary'
}

const formatDate = (date: string) => new Date(date).toLocaleString('zh-CN')

const loadData = () => {
  store.fetchSettlements({
    status: filterStatus.value || undefined,
    period: filterPeriod.value || undefined
  })
}

const approveSettlement = async (id: number, approved: boolean) => {
  try {
    await store.approveSettlement(id, approved)
    toast.add({ severity: 'success', summary: '成功', detail: approved ? '审批通过' : '已驳回' })
    loadData()
  } catch (e: any) {
    toast.add({ severity: 'error', summary: '错误', detail: e.response?.data?.detail || '操作失败' })
  }
}

const paySettlement = async (id: number) => {
  try {
    await store.paySettlement(id)
    toast.add({ severity: 'success', summary: '成功', detail: '已确认付款' })
    loadData()
  } catch (e: any) {
    toast.add({ severity: 'error', summary: '错误', detail: e.response?.data?.detail || '操作失败' })
  }
}

onMounted(loadData)
</script>
