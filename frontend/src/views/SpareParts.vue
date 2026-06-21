<template>
  <div>
    <div class="page-header">
      <h1 class="page-title">备件管理</h1>
      <PButton
        v-if="canEdit"
        label="新增备件"
        icon="pi pi-plus"
        @click="openDialog()"
      />
    </div>

    <div class="card">
      <div class="table-toolbar">
        <div class="toolbar-left">
          <InputText
            v-model="searchQuery"
            placeholder="搜索备件编码、名称..."
            class="w-64"
          />
        </div>
      </div>

      <PDataTable
        :value="filteredParts"
        :loading="store.loading"
        :paginator="true"
        :rows="10"
        :rows-per-page-options="[10, 25, 50]"
        emptyMessage="暂无备件数据"
        responsiveLayout="scroll"
      >
        <Column field="code" header="备件编码" :sortable="true" />
        <Column field="name" header="备件名称" :sortable="true" />
        <Column field="specification" header="规格型号" />
        <Column field="unit" header="单位" />
        <Column field="safety_stock" header="安全库存" />
        <Column field="available_stock" header="可用库存" :sortable="true">
          <template #body="{ data }">
            <span :class="data.is_below_safety ? 'stock-low' : 'stock-normal'">
              {{ data.available_stock || 0 }}
            </span>
          </template>
        </Column>
        <Column header="库存状态">
          <template #body="{ data }">
            <PBadge
              :value="data.is_below_safety ? '低于安全库存' : '正常'"
              :severity="data.is_below_safety ? 'danger' : 'success'"
            />
          </template>
        </Column>
        <Column field="is_active" header="状态">
          <template #body="{ data }">
            <PBadge :value="data.is_active ? '启用' : '停用'" :severity="data.is_active ? 'success' : 'secondary'" />
          </template>
        </Column>
        <Column header="操作" v-if="canEdit">
          <template #body="{ data }">
            <PButton
              icon="pi pi-pencil"
              size="small"
              severity="secondary"
              class="mr-2"
              @click="openDialog(data)"
            />
          </template>
        </Column>
      </PDataTable>
    </div>

    <PDialog
      v-model:visible="dialogVisible"
      :header="isEdit ? '编辑备件' : '新增备件'"
      :modal="true"
      :closable="true"
      class="dialog-form"
    >
      <div class="dialog-content">
        <div class="form-grid">
          <div class="form-row">
            <div>
              <label class="block mb-2 font-medium">备件编码 *</label>
              <InputText v-model="form.code" class="w-full" />
            </div>
            <div>
              <label class="block mb-2 font-medium">备件名称 *</label>
              <InputText v-model="form.name" class="w-full" />
            </div>
          </div>
          <div class="form-row">
            <div>
              <label class="block mb-2 font-medium">规格型号</label>
              <InputText v-model="form.specification" class="w-full" />
            </div>
            <div>
              <label class="block mb-2 font-medium">单位 *</label>
              <InputText v-model="form.unit" class="w-full" placeholder="如：件、台、套" />
            </div>
          </div>
          <div class="form-row">
            <div>
              <label class="block mb-2 font-medium">安全库存</label>
              <InputNumber v-model="form.safety_stock" class="w-full" :min="0" />
            </div>
            <div>
              <label class="block mb-2 font-medium">状态</label>
              <PInputSwitch v-model="form.is_active" />
            </div>
          </div>
          <div>
            <label class="block mb-2 font-medium">描述</label>
            <Textarea v-model="form.description" class="w-full" :rows="3" />
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
import { useMasterDataStore } from '@/stores'
import { useAuthStore } from '@/stores'
import { useToast } from 'primevue/usetoast'
import type { SparePart } from '@/types'
import Column from 'primevue/column'
import InputText from 'primevue/inputtext'
import InputNumber from 'primevue/inputnumber'
import Textarea from 'primevue/textarea'

const store = useMasterDataStore()
const authStore = useAuthStore()
const toast = useToast()

const searchQuery = ref('')
const dialogVisible = ref(false)
const isEdit = ref(false)
const saving = ref(false)
const editId = ref<number | null>(null)

const form = reactive({
  code: '',
  name: '',
  specification: '',
  unit: '',
  safety_stock: 0,
  description: '',
  is_active: true
})

const canEdit = computed(() => authStore.hasRole(['admin']))
const filteredParts = computed(() => {
  if (!searchQuery.value) return store.spareParts
  const query = searchQuery.value.toLowerCase()
  return store.spareParts.filter(
    p => p.code.toLowerCase().includes(query) || p.name.toLowerCase().includes(query)
  )
})

const openDialog = (data?: SparePart) => {
  if (data) {
    isEdit.value = true
    editId.value = data.id
    Object.assign(form, {
      code: data.code,
      name: data.name,
      specification: data.specification || '',
      unit: data.unit,
      safety_stock: data.safety_stock,
      description: data.description || '',
      is_active: data.is_active
    })
  } else {
    isEdit.value = false
    editId.value = null
    Object.assign(form, {
      code: '',
      name: '',
      specification: '',
      unit: '',
      safety_stock: 0,
      description: '',
      is_active: true
    })
  }
  dialogVisible.value = true
}

const saveData = async () => {
  if (!form.code || !form.name || !form.unit) {
    toast.add({ severity: 'warn', summary: '提示', detail: '请填写必填项' })
    return
  }
  saving.value = true
  try {
    if (isEdit.value && editId.value) {
      await store.updateSparePart(editId.value, form)
      toast.add({ severity: 'success', summary: '成功', detail: '备件更新成功' })
    } else {
      await store.createSparePart(form)
      toast.add({ severity: 'success', summary: '成功', detail: '备件创建成功' })
    }
    dialogVisible.value = false
  } catch (e: any) {
    toast.add({ severity: 'error', summary: '错误', detail: e.response?.data?.detail || '保存失败' })
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  store.fetchSpareParts()
})
</script>
