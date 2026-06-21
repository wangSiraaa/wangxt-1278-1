export const formatDate = (date: string | Date | null | undefined): string => {
  if (!date) return '-'
  const d = typeof date === 'string' ? new Date(date) : date
  return d.toLocaleString('zh-CN')
}

export const formatNumber = (num: number, decimals: number = 2): string => {
  return num.toLocaleString('zh-CN', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals
  })
}

export const formatCurrency = (amount: number): string => {
  return `¥${formatNumber(amount)}`
}

export const generateBatchNo = (prefix: string = 'B'): string => {
  const now = new Date()
  const timestamp = now.toISOString().slice(0, 10).replace(/-/g, '')
  const random = Math.floor(Math.random() * 10000).toString().padStart(4, '0')
  return `${prefix}${timestamp}${random}`
}

export const getCurrentPeriod = (): string => {
  const now = new Date()
  return `${now.getFullYear()}-${(now.getMonth() + 1).toString().padStart(2, '0')}`
}

export const getStatusColor = (status: string): string => {
  const colorMap: Record<string, string> = {
    draft: 'secondary',
    pending: 'warning',
    approved: 'info',
    rejected: 'danger',
    delivered: 'success',
    settled: 'success',
    in_transit: 'info',
    received: 'success',
    paid: 'success',
    confirmed: 'success'
  }
  return colorMap[status] || 'secondary'
}

export const getStatusText = (status: string): string => {
  const textMap: Record<string, string> = {
    draft: '草稿',
    pending: '待审批',
    approved: '已审批',
    rejected: '已拒绝',
    delivered: '已出库',
    settled: '已结算',
    in_transit: '运输中',
    received: '已入库',
    paid: '已付款',
    confirmed: '已确认'
  }
  return textMap[status] || status
}

export const getRoleText = (role: string): string => {
  const textMap: Record<string, string> = {
    equipment_engineer: '设备工程师',
    supplier: '供应商',
    finance: '财务',
    admin: '管理员'
  }
  return textMap[role] || role
}

export const validateRequired = (value: string | number | null | undefined): string | null => {
  if (value === null || value === undefined || value === '') {
    return '此字段为必填项'
  }
  if (typeof value === 'number' && value <= 0) {
    return '必须大于0'
  }
  return null
}
