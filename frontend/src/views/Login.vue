<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <i class="pi pi-cog text-5xl text-primary mb-4"></i>
        <h1 class="login-title">工业备件寄售库存</h1>
        <p class="login-subtitle">请登录以继续</p>
      </div>

      <PMessage v-if="error" severity="error" :content="error" class="mb-4" />

      <form @submit.prevent="handleLogin" class="form-grid">
        <InputText
          id="username"
          v-model="form.username"
          placeholder="用户名"
          class="w-full"
          :class="{ 'p-invalid': submitted && !form.username }"
          required
        />
        <Password
          id="password"
          v-model="form.password"
          placeholder="密码"
          class="w-full"
          :class="{ 'p-invalid': submitted && !form.password }"
          required
          :feedback="false"
        />
        <PButton type="submit" label="登录" class="w-full" :loading="loading" />
      </form>

      <div class="mt-6 text-center text-sm text-gray-500">
        <p>默认账号:</p>
        <p class="mt-1">admin / admin123 (管理员)</p>
        <p>engineer1 / engineer123 (设备工程师)</p>
        <p>supplier1 / supplier123 (供应商)</p>
        <p>finance1 / finance123 (财务)</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores'
import Password from 'primevue/password'
import InputText from 'primevue/inputtext'

const authStore = useAuthStore()
const router = useRouter()
const route = useRoute()

const form = reactive({
  username: '',
  password: ''
})
const loading = ref(false)
const error = ref('')
const submitted = ref(false)

const handleLogin = async () => {
  submitted.value = true
  if (!form.username || !form.password) return

  loading.value = true
  error.value = ''
  try {
    await authStore.login(form.username, form.password)
    const redirect = route.query.redirect as string || '/dashboard'
    router.push(redirect)
  } catch (e: any) {
    error.value = e.response?.data?.detail || '登录失败，请检查用户名和密码'
  } finally {
    loading.value = false
  }
}
</script>
