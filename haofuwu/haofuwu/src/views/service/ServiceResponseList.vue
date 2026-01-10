<template>
  <div class="response-list-container" v-loading="isLoading">
    <el-card class="response-list-card">
      <h2>响应列表 - 需求 {{ needId }}</h2>
      <el-table :data="responses" stripe>
        <el-table-column prop="serviceId" label="响应ID" width="100"></el-table-column>
        <el-table-column prop="userName" label="响应者" width="140"></el-table-column>
        <el-table-column prop="title" label="自荐主题" width="240"></el-table-column>
        <el-table-column prop="content" label="自荐内容"></el-table-column>
        <el-table-column prop="status" label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : (row.status === 2 ? 'danger' : 'warning')">{{ statusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button size="small" @click="viewDetail(row)">查看</el-button>
            <el-button size="small" type="primary" v-if="isOwner && row.status===0" @click="acceptRow(row)">接受</el-button>
            <el-button size="small" type="danger" v-if="isOwner && row.status===0" @click="rejectRow(row)">拒绝</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div v-if="responses.length===0" class="empty-tip">暂无响应</div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/store/userStore'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const needId = Number(route.params.id || route.query.needId || '')
const responses = ref([])
const isLoading = ref(false)
const isOwner = ref(false)

const statusText = (s) => {
  switch (s) {
    case 0: return '待处理'
    case 1: return '已接受'
    case 2: return '已拒绝'
    default: return '未知'
  }
}

const loadResponses = async () => {
  if (!needId) {
    ElMessage.error('缺少需求ID')
    return
  }
  isLoading.value = true
  try {
    userStore.initLoginState()
    const baseUrl = process.env.VUE_APP_API_BASE_URL || 'http://127.0.0.1:8000'
    const token = userStore.token || sessionStorage.getItem('token') || ''
    const res = await axios.get(`${baseUrl}/api/service/by-need/${needId}`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (res.data && res.data.code === 200) {
      responses.value = res.data.data || []
    } else {
      ElMessage.error(res.data.msg || '获取响应失败')
    }

    // determine if current user is the need owner
    const needDetail = await axios.get(`${baseUrl}/api/need/detail/${needId}`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (needDetail.data && needDetail.data.code === 200) {
      isOwner.value = String(needDetail.data.data.userId) === String(userStore.userInfo?.userId)
    }
  } catch (e) {
    console.error('loadResponses error', e)
    ElMessage.error('加载响应失败')
  } finally {
    isLoading.value = false
  }
}

const viewDetail = (row) => {
  // open confirm page for single response
  router.push({ name: 'ServiceConfirm', params: { serviceId: row.serviceId } })
}

const acceptRow = async (row) => {
  try {
    const baseUrl = process.env.VUE_APP_API_BASE_URL || 'http://127.0.0.1:8000'
    const token = userStore.token || sessionStorage.getItem('token') || ''
    const res = await axios.put(`${baseUrl}/api/service/confirm/${row.serviceId}`, {}, {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (res.data && res.data.code === 200) {
      ElMessage.success('已接受该响应')
      await loadResponses()
    } else {
      ElMessage.error(res.data.msg || '接受失败')
    }
  } catch (e) {
    console.error('acceptRow error', e)
    ElMessage.error('网络错误，接受失败')
  }
}

const rejectRow = async (row) => {
  try {
    const baseUrl = process.env.VUE_APP_API_BASE_URL || 'http://127.0.0.1:8000'
    const token = userStore.token || sessionStorage.getItem('token') || ''
    const res = await axios.put(`${baseUrl}/api/service/reject/${row.serviceId}`, {}, {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (res.data && res.data.code === 200) {
      ElMessage.success('已拒绝该响应')
      await loadResponses()
    } else {
      ElMessage.error(res.data.msg || '拒绝失败')
    }
  } catch (e) {
    console.error('rejectRow error', e)
    ElMessage.error('网络错误，拒绝失败')
  }
}

onMounted(() => {
  loadResponses()
})
</script>

<style scoped>
.response-list-card { max-width: 1100px; margin: 20px auto; }
.empty-tip { padding: 30px; text-align: center; color: #999 }
</style>
