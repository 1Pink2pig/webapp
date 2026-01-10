<template>
  <div class="need-list-container" v-loading="isLoading" element-loading-text="加载中...">
    <el-card class="need-list-card">
      <h2 class="need-list-title">我的需求</h2>

      <!-- 筛选栏 -->
      <div class="search-bar">
        <el-input
          v-model="searchKeyword"
          placeholder="输入需求主题搜索"
          style="flex: 1; min-width: 150px; margin-right: 10px;"
        ></el-input>
        <el-select
          v-model="serviceType"
          placeholder="选择服务类型"
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
        <div class="btn-group">
          <el-button type="primary" @click="searchNeed" class="search-btn">搜索</el-button>
          <el-button type="primary" @click="resetSearch" plain class="reset-btn">重置</el-button>
          <el-button type="primary" @click="goToAddNeed" class="add-btn">发布新需求</el-button>
        </div>
      </div>

      <!-- 需求表格 -->
      <el-table
        :data="displayNeedList"
        border
        style="width: 100%; margin-top: 20px;"
        :cell-style="{ padding: '10px 8px' }"
        :header-cell-style="{ background: '#F3E8CE', color: '#4A5568', borderBottom: '1px solid #D9CFB8' }"
        empty-text="暂无符合条件的需求"
      >
        <el-table-column label="需求ID" prop="needId" width="100" align="center"></el-table-column>
        <el-table-column label="需求主题" prop="title" min-width="180">
          <template #default="scope">
            <span class="title-text">{{ scope.row.title }}</span>
          </template>
        </el-table-column>
        <el-table-column label="服务类型" prop="serviceType" width="120" align="center"></el-table-column>
        <el-table-column label="地域" prop="region" width="150" align="center"></el-table-column>
        <el-table-column label="发布时间" prop="createTime" width="160" align="center"></el-table-column>
        <el-table-column label="状态" prop="status" width="100" align="center">
          <template #default="scope">
            <!-- 核心修改：优先判断已响应，再判断已发布/已取消 -->
            <el-tag
              :class="[
                scope.row.hasResponse ? 'status-responded' : '',
                !scope.row.hasResponse && scope.row.status === 0 ? 'status-published' : '',
                !scope.row.hasResponse && scope.row.status === -1 ? 'status-canceled' : ''
              ]"
              size="small"
            >
              {{
                scope.row.hasResponse ? '已响应' :
                scope.row.status === 0 ? '已发布' : '已取消'
              }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" align="center">
          <template #default="scope">
            <el-button type="text" @click="goToNeedDetail(scope.row.needId)" class="operate-btn view-btn">查看详情</el-button>
            <el-button
              type="text"
              @click="goToEditNeed(scope.row.needId)"
              :disabled="!canOperate(scope.row)"
              class="operate-btn edit-btn"
              :title="!canOperate(scope.row) ? '已取消/有响应的需求不可修改' : ''"
            >修改</el-button>
            <el-button
              type="text"
              danger
              @click="deleteNeed(scope.row.needId)"
              :disabled="!canOperate(scope.row)"
              class="operate-btn delete-btn"
              :title="!canOperate(scope.row) ? '已取消/有响应的需求不可删除' : ''"
            >删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container" v-if="total > 0">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 15, 20]"
          layout="total, sizes, prev, pager, next"
          @current-change="handlePageChange"
          @size-change="handleSizeChange"
          style="text-align: right; margin-top: 20px;"
        ></el-pagination>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/store/userStore'
import { ElMessage, ElMessageBox, ElLoading } from 'element-plus'
import axios from 'axios'

const isMock = ref(false) // 切换为后端模式：列表从后端获取发布的需求

const isLoading = ref(false)
const router = useRouter()
const userStore = useUserStore()
const currentUserId = ref('')

// 筛选条件
const searchKeyword = ref('')
const serviceType = ref('')
// 分页参数
const currentPage = ref(1)
const pageSize = ref(15)
const total = ref(0)

// 原始数据
const myAllNeeds = ref([])
// 筛选后的数据
const filteredNeeds = ref([])
// 最终显示的数据
const displayNeedList = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return filteredNeeds.value.slice(start, start + pageSize.value)
})

