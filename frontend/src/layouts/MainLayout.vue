<template>
  <div class="layout-container">
    <aside class="sidebar">
      <div class="sidebar-header">
        <h2 class="text-xl font-bold">寄售库存</h2>
      </div>
      <nav class="sidebar-menu">
        <template v-for="item in menuItems" :key="item.path">
          <router-link
            :to="item.path"
            class="menu-item"
            :class="{ active: $route.path === item.path }"
            v-if="!item.roles || hasRole(item.roles)"
          >
            <i :class="item.icon"></i>
            <span>{{ item.label }}</span>
          </router-link>
        </template>
      </nav>
    </aside>

    <div class="main-content">
      <header class="topbar">
        <div class="flex items-center gap-3">
          <span class="text-lg font-semibold">{{ pageTitle }}</span>
        </div>
        <div class="flex items-center gap-4">
          <PBadge v-if="unreadAlerts > 0" :value="unreadAlerts" severity="danger" class="mr-2">
            <i class="pi pi-bell text-xl cursor-pointer" @click="goToAlerts"></i>
          </PBadge>
          <i v-else class="pi pi-bell text-xl cursor-pointer" @click="goToAlerts"></i>
          <span>{{ authStore.user?.full_name }}</span>
          <PButton label="退出" severity="secondary" size="small" @click="logout" />
        </div>
      </header>

      <main class="page-content">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore, useSystemStore } from '@/stores'
import type { UserRole } from '@/types'

const authStore = useAuthStore()
const systemStore = useSystemStore()
const router = useRouter()
const route = useRoute()

interface MenuItem {
  path: string
  label: string
  icon: string
  roles?: UserRole[]
}

const menuItems: MenuItem[] = [
  { path: '/dashboard', label: '仪表盘', icon: 'pi pi-chart-bar' },
  { path: '/spare-parts', label: '备件管理', icon: 'pi pi-box' },
  { path: '/suppliers', label: '供应商管理', icon: 'pi pi-building', roles: ['admin', 'equipment_engineer', 'finance'] },
  { path: '/batches', label: '批次库存', icon: 'pi pi-tags' },
  { path: '/maintenance-orders', label: '维修单', icon: 'pi pi-wrench', roles: ['admin', 'equipment_engineer'] },
  { path: '/requisitions', label: '领用管理', icon: 'pi pi-shopping-cart', roles: ['admin', 'equipment_engineer'] },
  { path: '/replenishments', label: '补货管理', icon: 'pi pi-refresh', roles: ['admin', 'equipment_engineer', 'supplier'] },
  { path: '/settlements', label: '结算管理', icon: 'pi pi-money-bill', roles: ['admin', 'finance', 'supplier'] },
  { path: '/ownership-confirmations', label: '库存归属确认', icon: 'pi pi-check-circle' },
  { path: '/monthly-closings', label: '月结管理', icon: 'pi pi-calendar', roles: ['admin', 'finance'] },
  { path: '/alerts', label: '安全库存预警', icon: 'pi pi-exclamation-triangle' }
]

const hasRole = (roles: UserRole[]) => {
  if (!authStore.user) return false
  return roles.includes(authStore.user.role)
}

const pageTitle = computed(() => {
  const currentItem = menuItems.find(item => route.path === item.path)
  return currentItem?.label || ''
})

const unreadAlerts = computed(() => {
  return systemStore.safetyAlerts.filter(a => !a.is_processed).length
})

const goToAlerts = () => {
  router.push('/alerts')
}

const logout = () => {
  authStore.logout()
  router.push('/login')
}

onMounted(() => {
  systemStore.fetchSafetyAlerts(false)
})
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
