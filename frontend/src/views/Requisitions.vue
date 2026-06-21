<template>
  <div>
    <div class="page-header">
      <h1 class="page-title">领用管理</h1>
      <PButton
        label="新增领用"
        icon="pi pi-plus"
        @click="router.push('/requisitions/new')"
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
        </div>
      </div>

      <PDataTable
        :value="store.requisitions"
        :loading="store.loading"
        :paginator="true"
        :rows="10"
        emptyMessage="暂无领用数据"
      >
        <Column field="requisition_no" header="领用单号" :sortable="true" />
        <Column field="maintenance_order.order_no" header="维修单号">
          <template #body="{ data }">
            {{ data.maintenance_order?.order_no }}
          </template>
        </Column>
        <Column field="total_amount" header="总金额">
          <template #body="{ data }">
            ¥{{ data.total_amount.toFixed(2) }}
          </template>
        </Column>
        <Column field="status" header="状态">
          <template #body="{ data }">
            <PBadge :value="getStatusText(data.status)" :severity="getStatusSeverity(data.status)" />
          </template>
        </Column>
        <Column field="creator.full_name" header="申请人">
          <template #body="{ data }">
            {{ data.creator?.full_name }}
          </template>
        </Column>
        <Column field="created_at" header="创建时间">
          <template #body="{ data }">
            {{ formatDate(data.created_at) }}
          </template>
        </Column>
        <Column header="操作">
          <template #body="{ data }">
            <template v-if="data.status === 'draft' || data.status === 'rejected'">
              <PButton
                icon="pi pi-send"
                size="small"
                severity="info"
                class="mr-2"
                @click="submitRequisition(data.id)"
                v-tooltip.top="'提交审批'"
              />
            </template>
            <template v-if="data.status === 'pending' && canApprove">
              <PButton
                icon="pi pi-check"
                size="small"
                severity="success"
                class="mr-2"
                @click="approveRequisition(data.id, true)"
                v-tooltip.top="'审批通过'"
              />
              <PButton
                icon="pi pi-times"
                size="small"
                severity="danger"
                class="mr-2"
                @click="approveRequisition(data.id, false)"
                v-tooltip.top="'驳回'"
              />
            </template>
            <template v-if="data.status === 'approved' && canApprove">
              <PButton
                icon="pi pi-truck"
                size="small"
                severity="success"
                @click="deliverRequisition(data.id)"
                v-tooltip.top="'确认出库'"
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
import type { RequisitionStatus } from '@/types'
import Column from 'primevue/column'

const store = useTransactionStore()
const authStore = useAuthStore()
const router = useRouter()
const toast = useToast()

const filterStatus = ref<RequisitionStatus | null>(null)

const statusOptions = [
  { label: '草稿', value: 'draft' },
  { label: '待审批', value: 'pending' },
  { label: '已审批', value: 'approved' },
  { label: '已拒绝', value: 'rejected' },
  { label: '已出库', value: 'delivered' },
  { label: '已结算', value: 'settled' }
]

const canApprove = computed(() => authStore.hasRole(['admin', 'equipment_engineer']))

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

const formatDate = (date: string) => new Date(date).toLocaleString('zh-CN')

const loadData = () => {
  store.fetchRequisitions({ status: filterStatus.value || undefined })
}

const submitRequisition = async (id: number) => {
  try {
    await store.submitRequisition(id)
    toast.add({ severity: 'success', summary: '成功', detail: '领用单已提交审批' })
    loadData()
  } catch (e: any) {
    toast.add({ severity: 'error', summary: '错误', detail: e.response?.data?.detail || '操作失败' })
  }
}

const approveRequisition = async (id: number, approved: boolean) => {
  try {
    await store.approveRequisition(id, approved)
    toast.add({ severity: 'success', summary: '成功', detail: approved ? '审批通过' : '已驳回' })
    loadData()
  } catch (e: any) {
    toast.add({ severity: 'error', summary: '错误', detail: e.response?.data?.detail || '操作失败' })
  }
}

const deliverRequisition = async (id: number) => {
  try {
    await store.deliverRequisition(id)
    toast.add({ severity: 'success', summary: '成功', detail: '已确认出库' })
    loadData()
  } catch (e: any) {
    toast.add({ severity: 'error', summary: '错误', detail: e.response?.data?.detail || '操作失败' })
  }
}

onMounted(loadData)
</script>