/**
 * 权限判断：是否可修改/删除（已发布(0)+无响应），已取消(-1)/已响应不可操作
 * @param {Object} need - 需求数据
 * @returns {boolean} 是否可操作
 */
const canOperate = (need) => {
  // 已响应/已取消的需求都不可操作
  return need.status === 0 && !need.hasResponse
}

/**
 * 筛选数据
 */
const filterData = () => {
  let result = [...myAllNeeds.value]
  // 关键词筛选
  if (searchKeyword.value.trim()) {
    const keyword = searchKeyword.value.trim()
    result = result.filter(need => need.title.includes(keyword))
  }
  // 服务类型筛选
  if (serviceType.value) {
    result = result.filter(need => need.serviceType === serviceType.value)
  }
  filteredNeeds.value = result
  total.value = result.length
}

/**
 * 获取我的需求列表
 */
const fetchMyNeeds = async () => {
  isLoading.value = true
  try {
    if (isMock.value) {
      const stored = localStorage.getItem('mockNeedList')
      const initData = Array.isArray(userStore.needList) ? [...userStore.needList] : []
      const allNeeds = stored ? JSON.parse(stored) : initData

      myAllNeeds.value = allNeeds
        .filter(need => need.userId === currentUserId.value)
        .map(need => ({
          ...need,
          status: need.status === undefined ? 0 : Number(need.status),
          hasResponse: Boolean(need.hasResponse) || false
        }))

      filterData()
    } else {
      // Prefer token from userStore (sessionStorage-backed) to support per-tab login isolation
      const token = userStore.token || sessionStorage.getItem('token') || ''
      if (!token) {
        ElMessage.error('未登录，请重新登录')
        router.push('/login')
        return
      }

      // Include the current user's id in request params to enforce user-scoped list on backend
      const params = {
        keyword: searchKeyword.value.trim(),
        serviceType: serviceType.value,
        pageNum: currentPage.value,
        pageSize: pageSize.value,
        userId: currentUserId.value // <-- added
      }

      const res = await axios.get('/api/need/my-list', {
        params,
        headers: { Authorization: `Bearer ${token}` }
      })

      if (res.data?.code !== 200) {
        throw new Error(res.data?.msg || '获取需求失败')
      }
      const data = res.data.data || {}

      // Helper to extract owner id from various possible shapes
      const getOwnerId = (need) => {
        return need.userId ?? need.user_id ?? need.ownerId ?? need.owner_id ?? (need.user && (need.user.userId ?? need.user.id)) ?? null
      }

      // If backend returned no records for current page but total > 0, it means currentPage is out-of-range (e.g., someone else created/removed items)
      if ((data.records || []).length === 0 && (data.total || 0) > 0 && currentPage.value > 1) {
        // reset to first page and fetch again to ensure owner sees their items
        currentPage.value = 1
        const retryRes = await axios.get('/api/need/my-list', {
          params: { ...params, pageNum: currentPage.value },
          headers: { Authorization: `Bearer ${token}` }
        })
        if (retryRes.data?.code !== 200) throw new Error(retryRes.data?.msg || '获取需求失败')
        const retryData = retryRes.data.data || {}
        myAllNeeds.value = (retryData.records || [])
          .map(need => {
            let rawId = need.needId ?? need.id ?? need.need_id ?? null
            if (typeof rawId === 'string' && rawId.startsWith('need_')) rawId = Number(rawId.replace('need_', ''))
            const idNum = Number(rawId)
            return {
              ...need,
              needId: Number.isFinite(idNum) && !Number.isNaN(idNum) ? idNum : rawId,
              status: Number(need.status),
              hasResponse: Boolean(need.hasResponse) || false,
              hasAccepted: Boolean(need.hasAccepted) || false
            }
          })
          // defensive filter: ensure only current user's needs are shown
          .filter(need => {
            const owner = String(getOwnerId(need) ?? '')
            return owner === String(currentUserId.value)
          })
        filteredNeeds.value = [...myAllNeeds.value]
        total.value = retryData.total || 0
      } else {
        myAllNeeds.value = (data.records || [])
          .map(need => {
            // Normalize various possible id fields into a numeric needId when possible.
            let rawId = need.needId ?? need.id ?? need.need_id ?? null
            if (typeof rawId === 'string' && rawId.startsWith('need_')) {
              rawId = Number(rawId.replace('need_', ''))
            }
            const idNum = Number(rawId)
            return {
              ...need,
              needId: Number.isFinite(idNum) && !Number.isNaN(idNum) ? idNum : rawId,
              status: Number(need.status),
              hasResponse: Boolean(need.hasResponse) || false,
              hasAccepted: Boolean(need.hasAccepted) || false
            }
          })
          // defensive filter: ensure only current user's needs are shown
          .filter(need => {
            const owner = String(getOwnerId(need) ?? '')
            return owner === String(currentUserId.value)
          })

        filteredNeeds.value = [...myAllNeeds.value]
        total.value = data.total || 0
      }
    }
  } catch (error) {
    const errMsg = isMock.value
      ? `本地加载失败：${error.message}`
      : `接口请求失败：${error.message}`
    ElMessage.error(errMsg)
    console.error('获取需求列表异常：', error)
    myAllNeeds.value = []
    filteredNeeds.value = []
    total.value = 0
  } finally {
    isLoading.value = false
  }
}

