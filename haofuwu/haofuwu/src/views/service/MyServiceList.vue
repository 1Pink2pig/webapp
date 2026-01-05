<template>
  <!-- 加载状态覆盖整个页面 -->
  <div class="service-list-container" v-loading="isLoading" element-loading-text="加载中...">
    <!-- 服务列表卡片： -->
    <el-card class="service-list-card">
      <h2 class="service-list-title">我服务的需求列表</h2>
      <!-- 搜索筛选栏 -->
      <div class="search-bar">
        <el-input
          v-model="searchKeyword"
          placeholder="请输入需求主题搜索"
          style="width: 300px; margin-right: 10px;"
        ></el-input>
        <el-select
          v-model="serviceType"
          placeholder="请选择服务类型"
          style="width: 180px; margin-right: 10px;"
        >
          <el-option label="全部" value=""></el-option>
          <el-option label="居家维修" value="居家维修"></el-option>
          <el-option label="生活照料" value="生活照料"></el-option>
          <el-option label="清洁保洁" value="清洁保洁"></el-option>
          <el-option label="出行就医" value="出行就医"></el-option>
          <el-option label="餐食服务" value="餐食服务"></el-option>
          <el-option label="其它" value="其它"></el-option>
        </el-select>
        <el-button type="primary" @click="searchService" class="search-btn">搜索</el-button>
        <el-button type="primary" @click="resetSearch" plain class="reset-btn">重置</el-button>
      </div>

      <!-- 服务列表表格 -->
      <el-table
        :data="filterServiceList"
        border
        style="width: 100%; margin-top: 20px;"
        :cell-style="{ padding: '12px 8px' }"
        :header-cell-style="{ background: '#F3E8CE', color: '#4A5568' }"
        v-if="filteredList.length > 0"
      >
        <!-- 需求ID -->
        <el-table-column label="序号" width="100">
          <template #default="scope">
            {{ (currentPage - 1) * pageSize + scope.$index + 1 }}
          </template>
        </el-table-column>
        <el-table-column label="需求主题" prop="title" min-width="200"></el-table-column>
        <el-table-column label="服务类型" prop="serviceType" width="120"></el-table-column>
        <!-- 发布人显示用户名 -->
        <el-table-column label="发布人" width="120">
          <template #default="scope">
            {{ userStore.getUserById(scope.row.userId)?.username || '未知用户' }}
          </template>
        </el-table-column>
        <el-table-column label="发布时间" prop="createTime" width="180"></el-table-column>
        <el-table-column label="状态" prop="status" width="100">
          <template #default="scope">
            <el-tag
              :type="scope.row.status === '0' ? 'info' : 'success'"
              style="background: #F3E8CE; color: #9A7B68; border: none;"
            >
              {{ scope.row.status === '0' ? '待响应' : '已确认' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100">
          <template #default="scope">
            <el-button type="text" @click="goToNeedDetail(scope.row.needId)" class="operate-btn">查看详情</el-button>
          </template>
        </el-table-column>
        <!-- 提供服务列 -->
        <el-table-column label="服务操作" width="120">
          <template #default="scope">
            <el-button
              type="text"
              @click="goToServiceForm(scope.row.needId)"
              class="operate-btn"
              :disabled="scope.row.status !== '0'"
              :style="scope.row.status !== '0' ? 'color: #ccc; cursor: not-allowed;' : ''"
            >
              提供服务
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 空数据提示 -->
      <div class="empty-tip" v-else>
        暂无可服务的需求数据~
      </div>

      <!-- 分页组件 -->
      <div class="pagination-container" v-if="filteredList.length > 0">
        <BasePagination
          :total="total"
          :page-size="pageSize"
          :current-page="currentPage"
          @current-change="handlePageChange"
          :hide-on-single-page="true"
          :show-size-changer="false"
        ></BasePagination>
      </div>
    </el-card>
  </div>
</template>

<script setup>

import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/store/userStore'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'
import BasePagination from '@/components/BasePagination.vue'

const isMock = false

// 初始化
const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const isLoading = ref(false)
const currentUserId = ref('')

// 搜索/筛选条件
const searchKeyword = ref('')
const serviceType = ref('')

// 分页参数
const currentPage = ref(1)
const pageSize = ref(15)
const total = ref(0)

const mockServiceList = ref([])

// 后端
const getServiceList = async () => {
  try {
    isLoading.value = true
    const params = {
      keyword: searchKeyword.value,
      serviceType: serviceType.value
    }

    const res = await axios.get('/api/service-self/my-list', {
      params,
      headers: { Authorization: `Bearer ${localStorage.getItem('token') || ''}` }
    })

    if (res.data.code === 200) {
      // 兼容数组或分页对象
      const resultData = res.data.data
      if (Array.isArray(resultData)) {
        mockServiceList.value = resultData
        total.value = resultData.length
      } else if (resultData && resultData.records) {
        mockServiceList.value = resultData.records
        total.value = resultData.total
      }
    } else {
      ElMessage.error(res.data.msg || '获取服务列表失败')
    }
  } catch (error) {
    console.error('获取服务列表失败：', error)
    if (error.response && error.response.status === 401) {
       ElMessage.error('登录已过期，请重新登录')
    } else if (error.response && error.response.status === 404) {
       ElMessage.error('接口 404 未找到，请检查后端 main.py 是否注册了 service-self')
    } else {
       ElMessage.error('网络错误，无法获取服务列表')
    }
  } finally {
    isLoading.value = false
  }
}

const filteredList = computed(() => {
  let list = [...mockServiceList.value]

  // 筛选关键词搜索
  if (searchKeyword.value) {
    list = list.filter(item => item.title.includes(searchKeyword.value))
  }
  // 筛选服务类型
  if (serviceType.value) {
    list = list.filter(item => item.serviceType === serviceType.value)
  }

  return list
})

const filterServiceList = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredList.value.slice(start, end)
})

