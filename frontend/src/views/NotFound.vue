<template>
  <div class="flex flex-col items-center justify-center min-h-screen p-8">
    <h1 class="text-9xl font-bold text-gray-300 mb-4">404</h1>
    <h2 class="text-2xl font-semibold text-gray-700 mb-2">页面未找到</h2>
    <p class="text-gray-500 mb-8">您访问的页面不存在或已被移动。</p>
    <PButton label="返回首页" icon="pi pi-home" @click="router.push('/')" />
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()
</script>
