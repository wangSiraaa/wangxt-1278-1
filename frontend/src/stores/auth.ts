import { defineStore } from 'pinia'
import type { User, UserRole } from '@/types'
import { authApi } from '@/api'

interface AuthState {
  token: string | null
  user: User | null
}

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    token: null,
    user: null
  }),
  persist: true,
  getters: {
    isLoggedIn: (state) => !!state.token,
    userRole: (state): UserRole | null => state.user?.role || null,
    userName: (state) => state.user?.full_name || '',
    hasRole: (state) => (roles: UserRole[]) => {
      if (!state.user) return false
      return roles.includes(state.user.role)
    }
  },
  actions: {
    async login(username: string, password: string) {
      const response = await authApi.login({ username, password })
      this.token = response.access_token
      await this.fetchCurrentUser()
    },
    async fetchCurrentUser() {
      this.user = await authApi.getCurrentUser()
    },
    logout() {
      this.token = null
      this.user = null
    }
  }
})
