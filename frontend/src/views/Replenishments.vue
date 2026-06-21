<template>
  <div>
    <div class="page-header">
      <h1 class="page-title">补货管理</h1>
      <PButton
        v-if="canCreate"
        label="新增补货"
        icon="pi pi-plus"
        @click="router.push('/replenishments/new')"
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
        :value="store.replenishments"
        :loading="store.loading"
        :paginator="true"
        :rows="10"
        emptyMessage="暂无补货数据"
      >
        <Column field="replenishment_no" header="补货单号" :sortable="true" />
        <Column field="supplier.name" header="供应商">
          <template #body="{ data }">
            {{ data.supplier?.name }}
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
        <Column field="creator.full_name" header="创建人">
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
            <template v-if="data.status === 'draft' && canEdit(data.supplier_id)">
              <PButton
                icon="pi pi-send"
                size="small"
                severity="info"
                class="mr-2"
                @click="submitReplenishment(data.id)"
              />
            </template>
            <template v-if="data.status === 'pending' && canApprove">
              <PButton
                icon="pi pi-check"
                size="small"
                severity="success"
                class="mr-2"
                @click="approveReplenishment(data.id, true)"
              />
              <PButton
                icon="pi pi-times"
                size="small"
                severity="danger"
                class="mr-2"
                @click="approveReplenishment(data.id, false)"
              />
            </template>
            <template v-if="data.status === 'in_transit' && canApprove">
              <PButton
                icon="pi pi-download"
                size="small"
                severity="success"
                @click="receiveReplenishment(data.id)"
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
import type { ReplenishmentStatus } from '@/types'
import Column from 'primevue/column'

const store = useTransactionStore()
const authStore = useAuthStore()
const router = useRouter()
const toast = useToast()

const filterStatus = ref<ReplenishmentStatus | null>(null)

const statusOptions = [
  { label: '草稿', value: 'draft' },
  { label: '待审批', value: 'pending' },
  { label: '运输中', value: 'in_transit' },
  { label: '已入库', value: 'received' },
  { label: '已拒绝', value: 'rejected' }
]

const canCreate = computed(() => authStore.hasRole(['admin', 'supplier']))
const canApprove = computed(() => authStore.hasRole(['admin', 'equipment_engineer']))
const canEdit = (supplierId: number) => {
  if (authStore.hasRole(['admin'])) return true
  if (authStore.user?.role === 'supplier' && authStore.user.supplier_id === supplierId) return true
  return false
}

const getStatusText = (status: ReplenishmentStatus) => {
  const map: Record<ReplenishmentStatus, string> = {
    draft: '草稿',
    pending: '待审批',
    in_transit: '运输中',
    received: '已入库',
    rejected: '已拒绝'
  }
  return map[status] || status
}

const getStatusSeverity = (status: ReplenishmentStatus) => {
  const map: Record<ReplenishmentStatus, any> = {
    draft: 'secondary',
    pending: 'warning',
    in_transit: 'info',
    received: 'success',
    rejected: 'danger'
  }
  return map[status] || 'secondary'
}

const formatDate = (date: string) => new Date(date).toLocaleString('zh-CN')

const loadData = () => {
  store.fetchReplenishments({ status: filterStatus.value || undefined })
}

const submitReplenishment = async (id: number) => {
  try {
    await store.submitReplenishment(id)
    toast.add({ severity: 'success', summary: '成功', detail: '补货单已提交审批' })
    loadData()
  } catch (e: any) {
    toast.add({ severity: 'error', summary: '错误', detail: e.response?.data?.detail || '操作失败' })
  }
}

const approveReplenishment = async (id: number, approved: boolean) => {
  try {
    await store.approveReplenishment(id, approved)
    toast.add({ severity: 'success', summary: '成功', detail: approved ? '审批通过' : '已拒绝' })
    loadData()
  } catch (e: any) {
    toast.add({ severity: 'error', summary: '错误', detail: e.response?.data?.detail || '操作失败' })
  }
}

const receiveReplenishment = async (id: number) => {
  try {
    await store.receiveReplenishment(id)
    toast.add({ severity: 'success', summary: '成功', detail: '已确认入库' })
    loadData()
  } catch (e: any) {
    toast.add({ severity: 'error', summary: '错误', detail: e.response?.data?.detail || '操作失败' })
  }
}

onMounted(loadData)
</script>
