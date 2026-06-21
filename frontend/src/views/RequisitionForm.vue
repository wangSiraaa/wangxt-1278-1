<template>
  <div>
    <div class="page-header">
      <h1 class="page-title">新增领用单</h1>
      <PButton label="返回" icon="pi pi-arrow-left" severity="secondary" @click="router.back()" />
    </div>

    <div class="card">
      <div class="form-grid">
        <div class="form-row">
          <div>
            <label class="block mb-2 font-medium">维修单 *</label>
            <PSelect
              v-model="form.maintenance_order_id"
              :options="orderOptions"
              class="w-full"
              placeholder="选择维修单"
              filter
            />
          </div>
          <div class="text-right">
            <PButton
              label="添加备件"
              icon="pi pi-plus"
              @click="addItem"
              :disabled="!form.maintenance_order_id"
            />
          </div>
        </div>
        <div>
          <label class="block mb-2 font-medium">备注</label>
          <Textarea v-model="form.remark" class="w-full" :rows="2" />
        </div>
      </div>
    </div>

    <div class="card">
      <h3 class="text-lg font-semibold mb-4">领用明细</h3>
      <PDataTable :value="form.items" :editable="true" emptyMessage="请添加备件">
        <Column field="spare_part_id" header="备件 *" :editable="true">
          <template #editor="{ data }">
            <PSelect
              v-model="data.spare_part_id"
              :options="partOptions"
              class="w-full"
              placeholder="选择备件"
              @change="onPartChange(data)"
            />
          </template>
          <template #body="{ data }">
            {{ getPartName(data.spare_part_id) }}
          </template>
        </Column>
        <Column field="batch_id" header="批次 *" :editable="true">
          <template #editor="{ data }">
            <PSelect
              v-model="data.batch_id"
              :options="getBatchOptions(data.spare_part_id)"
              class="w-full"
              placeholder="选择批次"
              filter
            />
          </template>
          <template #body="{ data }">
            {{ getBatchNo(data.batch_id) }}
            <span class="text-xs text-gray-500 ml-2">
              (可用: {{ getBatchAvailable(data.batch_id) }})
            </span>
          </template>
        </Column>
        <Column field="quantity" header="数量 *" :editable="true">
          <template #editor="{ data }">
            <InputNumber v-model="data.quantity" class="w-full" :min="1" />
          </template>
          <template #body="{ data }">
            {{ data.quantity }}
          </template>
        </Column>
        <Column header="单价">
          <template #body="{ data }">
            ¥{{ getBatchPrice(data.batch_id)?.toFixed(2) || '0.00' }}
          </template>
        </Column>
        <Column header="金额">
          <template #body="{ data }">
            ¥{{ (data.quantity * (getBatchPrice(data.batch_id) || 0)).toFixed(2) }}
          </template>
        </Column>
        <Column header="操作">
          <template #body="{ index }">
            <PButton
              icon="pi pi-trash"
              size="small"
              severity="danger"
              @click="removeItem(index)"
            />
          </template>
        </Column>
      </PDataTable>

      <div class="mt-4 flex justify-end">
        <div class="text-lg font-semibold">
          总计: <span class="amount-positive">¥{{ totalAmount.toFixed(2) }}</span>
        </div>
      </div>
    </div>

    <div class="flex justify-end gap-3">
      <PButton label="取消" severity="secondary" @click="router.back()" />
      <PButton
        label="保存草稿"
        severity="secondary"
        @click="saveAsDraft"
        :loading="saving"
      />
      <PButton label="提交审批" @click="submitRequisition" :loading="submitting" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useMasterDataStore, useTransactionStore } from '@/stores'
import { useToast } from 'primevue/usetoast'
import type { RequisitionItemCreate } from '@/types'
import Column from 'primevue/column'
import InputNumber from 'primevue/inputnumber'
import Textarea from 'primevue/textarea'

const masterDataStore = useMasterDataStore()
const transactionStore = useTransactionStore()
const router = useRouter()
const toast = useToast()

const saving = ref(false)
const submitting = ref(false)

interface RequisitionFormItem extends RequisitionItemCreate {
  id?: number
  remark?: string
}

const form = reactive({
  maintenance_order_id: null as number | null,
  remark: '',
  items: [] as RequisitionFormItem[]
})