/**
 * 搜索按钮触发（重置页码+重新筛选）
 */
const searchNeed = () => {
  currentPage.value = 1 // 搜索后回到第一页
  filterData()
}

/**
 * 重置筛选条件
 */
const resetSearch = () => {
  searchKeyword.value = ''
  serviceType.value = ''
  currentPage.value = 1
  filterData()
}

/**
 * 删除需求（双模式）
 * @param {string} needId - 需求ID
 */
const deleteNeed = async (needId) => {
  const need = myAllNeeds.value.find(item => item.needId === needId)
  if (!need) {
    ElMessage.error('需求不存在')
    return
  }
  if (!canOperate(need)) {
    ElMessage.warning('已取消/有响应的需求不可删除')
    return
  }

  ElMessageBox.confirm(
    '确定删除该需求？删除后无法恢复',
    '删除确认',
    { type: 'warning', confirmButtonText: '确认删除', cancelButtonText: '取消' }
  ).then(async () => {
    const loading = ElLoading.service({ text: '删除中...' })
    try {
      if (isMock.value) {
        myAllNeeds.value = myAllNeeds.value.filter(item => item.needId !== needId)
        const stored = localStorage.getItem('mockNeedList')
        const allNeeds = stored ? JSON.parse(stored) : []
        const newAllNeeds = allNeeds.filter(item => item.needId !== needId)
        localStorage.setItem('mockNeedList', JSON.stringify(newAllNeeds))
        // 重新筛选
        filterData()
        ElMessage.success('删除成功（Mock模式）')
      } else {
        // 后端
        const token = userStore.token || sessionStorage.getItem('token') || ''
        const res = await axios.delete(`/api/need/${needId}`, {
          headers: { Authorization: `Bearer ${token}` }
        })
        if (res.data?.code !== 200) {
          throw new Error(res.data?.msg || '删除失败')
        }
        // 重新获取数据
        await fetchMyNeeds()
        ElMessage.success('删除成功（后端模式）')
      }
    } catch (error) {
      ElMessage.error(`删除失败：${error.message}`)
      console.error('删除需求异常：', error)
    } finally {
      loading.close()
    }
  }).catch(() => {
    ElMessage.info('已取消删除')
  })
}

// 分页
const handlePageChange = (page) => {
  currentPage.value = page
  // 滚动到表格顶部（优化体验）
  document.querySelector('.el-table')?.scrollTo(0, 0)
}

const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1 // 切换每页条数后回到第一页
}

// 页面跳转
const goToAddNeed = () => {
  router.push('/need/form')
}

const goToNeedDetail = (needId) => {
  // basic validation to avoid routing with invalid IDs (e.g. undefined or non-numeric)
  if (needId === undefined || needId === null || String(needId).trim() === '') {
    ElMessage.error('无效的需求ID，无法跳转详情')
    return
  }
  const idNum = Number(needId)
  if (!Number.isInteger(idNum) || idNum <= 0) {
    ElMessage.error('需求ID格式不正确')
    return
  }
  router.push(`/need/detail/${idNum}`)
}

const goToEditNeed = (needId) => {
  // reuse same validation
  if (needId === undefined || needId === null || String(needId).trim() === '') {
    ElMessage.error('无效的需求ID，无法跳转编辑')
    return
  }
  const idNum = Number(needId)
  if (!Number.isInteger(idNum) || idNum <= 0) {
    ElMessage.error('需求ID格式不正确')
    return
  }
  router.push(`/need/form/${idNum}`)
}

