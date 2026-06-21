<template>
  <div>
    <div class="page-header">
      <h1 class="page-title">安全库存预警</h1>
      <PButton
        label="刷新"
        icon="pi pi-refresh"
        @click="loadData"
      />
    </div>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
      <div class="stat-card">
        <div class="stat-icon danger">
          <i class="pi pi-exclamation-triangle"></i>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ pendingCount }}</div>
          <div class="stat-label">待处理预警</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon success">
          <i class="pi pi-check-circle"></i>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ processedCount }}</div>
          <div class="stat-label">已处理预警</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon info">
          <i class="pi pi-chart-bar"></i>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ totalShortage }}</div>
          <div class="stat-label">总短缺数量</div>
        </div>
      </div>
    </div>

    <div class="card">
      <div class="table-toolbar">
        <div class="toolbar-left">
          <PSelect
            v-model="filterProcessed"
            :options="filterOptions"
            placeholder="全部预警"
            class="w-40"
            @change="loadData()"
          />
        </div>
      </div>

      <PDataTable
        :value="store.safetyAlerts"
        :loading="store.loading"
        :paginator="true"
        :rows="10"
        emptyMessage="暂无预警数据"
      >
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
        <Column field="current_stock" header="当前库存" :sortable="true">
          <template #body="{ data }">
            <span class="stock-low">{{ data.current_stock }}</span>
          </template>
        </Column>
        <Column field="safety_stock" header="安全库存" />
        <Column field="shortage" header="短缺数量">
          <template #body="{ data }">
            <span class="stock-low">{{ data.shortage }}</span>
          </template>
        </Column>
        <Column field="created_at" header="预警时间">
          <template #body="{ data }">
            {{ formatDate(data.created_at) }}
          </template>
        </Column>
        <Column header="状态">
          <template #body="{ data }">
            <PBadge
              :value="data.is_processed ? '已处理' : '待处理'"
              :severity="data.is_processed ? 'success' : 'warning'"
            />
          </template>
        </Column>
        <Column header="操作" v-if="canProcess">
          <template #body="{ data }">
            <PButton
              v-if="!data.is_processed"
              icon="pi pi-check"
              size="small"
              severity="success"
              @click="processAlert(data.id)"
              v-tooltip.top="'标记已处理'"
            />
          </template>
        </Column>
      </PDataTable>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useSystemStore, useAuthStore } from '@/stores'
import { useToast } from 'primevue/usetoast'
import Column from 'primevue/column'

const store = useSystemStore()
const authStore = useAuthStore()
const toast = useToast()

const filterProcessed = ref<boolean | null>(null)

const filterOptions = [
  { label: '待处理', value: false },
  { label: '已处理', value: true }
]

const canProcess = computed(() => authStore.hasRole(['admin', 'equipment_engineer']))

const pendingCount = computed(() =>
  store.safetyAlerts.filter(a => !a.is_processed).length
)

const processedCount = computed(() =>
  store.safetyAlerts.filter(a => a.is_processed).length
)

const totalShortage = computed(() =>
  store.safetyAlerts.filter(a => !a.is_processed).reduce((sum, a) => sum + a.shortage, 0)
)

const formatDate = (date: string) => new Date(date).toLocaleString('zh-CN')

const loadData = () => {
  store.fetchSafetyAlerts(filterProcessed.value ?? undefined)
}

const processAlert = async (alertId: number) => {
  try {
    await store.processAlert(alertId)
    toast.add({ severity: 'success', summary: '成功', detail: '已标记为已处理' })
    loadData()
  } catch (e: any) {
    toast.add({ severity: 'error', summary: '错误', detail: e.response?.data?.detail || '操作失败' })
  }
}

onMounted(loadData)
</script>