watch(filteredList, (newList) => {
  total.value = newList.length
  if (isMock) {
    total.value = newList.length
  }
}, { immediate: true })

// 监听路由参数变化
watch(
  () => route.query.type,
  (newType) => {
    if (newType) {
      serviceType.value = newType
      currentPage.value = 1
      if (isMock) {
        total.value = filteredList.value.length
      } else {
        getServiceList()
      }
      ElMessage.success(`已筛选【${newType}】类服务`)
    }
  },
  { immediate: true }
)

onMounted(() => {
  userStore.initLoginState()

  //校验登录态
  if (!userStore.isLogin) {
    router.push('/login')
    return
  }

  //获取当前登录用户ID
  currentUserId.value = userStore.userInfo.userId || ''

  // 初始化
  if (isMock) {
    mockServiceList.value = userStore.needList
    total.value = filteredList.value.length
  } else {
    getServiceList()
  }
})

// 搜索服务
const searchService = () => {
  currentPage.value = 1
  if (!isMock) {
    getServiceList()
  }
}

// 重置搜索筛选
const resetSearch = () => {
  searchKeyword.value = ''
  serviceType.value = ''
  currentPage.value = 1
  router.push({ name: 'MyServiceList', query: {} })
  if (!isMock) {
    getServiceList()
  }
}

// 分页切换
const handlePageChange = (page) => {
  currentPage.value = page
  if (!isMock) {
    getServiceList()
  }
}

// 跳转到需求详情
const goToNeedDetail = (needId) => {
  if (!needId) {
    ElMessage.error('需求ID为空，无法查看详情')
    return
  }
  router.push({
    name: 'NeedDetail',
    params: { id: needId }
  })
}

// 跳转到提供服务表单页
const goToServiceForm = (needId) => {
  if (!needId) {
    ElMessage.error('需求ID为空，无法提供服务')
    return
  }
  if (!userStore.isLogin) {
    ElMessage.warning('请先登录后再提供服务')
    return router.push('/login')
  }

  ElMessageBox.confirm(
    '确定要为该需求提供服务吗？',
    '提供服务确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'info'
    }
  ).then(() => {
    ElMessage.success('已确认提供服务，正在跳转表单页...')
    console.log('跳转ServiceForm，需求ID：', needId)
    router.push({
      name: 'ServiceForm',
      params: {
        needId: needId,
        serviceId: undefined
      }
    }).catch(err => {
      console.error('路由跳转失败：', err)
      ElMessage.error('表单页面不存在，请检查路由配置')
    })
  }).catch(() => {
    ElMessage.info('已取消提供服务操作')
  })
}
</script>

<style scoped>

.service-list-container {
  width: 100%;
  min-height: 100vh;
  padding: 20px;
  background-color: #BFD7EA;
  display: flex;
  justify-content: center;
  align-items: flex-start;
}

/* 卡片样式 */
.service-list-card {
  width: 90%;
  max-width: 1400px;
  padding: 20px;
  box-shadow: 0 1px 6px rgba(0, 0, 0, 0.05) !important;
  border-radius: 12px !important;
  border: none !important;
  background-color: #FFFFFF !important;
}

/* 列表标题 */
.service-list-title {
  text-align: center;
  margin-bottom: 20px;
  color: #9A7B68;
  font-weight: 500;
  font-size: 20px;
  letter-spacing: 0.3px;
}

/* 搜索栏布局 */
.search-bar {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 10px;
}

/* 空数据提示 */
.empty-tip {
  text-align: center;
  padding: 40px 0;
  color: #9A7B68;
  font-size: 16px;
}

/* 按钮样式 */
.search-btn {
  background-color: #9A7B68 !important;
  border-color: #9A7B68 !important;
  border-radius: 8px !important;
  font-size: 14px;
  padding: 8px 16px;
}
.search-btn:hover {
  background-color: #8A6B58 !important;
  border-color: #8A6B58 !important;
}

.reset-btn {
  color: #9A7B68 !important;
  border-color: #9A7B68 !important;
  border-radius: 8px !important;
  font-size: 14px;
  padding: 8px 16px;
}
.reset-btn:hover {
  background-color: #F5F0E8 !important;
}

/* 表格样式 */
:deep(.el-table) {
  --el-table-border-color: #D9CFB8 !important;
  --el-table-row-hover-bg-color: #F8F6F0 !important;
  border: 1px solid #D9CFB8 !important;
}

:deep(.el-table th) {
  background-color: #F3E8CE !important;
  color: #4A5568 !important;
  font-weight: 400 !important;
}

:deep(.el-table td) {
  border-bottom: 1px solid #D9CFB8 !important;
  border-right: 1px solid #D9CFB8 !important;
}

/* 操作按钮*/
.operate-btn {
  color: #9A7B68 !important;
  font-size: 14px;
}
.operate-btn:hover {
  color: #8A6B58 !important;
}
:deep(.el-button--text.is-disabled) {
  color: #ccc !important;
  cursor: not-allowed !important;
}

/* 分页容器 */
.pagination-container {
  margin-top: 20px;
  text-align: right;
}
:deep(.el-pagination) {
  --el-pagination-button-color: #9A7B68 !important;
  --el-pagination-button-hover-color: #8A6B58 !important;
  --el-pagination-current-page-color: #FFFFFF !important;
  --el-pagination-current-page-bg-color: #9A7B68 !important;
}
</style>