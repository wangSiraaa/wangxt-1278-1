<template>
  <div>
    <div class="page-header">
      <h1 class="page-title">月结管理</h1>
      <PButton
        label="执行月结"
        icon="pi pi-calendar"
        @click="openDialog()"
      />
    </div>

    <div class="card">
      <PDataTable
        :value="store.monthlyClosings"
        :loading="store.loading"
        :paginator="true"
        :rows="10"
        emptyMessage="暂无月结记录"
      >
        <Column field="period" header="期间" :sortable="true" />
        <Column field="is_closed" header="状态">
          <template #body="{ data }">
            <PBadge :value="data.is_closed ? '已结账' : '未结账'" :severity="data.is_closed ? 'success' : 'warning'" />
          </template>
        </Column>
        <Column field="closed_at" header="结账时间">
          <template #body="{ data }">
            {{ data.closed_at ? formatDate(data.closed_at) : '-' }}
          </template>
        </Column>
        <Column field="remark" header="备注" />
        <Column header="操作">
          <template #body="{ data }">
            <PButton
              v-if="data.is_closed"
              icon="pi pi-undo"
              size="small"
              severity="warning"
              @click="reopenPeriod(data.period)"
              v-tooltip.top="'反结账'"
            />
          </template>
        </Column>
      </PDataTable>
    </div>

    <PDialog v-model:visible="dialogVisible" header="执行月结" :modal="true" class="dialog-form">
      <div class="dialog-content">
        <div class="form-grid">
          <div>
            <label class="block mb-2 font-medium">期间 *</label>
            <InputText v-model="form.period" class="w-full" placeholder="如: 2024-01" />
          </div>
          <div>
            <label class="block mb-2 font-medium">备注</label>
            <Textarea v-model="form.remark" class="w-full" :rows="2" />
          </div>
        </div>
        <PMessage
          severity="warning"
          class="mt-4"
          content="月结后，该期间的领用记录将无法修改。请确认所有业务已处理完毕。"
        />
      </div>
      <template #footer>
        <div class="dialog-footer">
          <PButton label="取消" severity="secondary" @click="dialogVisible = false" />
          <PButton label="确认月结" @click="executeClosing" :loading="saving" />
        </div>
      </template>
    </PDialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useSystemStore } from '@/stores'
import { useToast } from 'primevue/usetoast'
import { useConfirm } from 'primevue/useconfirm'
import Column from 'primevue/column'
import InputText from 'primevue/inputtext'
import Textarea from 'primevue/textarea'

const store = useSystemStore()
const toast = useToast()
const confirmDialog = useConfirm()

const dialogVisible = ref(false)
const saving = ref(false)

const form = reactive({
  period: new Date().toISOString().slice(0, 7),
  remark: ''
})

const formatDate = (date: string) => new Date(date).toLocaleString('zh-CN')

const openDialog = () => {
  form.period = new Date().toISOString().slice(0, 7)
  form.remark = ''
  dialogVisible.value = true
}

const executeClosing = async () => {
  if (!form.period) {
    toast.add({ severity: 'warn', summary: '提示', detail: '请输入期间' })
    return
  }
  saving.value = true
  try {
    await store.createMonthlyClosing(form.period, form.remark)
    toast.add({ severity: 'success', summary: '成功', detail: '月结执行成功' })
    dialogVisible.value = false
    store.fetchMonthlyClosings()
  } catch (e: any) {
    toast.add({ severity: 'error', summary: '错误', detail: e.response?.data?.detail || '月结失败' })
  } finally {
    saving.value = false
  }
}

const reopenPeriod = (period: string) => {
  confirmDialog.require({
    header: '确认反结账',
    message: `确定要反结账期间 ${period} 吗？反结账后该期间的领用记录将可以修改。`,
    icon: 'pi pi-exclamation-triangle',
    accept: async () => {
      try {
        await store.reopenMonthlyClosing(period)
        toast.add({ severity: 'success', summary: '成功', detail: '反结账成功' })
        store.fetchMonthlyClosings()
      } catch (e: any) {
        toast.add({ severity: 'error', summary: '错误', detail: e.response?.data?.detail || '反结账失败' })
      }
    }
  })
}

onMounted(() => {
  store.fetchMonthlyClosings()
})
</script>
