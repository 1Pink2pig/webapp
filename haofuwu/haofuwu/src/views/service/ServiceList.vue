<template>
  <div class="service-self-container" v-loading="loading">
    <el-card class="service-self-card">
      <!-- 头部：标题 + 筛选区 -->
      <div class="header-wrap">
        <h2 class="page-title">我的服务自荐列表</h2>
        <div class="search-wrap">
          <!-- 纯搜索框 -->
          <el-input
            v-model="searchKey"
            placeholder="请输入服务主题搜索"
            class="search-input"
            @input="handleFilter"
          ></el-input>

          <el-select
            v-model="serviceType"
            placeholder="请选择服务类型"
            class="type-select"
            @change="handleFilter"
          >
            <el-option label="全部类型" value=""></el-option>
            <el-option label="居家维修" value="居家维修"></el-option>
            <el-option label="生活照料" value="生活照料"></el-option>
            <el-option label="清洁保洁" value="清洁保洁"></el-option>
            <el-option label="出行就医" value="出行就医"></el-option>
            <el-option label="餐食服务" value="餐食服务"></el-option>
            <el-option label="其它" value="其它"></el-option>
          </el-select>

          <el-switch
            v-model="onlyAccepted"
            active-text="只看已接受"
            inactive-text="显示全部"
            @change="handleFilter"
          ></el-switch>
        </div>
      </div>

      <!-- 列表表格 -->
      <el-table
        :data="filteredList"
        border
        stripe
        class="service-table"
        :row-height="60"
      >
        <!-- 自荐ID → ID，显示当前登录用户的用户名 -->
        <el-table-column label="服务类型" prop="serviceType" width="120"></el-table-column>
        <el-table-column label="服务主题" prop="title" width="200"></el-table-column>
        <el-table-column label="自荐内容" prop="content" min-width="280"></el-table-column>
        <el-table-column label="提交时间" prop="createTime" width="180"></el-table-column>
        <!-- 状态改为三种：待接受/已接受/已拒绝 -->
        <el-table-column label="状态" prop="status" width="100">
          <template #default="scope">
            <el-tag :type="getStatusTagType(scope.row.status)">
              {{ getStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <!-- 操作列 -->
        <el-table-column label="操作" width="280">
          <template #default="scope">
            <el-button type="default" size="small" @click="viewDetail(scope.row)">查看</el-button>
            <el-button
              type="primary"
              size="small"
              @click="editService(scope.row)"
              v-if="scope.row.status === 0"
            >
              修改
            </el-button>
            <el-button
              type="danger"
              size="small"
              @click="deleteService(scope.row.serviceId)"
              v-if="scope.row.status === 0"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>

import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/store/userStore'
import axios from 'axios'

const isMock = false

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const loading = ref(false)

const searchKey = ref('')
const serviceType = ref('')
const onlyAccepted = ref(false)
const rawList = ref([])
const filteredList = ref([])

// 状态文本
const getStatusText = (status) => {
  switch (status) {
    case 0: return '待接受'
    case 1: return '已接受'
    case 2: return '已拒绝'
    default: return '未知状态'
  }
}

// 状态标签类型
const getStatusTagType = (status) => {
  switch (status) {
    case 0: return 'warning'
    case 1: return 'success'
    case 2: return 'danger'
    default: return 'info'
  }
}

// 页面初始化
onMounted(async () => {
  try {
    userStore.initLoginState()
    if (!userStore.isLogin) {
      ElMessage.warning('请先登录后再访问服务自荐列表')
      router.push({
        path: '/login',
        query: { redirect: route.fullPath || '/service/list' }
      })
      return
    }
    await loadServiceSelfList()
  } catch (err) {
    ElMessage.error('页面初始化失败：' + err.message)
  }
})

// 后端
const apiGetMyServiceSelfList = async () => {
  try {
    const baseUrl = process.env.VUE_APP_API_BASE_URL || 'http://127.0.0.1:8000'
    const response = await axios.get(
      `${baseUrl}/api/service-self/my-list`,
      {
        headers: {
          'Content-Type': 'application/json',
          // use the canonical token stored in userStore.token (persisted to localStorage by setLoginSuccess/initLoginState)
          'Authorization': userStore.token ? `Bearer ${userStore.token}` : ''
        },
        timeout: 10000
      }
    )
    const res = response.data
    if (res.code === 200) {
      return res.data || []
    } else {
      ElMessage.error(`获取列表失败：${res.msg || '接口返回异常'}`)
      return []
    }
  } catch (error) {
    console.error('获取列表接口异常：', error)
    if (error.code === 'ECONNABORTED') {
      ElMessage.error('请求超时：请检查网络或后端服务')
    } else if (error.response) {
      ElMessage.error(`后端报错[${error.response.status}]：${error.response.data?.msg || '服务器异常'}`)
    } else if (error.request) {
      ElMessage.error('网络错误：无法连接到后端服务器，请检查服务是否启动')
    } else {
      ElMessage.error('请求初始化失败：' + error.message)
    }
    return []
  }
}

// 删除接口函数
const apiDeleteServiceSelf = async (serviceId) => {
  if (!serviceId) {
    ElMessage.error('删除失败：缺少服务ID')
    return false
  }
  try {
    const baseUrl = process.env.VUE_APP_API_BASE_URL || 'http://127.0.0.1:8000'
    const response = await axios.delete(
      `${baseUrl}/api/service-self/${serviceId}`,
      {
        headers: {
          'Content-Type': 'application/json',
          // ensure we send the stored token
          'Authorization': userStore.token ? `Bearer ${userStore.token}` : ''
        },
        timeout: 10000
      }
    )
    const res = response.data
    if (res.code === 200) {
      ElMessage.success('删除服务自荐成功')
      return true
    } else {
      ElMessage.error(`删除失败：${res.msg || '仅可删除未被接受的自荐'}`)
      return false
    }
  } catch (error) {
    console.error('删除接口异常：', error)
    ElMessage.error('删除失败：网络异常或服务器错误')
    return false
  }
}

// 加载列表
const loadServiceSelfList = async () => {
  loading.value = true
  try {
    let list = []
    if (isMock) {
      list = Array.isArray(userStore.myServiceSelfList) ? userStore.myServiceSelfList : []
      console.log('加载的服务列表：', list)
    } else {
      list = await apiGetMyServiceSelfList()
    }
    rawList.value = list
    handleFilter()
  } catch (err) {
    ElMessage.error(`加载列表失败：${err.message || '未知错误'}`)
    rawList.value = []
    filteredList.value = []
  } finally {
    loading.value = false
  }
}

// 筛选逻辑
const handleFilter = () => {
  const originList = Array.isArray(rawList.value) ? [...rawList.value] : []
  let filtered = [...originList]

  if (searchKey.value.trim()) {
    const keyword = searchKey.value.trim().toLowerCase()
    filtered = filtered.filter(item =>
      item.title && item.title.toLowerCase().includes(keyword)
    )
  }

  if (serviceType.value.trim()) {
    filtered = filtered.filter(item => item.serviceType === serviceType.value)
  }

  if (onlyAccepted.value) {
    filtered = filtered.filter(item => item.status === 1)
  }

  filteredList.value = filtered
}

// 跳转详情页
const viewDetail = (row) => {
  if (!row || !row.serviceId) {
    ElMessage.warning('查看失败：缺少服务ID')
    return
  }
  console.log('跳转详情页，服务ID：', row.serviceId)
  console.log('全局服务列表：', userStore.serviceSelfList)

  router.push({
    name: 'ServiceDetail',
    params: { id: row.serviceId }
  }).catch(err => {
    console.error('跳转详情页失败：', err)
    ElMessage.error('跳转失败，请检查路由配置')
  })
}

// 修改服务
const editService = (row) => {
  if (!row || !row.serviceId) {
    ElMessage.warning('修改失败：缺少服务ID')
    return
  }
  // 获取有效needId
  let validNeedId = row.needId
  if (!validNeedId) {
    const matchedNeed = userStore.needList.find(item => item.serviceType === row.serviceType)
    validNeedId = matchedNeed ? matchedNeed.needId : 'none'
  }
  router.push({
    name: 'ServiceForm',
    params: {
      needId: validNeedId,
      serviceId: row.serviceId
    }
  })
}

// 删除服务
const deleteService = async (serviceId) => {
  if (!serviceId) {
    ElMessage.warning('删除失败：缺少服务ID')
    return
  }
  try {
    const confirmResult = await ElMessageBox.confirm(
      '确认删除该服务自荐？删除后无法恢复',
      '删除确认',
      {
        confirmButtonText: '确认删除',
        cancelButtonText: '取消',
        type: 'warning',
        closeOnClickModal: false
      }
    )

    if (confirmResult === 'confirm') {
      loading.value = true
      let deleteSuccess = false

      if (isMock) {
        deleteSuccess = typeof userStore.deleteServiceSelf === 'function'
          ? userStore.deleteServiceSelf(serviceId)
          : false
        if (deleteSuccess) {
          ElMessage.success('删除成功（本地模式）')
        } else {
          ElMessage.error('删除失败：仅可删除未被接受的自荐（本地模式）')
        }
      } else {
        deleteSuccess = await apiDeleteServiceSelf(serviceId)
      }

      if (deleteSuccess) {
        await loadServiceSelfList()
      }
    }
  } catch (err) {
    if (err !== 'cancel') {
      ElMessage.error(`删除操作异常：${err.message || '请重试'}`)
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>

:root {
  --morandi-bg: #BFD7EA;
  --morandi-white: #FFFFFF;
  --morandi-main: #9A7B68;
  --morandi-hover: #E8E0D5;
  --morandi-text: #4A5568;
  --danger-color: #e57373;
}


.service-self-container {
  width: 100%;
  min-height: calc(100vh - 40px);
  padding: 20px;
  background-color: var(--morandi-bg);
}

/* 卡片样式 */
.service-self-card {
  max-width: 1400px;
  margin: 0 auto;
  background-color: var(--morandi-white);
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  border: none;
  padding: 30px;
}

/* 头部样式 */
.header-wrap {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  flex-wrap: wrap;
  gap: 16px;
}

.page-title {
  font-size: 24px;
  font-weight: 900;
  color: var(--morandi-main);
  margin: 0;
  letter-spacing: 0.2px;
}

/* 搜索区样式 */
.search-wrap {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
  width: 100%;
  max-width: 800px;
}

.search-input {
  width: 300px !important;
}

.type-select {
  width: 200px !important;
}

/* 表格核心样式 */
.service-table {
  --el-table-header-text-color: var(--morandi-text);
  --el-table-row-hover-bg-color: var(--morandi-hover);
  --el-table-row-hover-text-color: var(--morandi-main);
  --el-table-border-color: var(--morandi-bg);
  margin-top: 10px;
}

/* 表格头部样式 */
:deep(.el-table th) {
  background-color: var(--morandi-bg) !important;
  font-weight: 600;
  padding: 12px 8px !important;
}

:deep(.el-table td) {
  border-bottom: 1px solid var(--morandi-bg) !important;
  padding: 18px 12px !important;
  overflow: visible !important;
  white-space: normal !important;
  text-align: left !important;
  height: auto !important;
}

:deep(.el-table .el-button) {
  display: inline-block !important;
  visibility: visible !important;
  opacity: 1 !important;
  pointer-events: auto !important;
  margin: 0 4px !important;
}

/* 按钮 */
:deep(.el-button--default) {
  color: #9A7B68 !important;
  border-color: var(--morandi-hover) !important;
  background-color: var(--morandi-white) !important;
}

:deep(.el-button--primary) {
  background-color: #9A7B68 !important;
  border-color: white !important;
  color: white !important;
}

:deep(.el-button--danger) {
  background-color: red !important;
  border-color: red !important;
  color: white !important;
}

/* 表格行 */
:deep(.el-table__row:hover td) {
  background-color: var(--morandi-hover) !important;
}

/* 状态标签 */
:deep(.el-tag--warning) {
  background-color: #F3E8CE !important;
  color: #9A7B68 !important;
  border: none !important;
}
:deep(.el-tag--success) {
  background-color: #E8F5E9 !important;
  color: #4CAF50 !important;
  border: none !important;
}
:deep(.el-tag--danger) {
  background-color: #FFEBEE !important;
  color: #F44336 !important;
  border: none !important;
}
</style>