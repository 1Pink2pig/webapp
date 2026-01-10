<template>
  <!-- 加载状态覆盖整个页面 -->
  <div class="need-detail-container" v-loading="isLoading" element-loading-text="加载中...">
    <el-card class="need-detail-card">
      <h2 class="need-detail-title">需求详情</h2>
      <!-- 无数据兜底 -->
      <div v-if="!needInfo.needId" class="empty-tip">
        <el-empty description="暂无需求数据"></el-empty>
      </div>
      <el-descriptions
        v-else
        title="需求基本信息"
        border
        class="need-info-desc"
      >
        <el-descriptions-item label="需求ID" prop="needId">{{ needInfo.needId }}</el-descriptions-item>
        <!-- 发布人显示用户名 -->
        <el-descriptions-item label="发布人" prop="userName">
          <el-button
            type="text"
            @click="goToUserDetail(needInfo.userId)"
            class="user-name-btn"
          >
            {{ needInfo.userName }}
          </el-button>
        </el-descriptions-item>
        <el-descriptions-item label="需求主题" prop="title">{{ needInfo.title }}</el-descriptions-item>
        <el-descriptions-item label="服务类型" prop="serviceType">{{ needInfo.serviceType }}</el-descriptions-item>
        <el-descriptions-item label="服务区域" prop="region">{{ needInfo.region || '未填写' }}</el-descriptions-item>
        <el-descriptions-item label="发布时间" prop="createTime">{{ needInfo.createTime }}</el-descriptions-item>
        <el-descriptions-item label="更新时间" prop="updateTime">{{ needInfo.updateTime }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag
            :type="needInfo.status === '0' ? 'info' : 'danger'"
          >
            {{ needInfo.status === '0' ? '已发布' : '已取消' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="是否有响应" prop="hasResponse">
          <el-tag :type="needInfo.hasResponse ? 'success' : 'info'">
            {{ needInfo.hasResponse ? '有响应' : '无人提供服务' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="需求描述" >
          <div class="description-content">{{ needInfo.description || '暂无描述' }}</div>
        </el-descriptions-item>
      </el-descriptions>

      <!-- 附件展示 -->
      <div class="files-section" v-if="needInfo.imgUrls.length > 0 || needInfo.videoUrl">
        <h3 class="section-title">需求附件</h3>
        <div class="files-list">
          <div
            v-for="(url, index) in needInfo.imgUrls"
            :key="`img-${index}`"
            class="file-item"
          >
            <img :src="url" alt="需求图片" class="file-img">
            <div class="file-name">图片{{ index+1 }}</div>
          </div>
          <div
            v-if="needInfo.videoUrl"
            :key="`video-${needInfo.needId}`"
            class="file-item"
          >
            <video :src="needInfo.videoUrl" controls class="file-video"></video>
            <div class="file-name">需求视频</div>
          </div>
        </div>
      </div>

      <!-- 响应提示 -->
      <div class="response-section" v-if="needInfo.hasResponse">
        <h3 class="section-title">响应状态</h3>
        <el-alert
          title="该需求已有服务者响应，可前往响应列表页查看详情"
          type="info"
          show-icon
        >
          <el-button
            type="text"
            @click="goToResponseList(needInfo.needId)"
            class="response-btn"
          >
            查看响应列表
          </el-button>
        </el-alert>
      </div>

      <!-- 操作按钮 -->
      <div class="btn-group" v-if="needInfo.needId">
        <el-button type="primary" @click="goBack" plain class="back-btn">返回</el-button>
        <el-button
          type="primary"
          @click="goToEditNeed"
          class="edit-btn"
          v-if="isOwner && needInfo.status === '0' && !needInfo.hasResponse"
        >
          编辑需求
        </el-button>
        <el-button
          type="danger"
          @click="deleteNeed"
          class="delete-btn"
          v-if="isOwner && needInfo.status === '0' && !needInfo.hasResponse"
        >
          删除需求
        </el-button>
        <el-button
          type="warning"
          @click="cancelNeed"
          class="cancel-btn"
          v-if="isOwner && needInfo.status === '0'"
        >
          取消需求
        </el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/store/userStore'
import { ElMessage, ElMessageBox, ElEmpty, ElAlert } from 'element-plus'
import axios from 'axios'

// 双模式控制
const isMock = false

// 初始化依赖
const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

// 响应式状态
// const needId = route.params.id || ''
const rawNeedId = route.params.id || ''
// normalize route param: ensure positive integer ID to avoid backend 422
let needId = ''
if (rawNeedId !== null && rawNeedId !== undefined) {
  const parsed = Number(rawNeedId)
  if (!Number.isFinite(parsed) || Number.isNaN(parsed)) {
    needId = ''
  } else {
    // keep integer value
    needId = Number.isInteger(parsed) ? parsed : Math.floor(parsed)
  }
}

const needInfo = ref({
  needId: '',
  userId: '',
  userName: '',
  title: '',
  serviceType: '',
  region: '',
  description: '',
  imgUrls: [],
  videoUrl: '',
  createTime: '',
  updateTime: '',
  status: '0',
  hasResponse: false
})
const isOwner = ref(false)
const isLoading = ref(false)

// 后端
const apiGetNeedDetail = async (needId) => {
  if (!needId) {
    ElMessage.error('需求ID不能为空')
    return null
  }
  try {
    const baseUrl = process.env.VUE_APP_API_BASE_URL || 'http://127.0.0.1:8000'
    const res = await axios.get(`${baseUrl}/api/need/detail/${needId}`, {
      headers: {
        'Authorization': `Bearer ${userStore.userInfo?.token || ''}`,
        'Content-Type': 'application/json'
      },
      timeout: 10000
    })
    if (res.data.code === 200) {
      return res.data.data
    } else {
      ElMessage.error(`获取详情失败：${res.data.msg || '接口返回异常'}`)
      return null
    }
  } catch (error) {
    console.error('获取需求详情接口异常：', error)
    if (error.code === 'ECONNABORTED') {
      ElMessage.error('请求超时：请检查网络或后端服务')
    } else if (error.response) {
      ElMessage.error(`后端报错[${error.response.status}]：${error.response.data?.msg || '服务器异常'}`)
    } else {
      ElMessage.error('获取需求详情失败：网络异常')
    }
    return null
  }
}

const apiDeleteNeed = async (needId) => {
  if (!needId) {
    ElMessage.error('需求ID不能为空')
    return false
  }
  try {
    const baseUrl = process.env.VUE_APP_API_BASE_URL || 'http://127.0.0.1:8000'
    const res = await axios.delete(`${baseUrl}/api/need/${needId}`, {
      headers: {
        'Authorization': `Bearer ${userStore.userInfo?.token || ''}`,
        'Content-Type': 'application/json'
      },
      timeout: 10000
    })
    return res.data.code === 200
  } catch (error) {
    console.error('删除需求接口异常：', error)
    ElMessage.error('删除需求失败：' + (error.response?.data?.msg || '服务器错误'))
    return false
  }
}

const apiCancelNeed = async (needId) => {
  if (!needId) {
    ElMessage.error('需求ID不能为空')
    return false
  }
  try {
    const baseUrl = process.env.VUE_APP_API_BASE_URL || 'http://127.0.0.1:8000'
    const res = await axios.put(`${baseUrl}/api/need/cancel/${needId}`, {}, {
      headers: {
        'Authorization': `Bearer ${userStore.userInfo?.token || ''}`,
        'Content-Type': 'application/json'
      },
      timeout: 10000
    })
    if (res.data.code === 200) {
      return true
    } else {
      ElMessage.error(`取消需求失败：${res.data.msg || '接口返回异常'}`)
      return false
    }
  } catch (error) {
    console.error('取消需求接口异常：', error)
    ElMessage.error('取消需求失败：' + (error.response?.data?.msg || '服务器错误'))
    return false
  }
}

// 加载需求详情
const loadNeedDetail = async () => {
  // 空ID直接返回
  if (!needId) {
    ElMessage.warning('缺少或无效的需求ID')
    return router.push('/login')
  }

  try {
    isLoading.value = true

    // 登录校验
    if (!userStore.isLogin) {
      ElMessage.warning('请先登录后查看需求详情')
      return router.push({
        path: '/login',
        query: { redirect: route.fullPath }
      })
    }

    let needData = null
    if (isMock) {
      // 本地
      needData = userStore.needList.find(item => item.needId === needId)
    } else {
      // 后端 - ensure we send numeric id to backend to prevent 422
      needData = await apiGetNeedDetail(needId)
    }

    // 无数据处理
    if (!needData) {
      ElMessage.warning('需求不存在或已删除')
      return router.push('/login')
    }

    // 补充发布人用户名
    // Prefer backend-provided username. Only use local mock lookup as a fallback.
    if (!needData.userName || String(needData.userName).trim() === '') {
      const publishUser = userStore.getUserById?.(needData.userId) || {}
      needData.userName = publishUser.username || '未知用户'
    }

    // 赋值并判断是否为发布者
    needInfo.value = {
      ...needInfo.value,
      ...needData
    }
    // Normalize types for comparison (string/number)
    isOwner.value = String(userStore.userInfo?.userId) === String(needData.userId)

  } catch (error) {
    console.error('加载需求详情异常：', error)
    if (error.response && error.response.status === 422) {
      ElMessage.error('请求参数错误：无效的需求ID')
      // 跳转回列表页或登录页，避免页面停留在错误状态
      router.push('/login')
    } else {
      ElMessage.error('加载需求详情失败：未知错误')
    }
  } finally {
    isLoading.value = false
  }
}

// 跳转到发布人详情
const goToUserDetail = (userId) => {
  if (!userId) {
    ElMessage.warning('缺少用户ID')
    return
  }
  router.push(`/user-detail/${userId}`).catch(err => {
    console.error('跳转用户详情失败：', err)
    ElMessage.error('跳转失败，请检查路由配置')
  })
}

// 跳转到响应列表
const goToResponseList = (needId) => {
  if (!needId) {
    ElMessage.warning('缺少需求ID')
    return
  }
  // 跳转到响应列表页面，让发布人查看所有响应
  router.push({ name: 'ServiceResponseList', params: { id: needId } }).catch(err => {
    console.error('跳转响应列表失败：', err)
    ElMessage.error('跳转失败，请检查路由配置')
  })
}

// 返回上一页
const goBack = () => {
  if (window.history.length > 1) {
    router.back()
  } else {
    router.push('/login')
  }
}

// 编辑需求
const goToEditNeed = () => {
  if (!needInfo.value.needId) {
    ElMessage.warning('缺少需求ID')
    return
  }
  router.push(`/need/form/${needInfo.value.needId}`).catch(err => {
    console.error('跳转编辑页失败：', err)
    ElMessage.error('跳转失败，请检查路由配置')
  })
}

// 删除需求
const deleteNeed = () => {
  ElMessageBox.confirm(
    '确定删除该需求？删除后无法恢复',
    '删除确认',
    {
      type: 'warning',
      confirmButtonText: '确认删除',
      cancelButtonText: '取消',
      closeOnClickModal: false
    }
  ).then(async () => {
    const isSuccess = isMock
      ? (userStore.deleteNeed?.(needId) || false)
      : await apiDeleteNeed(needId)

    if (isSuccess) {
      ElMessage.success('需求已删除')
      router.push('/login')
    } else {
      ElMessage.error('删除失败：需求已有响应或权限不足')
    }
  }).catch(() => {
    ElMessage.info('已取消删除操作')
  })
}

// 取消需求
const cancelNeed = () => {
  ElMessageBox.confirm(
    '确定取消该需求？取消后将无法恢复发布状态',
    '取消确认',
    {
      type: 'warning',
      confirmButtonText: '确认取消',
      cancelButtonText: '取消',
      closeOnClickModal: false
    }
  ).then(async () => {
    const isSuccess = isMock
      ? (userStore.cancelNeed?.(needId) || false)
      : await apiCancelNeed(needId)

    if (isSuccess) {
      needInfo.value.status = '1'
      ElMessage.success('需求已取消')
    } else {
      ElMessage.error('取消需求失败：权限不足或服务器错误')
    }
  }).catch(() => {
    ElMessage.info('已取消取消操作')
  })
}

onMounted(() => {
  loadNeedDetail()
})
</script>

<style scoped>

.need-detail-container {
  padding: 20px;
  background-color: #BFD7EA;
  min-height: 100vh;
}

.need-detail-card {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
  box-shadow: 0 1px 6px rgba(0, 0, 0, 0.05) !important;
  border-radius: 12px !important;
  border: none !important;
  background-color: #FFFFFF !important;
}

.need-detail-title {
  text-align: center;
  margin-bottom: 20px;
  color: #9A7B68;
  font-weight: 500;
  font-size: 20px;
  letter-spacing: 0.3px;
}

.empty-tip {
  padding: 40px 0;
  text-align: center;
}

/* 描述列表 */
.need-info-desc {
  margin-bottom: 20px;
}
:deep(.el-descriptions-item__label) {
  background-color: #F3E8CE !important;
  color: #4A5568 !important;
  font-weight: 500 !important;
}

:deep(.el-descriptions-item__content) {
  color: #666;
}

/* 发布人按钮 */
.user-name-btn {
  color: #9A7B68 !important;
  padding: 0 !important;
}
.user-name-btn:hover {
  color: #8A6B58 !important;
  text-decoration: underline;
}

/* 附件样式 */
.section-title {
  margin: 20px 0 10px;
  color: #9A7B68;
  font-size: 16px;
  font-weight: 500;
}

.files-list {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  margin-top: 10px;
}

.file-item {
  width: 200px;
  text-align: center;
}

.file-img, .file-video {
  width: 100%;
  height: 150px;
  object-fit: cover;
  border: 1px solid #F5F0E8;
  border-radius: 8px;
}

.file-name {
  margin-top: 5px;
  font-size: 14px;
  color: #666;
}

.other-file {
  width: 100%;
  height: 150px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #F8F6F0;
  border-radius: 8px;
  border: 1px solid #D9CFB8;
  color: #999;
}

/* 响应提示 */
:deep(.el-alert) {
  margin: 10px 0;
  background-color: #F5F9FF !important;
  border: 1px solid #E8F4FD !important;
}
.response-btn {
  color: #9A7B68 !important;
  margin-left: 10px;
}
.response-btn:hover {
  color: #8A6B58 !important;
}

/* 操作按钮 */
.btn-group {
  margin-top: 30px;
  text-align: center;
}

.btn-group .el-button {
  margin: 0 10px;
  border-radius: 8px !important;
  width: 120px;
  height: 40px;
  font-size: 14px;
}

/* 按钮配色 */
.back-btn {
  color: #9A7B68 !important;
  border-color: #9A7B68 !important;
}
.back-btn:hover {
  background-color: #F5F0E8 !important;
}

.edit-btn {
  background-color: #9A7B68 !important;
  border-color: #9A7B68 !important;
}
.edit-btn:hover {
  background-color: #8A6B58 !important;
}

.delete-btn {
  background-color: #E57373 !important;
  border-color: #E57373 !important;
}
.delete-btn:hover {
  background-color: #D32F2F !important;
}

.cancel-btn {
  background-color: #F5A623 !important;
  border-color: #F5A623 !important;
}
.cancel-btn:hover {
  background-color: #F57C00 !important;
}

</style>

