<template>
  <div>
    <div class="page-header">
      <h1 class="page-title">批次库存</h1>
      <PButton
        v-if="canCreate"
        label="新增批次"
        icon="pi pi-plus"
        @click="openDialog()"
      />
    </div>

    <div class="card">
      <div class="table-toolbar">
        <div class="toolbar-left">
          <PSelect
            v-model="filterSupplier"
            :options="supplierOptions"
            placeholder="全部供应商"
            class="w-48"
            @change="loadBatches()"
          />
          <PSelect
            v-model="filterPart"
            :options="partOptions"
            placeholder="选择备件"
            class="w-48"
            @change="loadBatches()"
          />
          <PInputSwitch
            v-model="availableOnly"
            label="显示有库存"
          />
        </div>
      </div>

      <PDataTable
        :value="store.batches"
        :loading="store.loading"
        :paginator="true"
        :rows="10"
        emptyMessage="暂无批次数据"
      >
        <Column field="batch_no" header="批次号" :sortable="true" />
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
        <Column field="supplier.name" header="供应商">
          <template #body="{ data }">
            {{ data.supplier?.name }}
          </template>
        </Column>
        <Column field="quantity" header="总数量" />
        <Column field="available_quantity" header="可用数量">
          <template #body="{ data }">
            <span :class="data.available_quantity === 0 ? 'stock-low' : ''">
              {{ data.available_quantity }}
            </span>
          </template>
        </Column>
        <Column field="unit_price" header="单价">
          <template #body="{ data }">
            ¥{{ data.unit_price.toFixed(2) }}
          </template>
        </Column>
        <Column header="归属状态">
          <template #body="{ data }">
            <div class="ownership-indicator">
              <span
                class="ownership-dot"
                :class="data.ownership_status?.equipment_confirmed ? 'confirmed' : 'pending'"
                title="设备部门"
              ></span>
              <span
                class="ownership-dot"
                :class="data.ownership_status?.supplier_confirmed ? 'confirmed' : 'pending'"
                title="供应商"
              ></span>
              <span
                class="ownership-dot"
                :class="data.ownership_status?.finance_confirmed ? 'confirmed' : 'pending'"
                title="财务"
              ></span>
              <PBadge
                :value="data.ownership_status?.is_fully_confirmed ? '已确认' : '待确认'"
                :severity="data.ownership_status?.is_fully_confirmed ? 'success' : 'warning'"
                class="ml-2"
              />
            </div>
          </template>
        </Column>
        <Column header="操作">
          <template #body="{ data }">
            <PButton
              icon="pi pi-check"
              size="small"
              :disabled="data.ownership_status?.[getMyRole() + '_confirmed']"
              @click="confirmOwnership(data.id)"
              v-tooltip.top="'确认归属'"
            />
          </template>
        </Column>
      </PDataTable>
    </div>

    <PDialog v-model:visible="dialogVisible" header="新增批次" :modal="true" class="dialog-form">
      <div class="dialog-content">
        <div class="form-grid">
          <div class="form-row">
            <div>
              <label class="block mb-2 font-medium">批次号 *</label>
              <InputText v-model="form.batch_no" class="w-full" />
            </div>
            <div>
              <label class="block mb-2 font-medium">备件 *</label>
              <PSelect
                v-model="form.spare_part_id"
                :options="partOptions"
                class="w-full"
                placeholder="选择备件"
              />
            </div>
          </div>
          <div class="form-row">
            <div>
              <label class="block mb-2 font-medium">供应商 *</label>
              <PSelect
                v-model="form.supplier_id"
                :options="supplierOptions"
                class="w-full"
                placeholder="选择供应商"
              />
            </div>
            <div>
              <label class="block mb-2 font-medium">数量 *</label>
              <InputNumber v-model="form.quantity" class="w-full" :min="0" />
            </div>
          </div>
          <div class="form-row">
            <div>
              <label class="block mb-2 font-medium">单价 *</label>
              <InputNumber v-model="form.unit_price" class="w-full" :min="0" :min-fraction-digits="2" />
            </div>
            <div>
              <label class="block mb-2 font-medium">存放位置</label>
              <InputText v-model="form.location" class="w-full" />
            </div>
          </div>
          <div class="form-row">
            <div>
              <label class="block mb-2 font-medium">生产日期</label>
              <Calendar v-model="productionDate" class="w-full" date-format="yy-mm-dd" />
            </div>
            <div>
              <label class="block mb-2 font-medium">有效期至</label>
              <Calendar v-model="expiryDate" class="w-full" date-format="yy-mm-dd" />
            </div>
          </div>
        </div>
      </div>
      <template #footer>
        <div class="dialog-footer">
          <PButton label="取消" severity="secondary" @click="dialogVisible = false" />
          <PButton label="保存" @click="saveData" :loading="saving" />
        </div>
      </template>
    </PDialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useMasterDataStore, useAuthStore } from '@/stores'
