<template>
  <div>
    <div class="page-header">
      <h1 class="page-title">库存归属确认</h1>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
      <div class="stat-card">
        <div class="stat-icon info">
          <i class="pi pi-box"></i>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ totalBatches }}</div>
          <div class="stat-label">总批次数</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon success">
          <i class="pi pi-check-circle"></i>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ fullyConfirmed }}</div>
          <div class="stat-label">已完全确认</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon warning">
          <i class="pi pi-clock"></i>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ pendingCount }}</div>
          <div class="stat-label">待我确认</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon danger">
          <i class="pi pi-times-circle"></i>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ rejectedCount }}</div>
          <div class="stat-label">已拒绝</div>
        </div>
      </div>
    </div>

    <div class="card">
      <PDataTable
        :value="store.batches"
        :loading="store.loading"
        :paginator="true"
        :rows="10"
        emptyMessage="暂无批次数据"
        responsiveLayout="scroll"
      >
        <Column field="batch_no" header="批次号" :sortable="true" />
        <Column field="spare_part.name" header="备件名称">
          <template #body="{ data }">
            {{ data.spare_part?.name }}
          </template>
        </Column>
        <Column field="supplier.name" header="供应商">
          <template #body="{ data }">
            {{ data.supplier?.name }}
          </template>
        </Column>
        <Column field="quantity" header="数量" />
        <Column field="unit_price" header="单价">
          <template #body="{ data }">
            ¥{{ data.unit_price.toFixed(2) }}
          </template>
        </Column>
        <Column header="设备部门">
          <template #body="{ data }">
            <PBadge
              :value="data.ownership_status?.equipment_confirmed ? '已确认' : '待确认'"
              :severity="data.ownership_status?.equipment_confirmed ? 'success' : 'warning'"
            />
          </template>
        </Column>
        <Column header="供应商">
          <template #body="{ data }">
            <PBadge
              :value="data.ownership_status?.supplier_confirmed ? '已确认' : '待确认'"
              :severity="data.ownership_status?.supplier_confirmed ? 'success' : 'warning'"
            />
          </template>
        </Column>
        <Column header="财务">
          <template #body="{ data }">
            <PBadge
              :value="data.ownership_status?.finance_confirmed ? '已确认' : '待确认'"
              :severity="data.ownership_status?.finance_confirmed ? 'success' : 'warning'"
            />
          </template>
        </Column>
        <Column header="状态">
          <template #body="{ data }">
            <PBadge
              :value="data.ownership_status?.is_fully_confirmed ? '全部确认' : '待确认'"
              :severity="data.ownership_status?.is_fully_confirmed ? 'success' : 'warning'"
            />
          </template>
        </Column>
        <Column header="操作" v-if="myRole">
          <template #body="{ data }">
            <template v-if="!hasMyConfirmation(data.id)">
              <PButton
                icon="pi pi-check"
                size="small"
                severity="success"
                @click="confirmOwnership(data.id)"
                v-tooltip.top="'确认归属'"
              />
            </template>
            <template v-else>
              <span class="text-green-600 font-medium">已确认</span>
            </template>
          </template>
        </Column>
      </PDataTable>
    </div>

    <PDialog v-model:visible="confirmDialogVisible" header="确认库存归属" :modal="true" class="dialog-form">
      <div class="dialog-content">
        <p class="mb-4">请确认库存归属信息：</p>
        <div class="form-grid">
          <div>
            <label class="block mb-2 font-medium">确认状态</label>
            <PSelect v-model="confirmForm.status" class="w-full" :options="statusOptions" />
          </div>
          <div>
            <label class="block mb-2 font-medium">备注</label>
            <Textarea v-model="confirmForm.comment" class="w-full" :rows="2" />
          </div>
        </div>
      </div>
      <template #footer>
        <div class="dialog-footer">
          <PButton label="取消" severity="secondary" @click="confirmDialogVisible = false" />
          <PButton label="确认" @click="submitConfirmation" :loading="saving" />
        </div>
      </template>
    </PDialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useMasterDataStore, useAuthStore } from '@/stores'
import { useToast } from 'primevue/usetoast'
import type { ConfirmationStatus } from '@/types'
import Column from 'primevue/column'
import Textarea from 'primevue/textarea'

const store = useMasterDataStore()
const authStore = useAuthStore()
const toast = useToast()

const confirmDialogVisible = ref(false)
const saving = ref(false)
const selectedBatchId = ref<number | null>(null)

const confirmForm = reactive({
  status: 'confirmed' as ConfirmationStatus,
  comment: ''
})

const statusOptions = [
  { label: '确认', value: 'confirmed' },
  { label: '拒绝', value: 'rejected' }
]

const myRole = computed(() => {
  const role = authStore.user?.role
  if (role === 'admin') return 'equipment'
  const map: Record<string, string> = {
    equipment_engineer: 'equipment',
    supplier: 'supplier',
    finance: 'finance'
  }
  return map[role || ''] || null
})

const totalBatches = computed(() => store.batches.length)
const fullyConfirmed = computed(() =>
  store.batches.filter(b => b.ownership_status?.is_fully_confirmed).length
)
const pendingCount = computed(() => {
  const role = myRole.value
  if (!role) return 0
  return store.batches.filter(b => !b.ownership_status?.[role + '_confirmed' as keyof typeof b.ownership_status]).length
})
const rejectedCount = computed(() =>
  store.ownershipConfirmations.filter(c => c.status === 'rejected').length
)

const hasMyConfirmation = (batchId: number) => {
  if (!authStore.user) return false
  return store.ownershipConfirmations.some(
    c => c.batch_id === batchId && c.confirmer_id === authStore.user!.id
  )
}

const confirmOwnership = async (batchId: number) => {
  selectedBatchId.value = batchId
  confirmForm.status = 'confirmed'
  confirmForm.comment = ''
  confirmDialogVisible.value = true
}

const submitConfirmation = async () => {
  if (!selectedBatchId.value) return
  saving.value = true
  try {
    let confirmation = store.ownershipConfirmations.find(
      c => c.batch_id === selectedBatchId.value && c.confirmer_id === authStore.user!.id
    )
    if (!confirmation) {
      await store.confirmBatchOwnership(selectedBatchId.value)
      confirmation = store.ownershipConfirmations.find(
        c => c.batch_id === selectedBatchId.value && c.confirmer_id === authStore.user!.id
      )
    }
    if (confirmation) {
      await store.updateConfirmation(confirmation.id, {
        status: confirmForm.status,
        comment: confirmForm.comment
      })
    }
    toast.add({ severity: 'success', summary: '成功', detail: '归属确认已提交' })
    confirmDialogVisible.value = false
    loadData()
  } catch (e: any) {
    toast.add({ severity: 'error', summary: '错误', detail: e.response?.data?.detail || '操作失败' })
  } finally {
    saving.value = false
  }
}

const loadData = async () => {
  await Promise.all([
    store.fetchBatches(),
    store.fetchOwnershipConfirmations()
  ])
}

onMounted(loadData)
</script>
