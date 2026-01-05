<template>
  <div class="service-confirm-container" v-loading="isLoading">
    <el-card class="service-confirm-card" v-if="serviceInfo.serviceId">
      <h2 class="service-confirm-title">确认响应</h2>
      <el-descriptions title="响应信息确认" column="2" border>
        <el-descriptions-item label="响应ID" prop="serviceId">{{ serviceInfo.serviceId }}</el-descriptions-item>
        <el-descriptions-item label="需求ID" prop="needId">{{ serviceInfo.needId }}</el-descriptions-item>
        <el-descriptions-item label="需求主题" prop="needTitle">{{ serviceInfo.needTitle }}</el-descriptions-item>
        <el-descriptions-item label="服务类型" prop="serviceType">{{ serviceInfo.serviceType }}</el-descriptions-item>
        <el-descriptions-item label="响应者" prop="serviceUserName">{{ serviceInfo.serviceUserName }}</el-descriptions-item>
        <el-descriptions-item label="响应时间" prop="createTime">{{ serviceInfo.createTime }}</el-descriptions-item>
        <el-descriptions-item label="响应描述" span="2">
          <div class="description-content">{{ serviceInfo.content || '无' }}</div>
        </el-descriptions-item>
      </el-descriptions>

      <!-- 移除提示框 -->
      <div class="btn-group">
        <el-button @click="goBack" class="cancel-btn">取消</el-button>
        <el-button type="primary" @click="confirmService" class="confirm-btn">确认</el-button>
        <el-button type="danger" @click="rejectService" class="reject-btn">拒绝</el-button>
      </div>
    </el-card>

    <!-- 无数据兜底 -->
    <div class="empty-tip" v-else>
      <el-empty description="暂无该响应信息"></el-empty>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/store/userStore'
import { ElMessage, ElEmpty } from 'element-plus'
import axios from 'axios'

const isMock = false

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

// 响应式状态
const serviceId = route.params.serviceId || ''
const serviceInfo = ref({})
const isLoading = ref(false)

// 获取响应详情
const apiGetServiceDetail = async (serviceId) => {
  if (!serviceId) {
    ElMessage.error('响应ID不能为空')
    return null
  }
  try {
    const baseUrl = process.env.VUE_APP_API_BASE_URL || 'http://127.0.0.1:8000'
    const res = await axios.get(`${baseUrl}/api/service/detail/${serviceId}`, {
      headers: {
        'Authorization': `Bearer ${userStore.userInfo?.token || ''}`,
        'Content-Type': 'application/json'
      },
      timeout: 10000
    })
    if (res.data.code === 200) {
      return res.data.data
    } else {
      ElMessage.error(`获取响应详情失败：${res.data.msg || '接口返回异常'}`)
      return null
    }
  } catch (error) {
    console.error('获取响应详情接口异常：', error)
    if (error.code === 'ECONNABORTED') {
      ElMessage.error('请求超时：请检查网络或后端服务')
    } else if (error.response) {
      ElMessage.error(`后端报错[${error.response.status}]：${error.response.data?.msg || '服务器异常'}`)
    } else {
      ElMessage.error('获取响应详情失败：网络异常')
    }
    return null
  }
}

// 确认响应
const apiConfirmService = async (serviceId) => {
  if (!serviceId) {
    ElMessage.error('响应ID不能为空')
    return false
  }
  try {
    const baseUrl = process.env.VUE_APP_API_BASE_URL || 'http://127.0.0.1:8000'
    const res = await axios.put(`${baseUrl}/api/service/confirm/${serviceId}`, {}, {
      headers: {
        'Authorization': `Bearer ${userStore.userInfo?.token || ''}`,
        'Content-Type': 'application/json'
      },
      timeout: 10000
    })
    if (res.data.code === 200) {
      return true
    } else {
      ElMessage.error(`确认响应失败：${res.data.msg || '接口返回异常'}`)
      return false
    }
  } catch (error) {
    console.error('确认响应接口异常：', error)
    if (error.code === 'ECONNABORTED') {
      ElMessage.error('请求超时：请检查网络或后端服务')
    } else if (error.response) {
      ElMessage.error(`后端报错[${error.response.status}]：${error.response.data?.msg || '服务器异常'}`)
    } else {
      ElMessage.error('确认响应失败：网络异常')
    }
    return false
  }
}

//拒绝响应
const apiRejectService = async (serviceId) => {
  if (!serviceId) {
    ElMessage.error('响应ID不能为空')
    return false
  }
  try {
    const baseUrl = process.env.VUE_APP_API_BASE_URL || 'http://127.0.0.1:8000'
    const res = await axios.put(`${baseUrl}/api/service/reject/${serviceId}`, {}, {
      headers: {
        'Authorization': `Bearer ${userStore.userInfo?.token || ''}`,
        'Content-Type': 'application/json'
      },
      timeout: 10000
    })
    if (res.data.code === 200) {
      return true
    } else {
      ElMessage.error(`拒绝响应失败：${res.data.msg || '接口返回异常'}`)
      return false
    }
  } catch (error) {
    console.error('拒绝响应接口异常：', error)
    if (error.code === 'ECONNABORTED') {
      ElMessage.error('请求超时：请检查网络或后端服务')
    } else if (error.response) {
      ElMessage.error(`后端报错[${error.response.status}]：${error.response.data?.msg || '服务器异常'}`)
    } else {
      ElMessage.error('拒绝响应失败：网络异常')
    }
    return false
  }
}


