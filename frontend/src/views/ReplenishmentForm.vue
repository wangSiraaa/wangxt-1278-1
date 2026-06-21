<template>
  <div>
    <div class="page-header">
      <h1 class="page-title">新增补货单</h1>
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
              :disabled="!authStore.hasRole(['admin'])"
            />
          </div>
          <div class="text-right">
            <PButton label="添加备件" icon="pi pi-plus" @click="addItem" :disabled="!form.supplier_id" />
          </div>
        </div>
        <div>
          <label class="block mb-2 font-medium">备注</label>
          <Textarea v-model="form.remark" class="w-full" :rows="2" />
        </div>
      </div>
    </div>

    <div class="card">
      <h3 class="text-lg font-semibold mb-4">补货明细</h3>
      <PDataTable :value="form.items" :editable="true" emptyMessage="请添加备件">
        <Column field="spare_part_id" header="备件 *" :editable="true">
          <template #editor="{ data }">
            <PSelect
              v-model="data.spare_part_id"
              :options="partOptions"
              class="w-full"
              placeholder="选择备件"
              filter
            />
          </template>
          <template #body="{ data }">
            {{ getPartName(data.spare_part_id) }}
          </template>
        </Column>
        <Column field="batch_no" header="批次号 *" :editable="true">
          <template #editor="{ data }">
            <InputText v-model="data.batch_no" class="w-full" />
          </template>
        </Column>
        <Column field="quantity" header="数量 *" :editable="true">
          <template #editor="{ data }">
            <InputNumber v-model="data.quantity" class="w-full" :min="1" />
          </template>
        </Column>
        <Column field="unit_price" header="单价 *" :editable="true">
          <template #editor="{ data }">
            <InputNumber v-model="data.unit_price" class="w-full" :min="0" :min-fraction-digits="2" />
          </template>
        </Column>
        <Column header="金额">
          <template #body="{ data }">
            ¥{{ (data.quantity * data.unit_price).toFixed(2) }}
          </template>
        </Column>
        <Column field="production_date" header="生产日期" :editable="true">
          <template #editor="{ data }">
            <Calendar v-model="data.production_date" class="w-full" date-format="yy-mm-dd" />
          </template>
        </Column>
        <Column field="expiry_date" header="有效期至" :editable="true">
          <template #editor="{ data }">
            <Calendar v-model="data.expiry_date" class="w-full" date-format="yy-mm-dd" />
          </template>
        </Column>
        <Column field="location" header="存放位置" :editable="true">
          <template #editor="{ data }">
            <InputText v-model="data.location" class="w-full" />
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
      <PButton label="保存草稿" severity="secondary" @click="saveAsDraft" :loading="saving" />
      <PButton label="提交审批" @click="submitReplenishment" :loading="submitting" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useMasterDataStore, useTransactionStore, useAuthStore } from '@/stores'
import { useToast } from 'primevue/usetoast'
import type { ReplenishmentItemCreate } from '@/types'
import Column from 'primevue/column'
import InputText from 'primevue/inputtext'
import InputNumber from 'primevue/inputnumber'
import Textarea from 'primevue/textarea'
import Calendar from 'primevue/calendar'

const masterDataStore = useMasterDataStore()
const transactionStore = useTransactionStore()
const authStore = useAuthStore()
const router = useRouter()
const toast = useToast()

const saving = ref(false)
const submitting = ref(false)

interface ReplenishmentFormItem extends Omit<ReplenishmentItemCreate, 'production_date' | 'expiry_date'> {
  id?: number
  production_date?: Date | null
  expiry_date?: Date | null
  location?: string
  remark?: string
}

const form = reactive({
  supplier_id: (authStore.user?.supplier_id || null) as number | null,
  remark: '',
  items: [] as ReplenishmentFormItem[]
})

const supplierOptions = computed(() =>
  masterDataStore.suppliers
    .filter(s => s.is_active)
    .map(s => ({ label: s.name, value: s.id }))
)

const partOptions = computed(() =>
  masterDataStore.spareParts
    .filter(p => p.is_active)
    .map(p => ({ label: `${p.code} - ${p.name}`, value: p.id }))
)

const getPartName = (id: number) => {
  const part = masterDataStore.spareParts.find(p => p.id === id)
  return part ? `${part.code} - ${part.name}` : ''
}

const totalAmount = computed(() => {
  return form.items.reduce((sum, item) => sum + item.quantity * item.unit_price, 0)
})

const addItem = () => {
  form.items.push({
    spare_part_id: null as unknown as number,
    batch_no: '',
    quantity: 1,
    unit_price: 0,
    production_date: null as Date | null,
    expiry_date: null as Date | null,
    location: '',
    remark: ''
  })
}

const removeItem = (index: number) => {
  form.items.splice(index, 1)
}

const validateForm = () => {
  if (!form.supplier_id) {
    toast.add({ severity: 'warn', summary: '提示', detail: '请选择供应商' })
    return false
  }
  if (form.items.length === 0) {
    toast.add({ severity: 'warn', summary: '提示', detail: '请添加备件明细' })
    return false
  }
  for (let i = 0; i < form.items.length; i++) {
    const item = form.items[i]
    if (!item.spare_part_id || !item.batch_no || !item.quantity || !item.unit_price) {
      toast.add({ severity: 'warn', summary: '提示', detail: `第${i + 1}行信息不完整` })
      return false
    }
  }
  return true
}

const convertItemsToApiFormat = (items: ReplenishmentFormItem[]): ReplenishmentItemCreate[] => {
  return items.map(item => ({
    ...item,
    production_date: item.production_date ? item.production_date.toISOString().split('T')[0] : undefined,
    expiry_date: item.expiry_date ? item.expiry_date.toISOString().split('T')[0] : undefined
  }))
}

const saveAsDraft = async () => {
  if (!validateForm()) return
  saving.value = true
  try {
    const data = {
      supplier_id: form.supplier_id!,
      remark: form.remark,
      items: convertItemsToApiFormat(form.items)
    }
    await transactionStore.createReplenishment(data)
    toast.add({ severity: 'success', summary: '成功', detail: '补货单已保存为草稿' })
    router.push('/replenishments')
  } catch (e: any) {
    toast.add({ severity: 'error', summary: '错误', detail: e.response?.data?.detail || '保存失败' })
  } finally {
    saving.value = false
  }
}

const submitReplenishment = async () => {
  if (!validateForm()) return
  submitting.value = true
  try {
    const data = {
      supplier_id: form.supplier_id!,
      remark: form.remark,
      items: convertItemsToApiFormat(form.items)
    }
    const replenishment = await transactionStore.createReplenishment(data)
    await transactionStore.submitReplenishment(replenishment.id)
    toast.add({ severity: 'success', summary: '成功', detail: '补货单已提交审批' })
    router.push('/replenishments')
  } catch (e: any) {
    toast.add({ severity: 'error', summary: '错误', detail: e.response?.data?.detail || '提交失败' })
  } finally {
    submitting.value = false
  }
}

onMounted(async () => {
  await Promise.all([
    masterDataStore.fetchSuppliers(),
    masterDataStore.fetchSpareParts()
  ])
})
</script>