onMounted(async () => {
  // 如果 store 中没有 userId，但有 token，尝试用 token 拉取用户信息（避免 token 存在但 user 丢失导致页面报错/跳转）
  if ((!userStore.userInfo || !userStore.userInfo.userId) && userStore.token) {
    try {
      // 尝试调用后端 me 接口
      const base = 'http://127.0.0.1:8000'
      const res = await axios.get(`${base}/api/user/me`, {
        headers: { Authorization: `Bearer ${userStore.token}` }
      })
      const fetched = res.data?.data || res.data || null
      if (fetched) {
        // 标准化 id
        if (!fetched.userId && fetched.id) fetched.userId = fetched.id
        userStore.setLoginSuccess(userStore.token, fetched)
      }
    } catch (e) {
      // 无法获取用户信息：清理并跳回登录
      console.warn('Use token to fetch /api/user/me failed:', e)
      userStore.logout()
      router.push('/login')
      return
    }
  }

  // 已在路由守卫中调用 initLoginState 并处理未登录跳转，页面不再重复调用以避免冲突
  // 这里保留一个轻量防护：如果 userInfo 不存在则提示并返回（不再强制跳转）
  if (!userStore.userInfo || !userStore.userInfo.userId) {
    ElMessage.error('用户未登录或信息丢失，请重新登录')
    // 如没有 user info，则强制跳转到登录页
    router.push('/login')
    return
  }

  //设置当前用户ID
  currentUserId.value = userStore.userInfo.userId || ''
  if (!currentUserId.value) {
    ElMessage.error('用户信息异常，请重新登录')
    router.push('/login')
    return
  }
  //加载数据
  await fetchMyNeeds()
})
</script>

<style scoped>

.need-list-container {
  width: 100%;
  min-height: 100vh;
  padding: 20px;
  background-color: #BFD7EA;
  box-sizing: border-box;
}

/* 卡片 */
.need-list-card {
  width: 100%;
  max-width: 1400px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06) !important;
  border-radius: 12px !important;
  border: none !important;
  background-color: #FFFFFF !important;
}

/* 标题 */
.need-list-title {
  text-align: center;
  margin-bottom: 24px;
  color: #9A7B68;
  font-weight: 500;
  font-size: 20px;
  letter-spacing: 0.5px;
}

/* 搜索栏 */
.search-bar {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 20px;
}

.btn-group {
  display: flex;
  gap: 10px;
}

/* 按钮 */
.search-btn, .add-btn {
  background-color: #9A7B68 !important;
  border-color: #9A7B68 !important;
  border-radius: 8px !important;
  font-size: 14px;
  padding: 8px 16px;
}
.search-btn:hover, .add-btn:hover {
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

/* 表格 */
:deep(.el-table) {
  --el-table-border-color: #D9CFB8 !important;
  --el-table-row-hover-bg-color: #F8F6F0 !important;
  border: 1px solid #D9CFB8 !important;
  border-radius: 8px !important;
  overflow: hidden !important;
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

/* 需求主题文本 */
.title-text {
  display: inline-block;
  width: 100%;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 状态标签 */
.status-responded {
  background-color: #F5F3FF !important;
  color: #8B5CF6 !important;
  border: none !important;
}

.status-published {
  background-color: #E8F4F8 !important;
  color: #4299E1 !important;
  border: none !important;
}

.status-canceled {
  background-color: #FDF2F8 !important;
  color: #E53E3E !important;
  border: none !important;
}

/* 操作按钮 */
.operate-btn {
  color: #9A7B68 !important;
  font-size: 14px;
  margin: 0 4px;
}

.view-btn:hover {
  color: #6A994E !important;
}

.edit-btn:hover {
  color: #4299E1 !important;
}

.delete-btn:hover {
  color: #E53E3E !important;
}

/* 分页样式 */
:deep(.el-pagination) {
  --el-pagination-button-color: #9A7B68 !important;
  --el-pagination-button-hover-color: #8A6B58 !important;
  --el-pagination-current-page-bg-color: #9A7B68 !important;
  --el-pagination-current-page-color: #FFFFFF !important;
}
</style>