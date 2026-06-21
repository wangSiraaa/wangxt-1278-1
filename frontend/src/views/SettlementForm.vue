<template>
  <div>
    <div class="page-header">
      <h1 class="page-title">新增结算单</h1>
      <PButton label="返回" icon="pi pi-arrow-left" severity="secondary" @click="router.back()" />
    </div>

    <div class="card">
      <div class="form-grid">
        <div class="form-row">
          <div>
            <label class="block mb-2 font-medium">供应商 *</label>
            <PSelect
              v-model="form.supplier_id"
              :options="supplierOptions"
              class="w-full"
              placeholder="选择供应商"
              @change="loadRequisitions()"
            />
          </div>
          <div>
            <label class="block mb-2 font-medium">期间 *</label>
            <InputText v-model="form.period" class="w-full" placeholder="如: 2024-01" />
          </div>
        </div>
        <div>
          <label class="block mb-2 font-medium">备注</label>
          <Textarea v-model="form.remark" class="w-full" :rows="2" />
        </div>
      </div>
    </div>

    <div class="card">
      <h3 class="text-lg font-semibold mb-4">选择领用单</h3>
      <PMessage v-if="!form.supplier_id" severity="info" content="请先选择供应商以显示可用领用单" />
      <PDataTable
        v-else
        :value="availableRequisitions"
        :loading="loadingRequisitions"
        :paginator="true"
        :rows="10"
        emptyMessage="没有可结算的领用单"
        selectionMode="multiple"
        v-model:selection="selectedRequisitions"
      >
        <Column selectionMode="multiple" :style="{ width: '3em' }" />
        <Column field="requisition_no" header="领用单号" />
        <Column field="maintenance_order.order_no" header="维修单号">
          <template #body="{ data }">
            {{ data.maintenance_order?.order_no }}
          </template>
        </Column>
        <Column field="total_amount" header="金额">
          <template #body="{ data }">
            ¥{{ data.total_amount.toFixed(2) }}
          </template>
        </Column>
        <Column field="delivered_at" header="出库时间">
          <template #body="{ data }">
            {{ data.delivered_at ? formatDate(data.delivered_at) : '-' }}
          </template>
        </Column>
      </PDataTable>

      <div class="mt-4 flex justify-end">
        <div class="text-lg font-semibold">
          已选 {{ selectedRequisitions.length }} 张领用单, 合计:
          <span class="amount-positive">¥{{ selectedTotal.toFixed(2) }}</span>
        </div>
      </div>
    </div>

    <div class="flex justify-end gap-3">
      <PButton label="取消" severity="secondary" @click="router.back()" />
      <PButton label="创建结算" @click="createSettlement" :loading="saving" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useMasterDataStore, useTransactionStore } from '@/stores'
import { useToast } from 'primevue/usetoast'
import type { Requisition } from '@/types'
import Column from 'primevue/column'
import InputText from 'primevue/inputtext'
import Textarea from 'primevue/textarea'

const masterDataStore = useMasterDataStore()
const transactionStore = useTransactionStore()
const router = useRouter()
const toast = useToast()

const saving = ref(false)
const loadingRequisitions = ref(false)
const availableRequisitions = ref<Requisition[]>([])
const selectedRequisitions = ref<Requisition[]>([])

const form = reactive({
  supplier_id: null as number | null,
  period: new Date().toISOString().slice(0, 7),
  remark: ''
})

const supplierOptions = computed(() =>
  masterDataStore.suppliers
    .filter(s => s.is_active)
    .map(s => ({ label: s.name, value: s.id }))
)

const selectedTotal = computed(() =>
  selectedRequisitions.value.reduce((sum, req) => sum + req.total_amount, 0)
)

const formatDate = (date: string) => new Date(date).toLocaleString('zh-CN')

const loadRequisitions = async () => {
  if (!form.supplier_id) return
  loadingRequisitions.value = true
  try {
    await transactionStore.fetchRequisitions({ is_settled: false })
    availableRequisitions.value = transactionStore.requisitions.filter(
      r => r.status === 'delivered' && !r.is_settled
    )
    selectedRequisitions.value = []
  } finally {
    loadingRequisitions.value = false
  }
}

const createSettlement = async () => {
  if (!form.supplier_id || !form.period) {
    toast.add({ severity: 'warn', summary: '提示', detail: '请填写供应商和期间' })
    return
  }
  if (selectedRequisitions.value.length === 0) {
    toast.add({ severity: 'warn', summary: '提示', detail: '请选择至少一张领用单' })
    return
  }
  saving.value = true
  try {
    const data = {
      supplier_id: form.supplier_id!,
      period: form.period,
      remark: form.remark,
      requisition_ids: selectedRequisitions.value.map(r => r.id)
    }
    await transactionStore.createSettlement(data)
    toast.add({ severity: 'success', summary: '成功', detail: '结算单已创建' })
    router.push('/settlements')
  } catch (e: any) {
    toast.add({ severity: 'error', summary: '错误', detail: e.response?.data?.detail || '创建失败' })
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  await masterDataStore.fetchSuppliers()
})
</script>
