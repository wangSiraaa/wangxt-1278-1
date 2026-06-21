<template>
  <div>
    <div class="page-header">
      <h1 class="page-title">维修单管理</h1>
      <PButton
        label="新增维修单"
        icon="pi pi-plus"
        @click="openDialog()"
      />
    </div>

    <div class="card">
      <PDataTable
        :value="store.maintenanceOrders"
        :loading="store.loading"
        :paginator="true"
        :rows="10"
        emptyMessage="暂无维修单数据"
      >
        <Column field="order_no" header="维修单号" :sortable="true" />
        <Column field="equipment_code" header="设备编码" />
        <Column field="equipment_name" header="设备名称" />
        <Column field="description" header="故障描述" />
        <Column field="is_closed" header="状态">
          <template #body="{ data }">
            <PBadge :value="data.is_closed ? '已关闭' : '进行中'" :severity="data.is_closed ? 'success' : 'warning'" />
          </template>
        </Column>
        <Column field="created_at" header="创建时间">
          <template #body="{ data }">
            {{ formatDate(data.created_at) }}
          </template>
        </Column>
        <Column header="操作">
          <template #body="{ data }">
            <PButton
              icon="pi pi-pencil"
              size="small"
              severity="secondary"
              class="mr-2"
              @click="openDialog(data)"
              :disabled="data.is_closed"
            />
          </template>
        </Column>
      </PDataTable>
    </div>

    <PDialog v-model:visible="dialogVisible" :header="isEdit ? '编辑维修单' : '新增维修单'" :modal="true" class="dialog-form">
      <div class="dialog-content">
        <div class="form-grid">
          <div class="form-row">
            <div>
              <label class="block mb-2 font-medium">维修单号 *</label>
              <InputText v-model="form.order_no" class="w-full" />
            </div>
            <div>
              <label class="block mb-2 font-medium">设备编码 *</label>
              <InputText v-model="form.equipment_code" class="w-full" />
            </div>
          </div>
          <div>
            <label class="block mb-2 font-medium">设备名称 *</label>
            <InputText v-model="form.equipment_name" class="w-full" />
          </div>
          <div>
            <label class="block mb-2 font-medium">故障描述</label>
            <Textarea v-model="form.description" class="w-full" :rows="3" />
          </div>
          <div v-if="isEdit">
            <PInputSwitch v-model="form.is_closed" />
            <label class="ml-2">关闭维修单</label>
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
import { ref, reactive, onMounted } from 'vue'
import { useMasterDataStore } from '@/stores'
import { useToast } from 'primevue/usetoast'
import type { MaintenanceOrder } from '@/types'
import Column from 'primevue/column'
import InputText from 'primevue/inputtext'
import Textarea from 'primevue/textarea'

const store = useMasterDataStore()
const toast = useToast()

const dialogVisible = ref(false)
const isEdit = ref(false)
const saving = ref(false)
const editId = ref<number | null>(null)

const form = reactive({
  order_no: '',
  equipment_code: '',
  equipment_name: '',
  description: '',
  is_closed: false
})

const formatDate = (date: string) => new Date(date).toLocaleString('zh-CN')

const openDialog = (data?: MaintenanceOrder) => {
  if (data) {
    isEdit.value = true
    editId.value = data.id
    Object.assign(form, {
      order_no: data.order_no,
      equipment_code: data.equipment_code,
      equipment_name: data.equipment_name,
      description: data.description || '',
      is_closed: data.is_closed
    })
  } else {
    isEdit.value = false
    editId.value = null
    Object.assign(form, {
      order_no: '',
      equipment_code: '',
      equipment_name: '',
      description: '',
      is_closed: false
    })
  }
  dialogVisible.value = true
}

const saveData = async () => {
  if (!form.order_no || !form.equipment_code || !form.equipment_name) {
    toast.add({ severity: 'warn', summary: '提示', detail: '请填写必填项' })
    return
  }
  saving.value = true
  try {
    if (isEdit.value && editId.value) {
      await store.updateMaintenanceOrder(editId.value, form)
      toast.add({ severity: 'success', summary: '成功', detail: '维修单更新成功' })
    } else {
      await store.createMaintenanceOrder(form)
      toast.add({ severity: 'success', summary: '成功', detail: '维修单创建成功' })
    }
    dialogVisible.value = false
    store.fetchMaintenanceOrders()
  } catch (e: any) {
    toast.add({ severity: 'error', summary: '错误', detail: e.response?.data?.detail || '保存失败' })
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  store.fetchMaintenanceOrders()
})
</script>
