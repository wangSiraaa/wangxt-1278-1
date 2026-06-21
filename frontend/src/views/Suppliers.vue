<template>
  <div>
    <div class="page-header">
      <h1 class="page-title">供应商管理</h1>
      <PButton
        v-if="canEdit"
        label="新增供应商"
        icon="pi pi-plus"
        @click="openDialog()"
      />
    </div>

    <div class="card">
      <PDataTable
        :value="store.suppliers"
        :loading="store.loading"
        :paginator="true"
        :rows="10"
        emptyMessage="暂无供应商数据"
      >
        <Column field="code" header="供应商编码" :sortable="true" />
        <Column field="name" header="供应商名称" :sortable="true" />
        <Column field="contact_person" header="联系人" />
        <Column field="phone" header="联系电话" />
        <Column field="email" header="邮箱" />
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
              @click="openDialog(data)"
            />
          </template>
        </Column>
      </PDataTable>
    </div>

    <PDialog v-model:visible="dialogVisible" :header="isEdit ? '编辑供应商' : '新增供应商'" :modal="true" class="dialog-form">
      <div class="dialog-content">
        <div class="form-grid">
          <div class="form-row">
            <div>
              <label class="block mb-2 font-medium">供应商编码 *</label>
              <InputText v-model="form.code" class="w-full" />
            </div>
            <div>
              <label class="block mb-2 font-medium">供应商名称 *</label>
              <InputText v-model="form.name" class="w-full" />
            </div>
          </div>
          <div class="form-row">
            <div>
              <label class="block mb-2 font-medium">联系人</label>
              <InputText v-model="form.contact_person" class="w-full" />
            </div>
            <div>
              <label class="block mb-2 font-medium">联系电话</label>
              <InputText v-model="form.phone" class="w-full" />
            </div>
          </div>
          <div>
            <label class="block mb-2 font-medium">邮箱</label>
            <InputText v-model="form.email" class="w-full" />
          </div>
          <div>
            <label class="block mb-2 font-medium">地址</label>
            <Textarea v-model="form.address" class="w-full" :rows="2" />
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
import type { Supplier } from '@/types'
import Column from 'primevue/column'
import InputText from 'primevue/inputtext'
import Textarea from 'primevue/textarea'

const store = useMasterDataStore()
const authStore = useAuthStore()
const toast = useToast()

const dialogVisible = ref(false)
const isEdit = ref(false)
const saving = ref(false)
const editId = ref<number | null>(null)

const form = reactive({
  code: '',
  name: '',
  contact_person: '',
  phone: '',
  email: '',
  address: ''
})

const canEdit = computed(() => authStore.hasRole(['admin']))

const openDialog = (data?: Supplier) => {
  if (data) {
    isEdit.value = true
    editId.value = data.id
    Object.assign(form, {
      code: data.code,
      name: data.name,
      contact_person: data.contact_person || '',
      phone: data.phone || '',
      email: data.email || '',
      address: data.address || ''
    })
  } else {
    isEdit.value = false
    editId.value = null
    Object.assign(form, {
      code: '',
      name: '',
      contact_person: '',
      phone: '',
      email: '',
      address: ''
    })
  }
  dialogVisible.value = true
}

const saveData = async () => {
  if (!form.code || !form.name) {
    toast.add({ severity: 'warn', summary: '提示', detail: '请填写必填项' })
    return
  }
  saving.value = true
  try {
    if (isEdit.value && editId.value) {
      await store.updateSupplier(editId.value, form)
      toast.add({ severity: 'success', summary: '成功', detail: '供应商更新成功' })
    } else {
      await store.createSupplier(form)
      toast.add({ severity: 'success', summary: '成功', detail: '供应商创建成功' })
    }
    dialogVisible.value = false
  } catch (e: any) {
    toast.add({ severity: 'error', summary: '错误', detail: e.response?.data?.detail || '保存失败' })
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  store.fetchSuppliers()
})
</script>