const orderOptions = computed(() =>
  masterDataStore.maintenanceOrders
    .filter(o => !o.is_closed)
    .map(o => ({ label: `${o.order_no} - ${o.equipment_name}`, value: o.id }))
)

const partOptions = computed(() =>
  masterDataStore.spareParts
    .filter(p => p.is_active)
    .map(p => ({ label: `${p.code} - ${p.name}`, value: p.id }))
)

const getBatchOptions = (sparePartId: number | null) => {
  if (!sparePartId) return []
  return masterDataStore.batches
    .filter(b => b.spare_part_id === sparePartId && b.available_quantity > 0 && b.ownership_status?.is_fully_confirmed)
    .map(b => ({
      label: `${b.batch_no} (可用: ${b.available_quantity}, ¥${b.unit_price})`,
      value: b.id
    }))
}

const getPartName = (id: number) => {
  const part = masterDataStore.spareParts.find(p => p.id === id)
  return part ? `${part.code} - ${part.name}` : ''
}

const getBatchNo = (id: number) => {
  const batch = masterDataStore.batches.find(b => b.id === id)
  return batch?.batch_no || ''
}

const getBatchAvailable = (id: number) => {
  const batch = masterDataStore.batches.find(b => b.id === id)
  return batch?.available_quantity || 0
}

const getBatchPrice = (id: number) => {
  const batch = masterDataStore.batches.find(b => b.id === id)
  return batch?.unit_price || 0
}

const totalAmount = computed(() => {
  return form.items.reduce((sum, item) => {
    return sum + item.quantity * getBatchPrice(item.batch_id)
  }, 0)
})

const addItem = () => {
  form.items.push({
    spare_part_id: null as unknown as number,
    batch_id: null as unknown as number,
    quantity: 1,
    remark: ''
  })
}

const removeItem = (index: number) => {
  form.items.splice(index, 1)
}

const onPartChange = (data: any) => {
  data.batch_id = null
}

const validateForm = () => {
  if (!form.maintenance_order_id) {
    toast.add({ severity: 'warn', summary: '提示', detail: '请选择维修单' })
    return false
  }
  if (form.items.length === 0) {
    toast.add({ severity: 'warn', summary: '提示', detail: '请添加备件明细' })
    return false
  }
  for (let i = 0; i < form.items.length; i++) {
    const item = form.items[i]
    if (!item.spare_part_id || !item.batch_id || !item.quantity) {
      toast.add({ severity: 'warn', summary: '提示', detail: `第${i + 1}行信息不完整` })
      return false
    }
    const available = getBatchAvailable(item.batch_id)
    if (item.quantity > available) {
      toast.add({ severity: 'warn', summary: '提示', detail: `第${i + 1}行数量超过可用库存` })
      return false
    }
  }
  return true
}

const saveAsDraft = async () => {
  if (!validateForm()) return
  saving.value = true
  try {
    const data = {
      maintenance_order_id: form.maintenance_order_id!,
      remark: form.remark,
      items: form.items
    }
    await transactionStore.createRequisition(data)
    toast.add({ severity: 'success', summary: '成功', detail: '领用单已保存为草稿' })
    router.push('/requisitions')
  } catch (e: any) {
    toast.add({ severity: 'error', summary: '错误', detail: e.response?.data?.detail || '保存失败' })
  } finally {
    saving.value = false
  }
}

const submitRequisition = async () => {
  if (!validateForm()) return
  submitting.value = true
  try {
    const data = {
      maintenance_order_id: form.maintenance_order_id!,
      remark: form.remark,
      items: form.items
    }
    const requisition = await transactionStore.createRequisition(data)
    await transactionStore.submitRequisition(requisition.id)
    toast.add({ severity: 'success', summary: '成功', detail: '领用单已提交审批' })
    router.push('/requisitions')
  } catch (e: any) {
    toast.add({ severity: 'error', summary: '错误', detail: e.response?.data?.detail || '提交失败' })
  } finally {
    submitting.value = false
  }
}

onMounted(async () => {
  await Promise.all([
    masterDataStore.fetchMaintenanceOrders(),
    masterDataStore.fetchSpareParts(),
    masterDataStore.fetchBatches({ available_only: true })
  ])
})
</script>