import { useToast } from 'primevue/usetoast'
import Column from 'primevue/column'
import InputText from 'primevue/inputtext'
import InputNumber from 'primevue/inputnumber'
import Calendar from 'primevue/calendar'

const store = useMasterDataStore()
const authStore = useAuthStore()
const toast = useToast()

const filterSupplier = ref<number | null>(null)
const filterPart = ref<number | null>(null)
const availableOnly = ref(false)
const dialogVisible = ref(false)
const saving = ref(false)

const productionDate = ref<Date | null>(null)
const expiryDate = ref<Date | null>(null)

const form = reactive({
  batch_no: '',
  spare_part_id: null as number | null,
  supplier_id: null as number | null,
  quantity: 0,
  unit_price: 0,
  production_date: null as string | null,
  expiry_date: null as string | null,
  location: ''
})

const canCreate = computed(() => authStore.hasRole(['admin']))
const supplierOptions = computed(() =>
  store.suppliers.map(s => ({ label: s.name, value: s.id }))
)
const partOptions = computed(() =>
  store.spareParts.map(p => ({ label: p.name, value: p.id }))
)

const getMyRole = () => {
  const role = authStore.user?.role
  const map: Record<string, string> = {
    equipment_engineer: 'equipment',
    supplier: 'supplier',
    finance: 'finance',
    admin: 'equipment'
  }
  return map[role || ''] || 'equipment'
}

const loadBatches = () => {
  store.fetchBatches({
    supplier_id: filterSupplier.value || undefined,
    spare_part_id: filterPart.value || undefined,
    available_only: availableOnly.value
  })
}

const openDialog = () => {
  Object.assign(form, {
    batch_no: '',
    spare_part_id: null,
    supplier_id: null,
    quantity: 0,
    unit_price: 0,
    production_date: null,
    expiry_date: null,
    location: ''
  })
  productionDate.value = null
  expiryDate.value = null
  dialogVisible.value = true
}

const saveData = async () => {
  if (!form.batch_no || !form.spare_part_id || !form.supplier_id || !form.quantity || !form.unit_price) {
    toast.add({ severity: 'warn', summary: '提示', detail: '请填写必填项' })
    return
  }
  saving.value = true
  try {
    await store.createBatch({
      ...form,
      spare_part_id: form.spare_part_id!,
      supplier_id: form.supplier_id!,
      production_date: productionDate.value ? productionDate.value.toISOString().split('T')[0] : undefined,
      expiry_date: expiryDate.value ? expiryDate.value.toISOString().split('T')[0] : undefined
    })
    toast.add({ severity: 'success', summary: '成功', detail: '批次创建成功' })
    dialogVisible.value = false
    loadBatches()
  } catch (e: any) {
    toast.add({ severity: 'error', summary: '错误', detail: e.response?.data?.detail || '保存失败' })
  } finally {
    saving.value = false
  }
}

const confirmOwnership = async (batchId: number) => {
  try {
    await store.confirmBatchOwnership(batchId)
    toast.add({ severity: 'success', summary: '成功', detail: '归属确认已提交' })
    loadBatches()
  } catch (e: any) {
    toast.add({ severity: 'error', summary: '错误', detail: e.response?.data?.detail || '确认失败' })
  }
}

onMounted(async () => {
  await Promise.all([
    store.fetchSuppliers(),
    store.fetchSpareParts()
  ])
  loadBatches()
})
</script>