// 加载响应详情
const loadServiceDetail = async () => {
  isLoading.value = true
  try {
    userStore.initLoginState()

    // 空ID处理
    if (!serviceId) {
      ElMessage.warning('缺少响应ID')
      serviceInfo.value = {}
      return
    }

    let serviceData = null
    if (isMock) {
      serviceData = userStore.serviceSelfList.find(item => item.serviceId === serviceId)
    } else {
      serviceData = await apiGetServiceDetail(serviceId)
    }

    // 无数据处理
    if (!serviceData) {
      ElMessage.warning('响应不存在或已删除')
      serviceInfo.value = {}
      return
    }

    let needData = null
    let serviceUserData = null

    if (isMock) {
      needData = userStore.needList.find(item => item.needId === serviceData.needId) || {}
      serviceUserData = userStore.getUserById(serviceData.userId) || {}
    } else {
      needData = serviceData.needInfo || {}
      serviceUserData = serviceData.serviceUserInfo || {}
    }

    // 最终数据
    serviceInfo.value = {
      ...serviceData,
      needTitle: needData.title || '无关联需求',
      serviceUserName: serviceUserData.username || '未知用户',
      needUserId: needData.userId || ''
    }

    // 权限校验
    if (userStore.userInfo.userId !== serviceInfo.value.needUserId) {
      ElMessage.warning('无权限操作该响应')
      setTimeout(() => router.back(), 1500)
    }
  } catch (error) {
    console.error('加载响应详情异常：', error)
    ElMessage.error('加载响应详情失败：未知错误')
    serviceInfo.value = {}
  } finally {
    isLoading.value = false
  }
}

// 确认响应
const confirmService = async () => {
  if (!serviceInfo.value.serviceId) return

  let isSuccess = false
  if (isMock) {
    const index = userStore.serviceSelfList.findIndex(item => item.serviceId === serviceInfo.value.serviceId)
    if (index !== -1) {
      userStore.serviceSelfList[index].status = 1
      userStore.serviceSelfList[index].updateTime = new Date().toLocaleString()
      // 标记同需求其他响应为已拒绝
      userStore.serviceSelfList.forEach(item => {
        if (item.needId === serviceInfo.value.needId && item.serviceId !== serviceInfo.value.serviceId) {
          item.status = 2
          item.updateTime = new Date().toLocaleString()
        }
      })
      localStorage.setItem('mockServiceSelfList', JSON.stringify(userStore.serviceSelfList))
      isSuccess = true
    }
  } else {
    isSuccess = await apiConfirmService(serviceInfo.value.serviceId)
  }

  if (isSuccess) {
    ElMessage.success('响应已确认（接受）')
    router.push(`/need/detail/${serviceInfo.value.needId}`)
  } else {
    ElMessage.error('确认响应失败')
  }
}

// 拒绝响应
const rejectService = async () => {
  if (!serviceInfo.value.serviceId) return

  let isSuccess = false
  if (isMock) {
    const index = userStore.serviceSelfList.findIndex(item => item.serviceId === serviceInfo.value.serviceId)
    if (index !== -1) {
      userStore.serviceSelfList[index].status = 2
      userStore.serviceSelfList[index].updateTime = new Date().toLocaleString()
      localStorage.setItem('mockServiceSelfList', JSON.stringify(userStore.serviceSelfList))
      isSuccess = true
    }
  } else {
    isSuccess = await apiRejectService(serviceInfo.value.serviceId)
  }

  if (isSuccess) {
    ElMessage.success('响应已拒绝')
    router.push(`/need/detail/${serviceInfo.value.needId}`)
  } else {
    ElMessage.error('拒绝响应失败')
  }
}

// 取消
const goBack = () => {
  router.back()
}


onMounted(() => {
  loadServiceDetail()
})
</script>

<style scoped>

.service-confirm-container {
  padding: 20px;
  background-color: #BFD7EA;
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: flex-start;
}

.service-confirm-card {
  width: 800px;
  padding: 30px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05) !important;
  border-radius: 12px !important;
  border: none !important;
  background-color: #FFFFFF !important;
  margin-top: 20px;
}

.service-confirm-title {
  text-align: center;
  margin-bottom: 20px;
  color: #9A7B68;
  font-weight: 500;
  font-size: 20px;
}

.description-content {
  white-space: pre-wrap;
  line-height: 1.6;
  padding: 5px 0;
  color: #666;
}

.btn-group {
  text-align: center;
  margin-top: 30px;
}

.btn-group .el-button {
  margin: 0 10px;
  width: 120px;
  height: 40px;
  border-radius: 8px !important;
}

/* 按钮配色区分 */
.cancel-btn {
  color: #666 !important;
  border-color: #ddd !important;
}
.cancel-btn:hover {
  background-color: #f5f5f5 !important;
}

.confirm-btn {
  background-color: #9A7B68 !important;
  border-color: #9A7B68 !important;
}
.confirm-btn:hover {
  background-color: #8A6B58 !important;
}

.reject-btn {
  background-color: #E57373 !important;
  border-color: #E57373 !important;
}
.reject-btn:hover {
  background-color: #D32F2F !important;
}

/* 无数据提示 */
.empty-tip {
  width: 100%;
  padding: 60px 0;
  text-align: center;
}
</style>