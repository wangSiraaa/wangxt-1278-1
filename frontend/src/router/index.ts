import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores'
import type { UserRole } from '@/types'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    component: () => import('@/layouts/MainLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        redirect: '/dashboard'
      },
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue')
      },
      {
        path: 'spare-parts',
        name: 'SpareParts',
        component: () => import('@/views/SpareParts.vue'),
        meta: { roles: ['admin', 'equipment_engineer', 'supplier', 'finance'] as UserRole[] }
      },
      {
        path: 'suppliers',
        name: 'Suppliers',
        component: () => import('@/views/Suppliers.vue'),
        meta: { roles: ['admin', 'equipment_engineer', 'finance'] as UserRole[] }
      },
      {
        path: 'batches',
        name: 'Batches',
        component: () => import('@/views/Batches.vue'),
        meta: { roles: ['admin', 'equipment_engineer', 'supplier', 'finance'] as UserRole[] }
      },
      {
        path: 'maintenance-orders',
        name: 'MaintenanceOrders',
        component: () => import('@/views/MaintenanceOrders.vue'),
        meta: { roles: ['admin', 'equipment_engineer'] as UserRole[] }
      },
      {
        path: 'requisitions',
        name: 'Requisitions',
        component: () => import('@/views/Requisitions.vue'),
        meta: { roles: ['admin', 'equipment_engineer'] as UserRole[] }
      },
      {
        path: 'requisitions/new',
        name: 'NewRequisition',
        component: () => import('@/views/RequisitionForm.vue'),
        meta: { roles: ['admin', 'equipment_engineer'] as UserRole[] }
      },
      {
        path: 'replenishments',
        name: 'Replenishments',
        component: () => import('@/views/Replenishments.vue'),
        meta: { roles: ['admin', 'equipment_engineer', 'supplier'] as UserRole[] }
      },
      {
        path: 'replenishments/new',
        name: 'NewReplenishment',
        component: () => import('@/views/ReplenishmentForm.vue'),
        meta: { roles: ['admin', 'supplier'] as UserRole[] }
      },
      {
        path: 'settlements',
        name: 'Settlements',
        component: () => import('@/views/Settlements.vue'),
        meta: { roles: ['admin', 'finance', 'supplier'] as UserRole[] }
      },
      {
        path: 'settlements/new',
        name: 'NewSettlement',
        component: () => import('@/views/SettlementForm.vue'),
        meta: { roles: ['admin', 'finance'] as UserRole[] }
      },
      {
        path: 'monthly-closings',
        name: 'MonthlyClosings',
        component: () => import('@/views/MonthlyClosings.vue'),
        meta: { roles: ['admin', 'finance'] as UserRole[] }
      },
      {
        path: 'alerts',
        name: 'Alerts',
        component: () => import('@/views/SafetyAlerts.vue'),
        meta: { roles: ['admin', 'equipment_engineer', 'finance'] as UserRole[] }
      },
      {
        path: 'ownership-confirmations',
        name: 'OwnershipConfirmations',
        component: () => import('@/views/OwnershipConfirmations.vue'),
        meta: { roles: ['admin', 'equipment_engineer', 'supplier', 'finance'] as UserRole[] }
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFound.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, _from, next) => {
  const authStore = useAuthStore()

  if (to.meta.requiresAuth && !authStore.isLoggedIn) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
    return
  }

  if (to.name === 'Login' && authStore.isLoggedIn) {
    next({ name: 'Dashboard' })
    return
  }

  const roles = to.meta.roles as UserRole[] | undefined
  if (roles && authStore.user && !roles.includes(authStore.user.role)) {
    next({ name: 'Dashboard' })
    return
  }

  next()
})

export default router
