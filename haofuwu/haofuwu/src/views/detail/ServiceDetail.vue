<template>
  <div class="service-detail-container" v-loading="isLoading" element-loading-text="加载详情中...">
    <!-- 详情卡片 -->
    <el-card class="service-detail-card">
      <!-- 头部：标题 + 返回按钮 -->
      <div class="detail-header">
        <h2 class="detail-title">服务自荐详情</h2>
        <el-button
          type="primary"
          icon="el-icon-arrow-left"
          @click="goBack"
          class="back-btn"
        >
          返回列表
        </el-button>
      </div>

      <div class="detail-content" v-if="serviceDetail">
        <!-- 服务人ID：显示服务自荐人的用户名 -->
        <div class="detail-row">
          <div class="detail-label">服务人ID：</div>
          <div class="detail-value">{{ servicePublisher.username || '未知用户' }}</div>
        </div>

        <!-- 服务类型 -->
        <div class="detail-row">
          <div class="detail-label">服务类型：</div>
          <div class="detail-value">{{ serviceDetail.serviceType || '无' }}</div>
        </div>

        <!-- 需求主题 -->
        <div class="detail-row">
          <div class="detail-label">需求主题：</div>
          <div class="detail-value">{{ matchedNeed.title || '无关联需求' }}</div>
        </div>

        <!-- 服务自荐主题 -->
        <div class="detail-row">
          <div class="detail-label">自荐主题：</div>
          <div class="detail-value">{{ serviceDetail.title || '无' }}</div>
        </div>

        <!-- 自荐内容 -->
        <div class="detail-row">
          <div class="detail-label">自荐内容：</div>
          <div class="detail-value content-value">{{ serviceDetail.content || '无' }}</div>
        </div>

        <!-- 需求发布人 -->
        <div class="detail-row">
          <div class="detail-label">需求发布人：</div>
          <div class="detail-value">{{ needPublisher.username || '未知用户' }}</div>
        </div>

        <div class="detail-row">
          <div class="detail-label">提交时间：</div>
          <div class="detail-value">{{ formatTime(serviceDetail.createTime) || '无' }}</div>
        </div>

        <div class="detail-row">
          <div class="detail-label">更新时间：</div>
          <div class="detail-value">{{ formatTime(serviceDetail.updateTime) || '无' }}</div>
        </div>

        <!-- 服务状态：三种状态 -->
        <div class="detail-row">
          <div class="detail-label">服务状态：</div>
          <div class="detail-value">
            <el-tag
              :type="getStatusTagType(serviceDetail.status)"
              class="status-tag"
            >
              {{ getStatusText(serviceDetail.status) }}
            </el-tag>
          </div>
        </div>

        <!-- 上传文件预览 -->
        <div class="detail-row" v-if="serviceDetail.files && serviceDetail.files.length > 0">
          <div class="detail-label">证明文件：</div>
          <div class="detail-value file-container">
            <div
              class="file-item"
              v-for="(file, index) in serviceDetail.files"
              :key="index"
            >
              <div class="file-name">{{ file.name || `文件${index+1}` }}</div>
              <template v-if="file.url.includes('image')">
                <img :src="file.url" alt="证明图片" class="preview-img" @click="openPreview(file.url, 'image')" style="cursor: pointer;">
              </template>
              <template v-else-if="file.url.includes('video')">
                <video :src="file.url" controls class="preview-video" @click="openPreview(file.url, 'video')" style="cursor: pointer;"></video>
              </template>
              <template v-else>
                <div class="other-file">不支持预览的文件</div>
              </template>
            </div>
          </div>
        </div>
      </div>

      <!-- 空数据/加载失败提示 -->
      <div class="empty-tip" v-else>
        暂无该服务的详情信息
      </div>
    </el-card>

    <!-- 预览对话框 -->
    <el-dialog v-model="previewVisible" title="附件预览" width="80%" append-to-body>
      <template v-if="previewType === 'image'">
        <el-image :src="previewFile.url" fit="contain" style="width:100%; height:70vh; background:#000"></el-image>
      </template>
      <template v-else-if="previewType === 'video'">
        <video :src="previewFile.url" controls style="width:100%; max-height:70vh"></video>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
/* eslint-disable no-undef */
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/store/userStore'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const isMock = false

const props = defineProps({
  id: {
    type: [String, Number],
    required: true,
    default: ''
  }
})

// --- normalize incoming id to numeric service id ---
const normalizeId = (v) => {
  if (v === null || v === undefined || v === '') return null
  if (typeof v === 'number') return Number(v)
  const s = String(v)
  // accept 'service_123' or '123'
  const m = s.match(/(\d+)/)
  return m ? Number(m[1]) : null
}

const resolvedServiceId = normalizeId(props.id)

// 初始化
const router = useRouter()
const userStore = useUserStore()
const isLoading = ref(false)
const serviceDetail = ref(null)
const matchedNeed = ref({})

// 服务自荐人
// replace computed (which used mock store) with refs populated from backend
const servicePublisher = ref({})

// 需求发布人
const needPublisher = ref({})

// 调试
console.log('接收的原始服务ID：', props.id)
console.log('解析后的服务ID（数字）：', resolvedServiceId)
console.log('全局服务自荐列表：', userStore.serviceSelfList)
console.log('全局需求列表：', userStore.needList)

// 格式化时间
const formatTime = (timeStr) => {
  if (!timeStr) return ''
  try {
    const date = new Date(timeStr)
    return `${date.getFullYear()}-${(date.getMonth()+1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')} ${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}:${date.getSeconds().toString().padStart(2, '0')}`
  } catch (e) {
    return timeStr
  }
}

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

const matchNeedDirectly = (needId) => {
  if (!needId) {
    console.log('服务自荐无关联的needId')
    return {}
  }
  const needList = userStore.needList || []
  const need = needList.find(item => String(item.needId) === String(needId))
  if (need) {
    console.log(`成功匹配需求：needId=${needId}，需求标题=${need.title}`)
    return need
  } else {
    console.warn(`未找到匹配的需求：needId=${needId}，请检查needId格式是否与需求列表一致`)
    console.log('需求列表中存在的needId：', needList.map(item => item.needId))
    return {}
  }
}

const getMockServiceDetail = () => {
  const serviceList = userStore.serviceSelfList || []
  if (resolvedServiceId === null) {
    serviceDetail.value = null
    matchedNeed.value = {}
    ElMessage.warning(`服务ID格式不正确：${props.id}`)
    return
  }

  const service = serviceList.find(item => {
    // normalize stored serviceId which might be 'service_1' or numeric
    const sid = item.serviceId ?? item.id ?? item.service_id
    const parsed = normalizeId(sid)
    return parsed === resolvedServiceId
  })

  if (service) {
    serviceDetail.value = {
      serviceId: resolvedServiceId,
      needId: normalizeId(service.needId ?? service.need_id),
      serviceType: service.serviceType || service.service_type || '',
      title: service.title || '',
      content: service.content || '',
      userId: service.userId || service.user_id || '',
      createTime: service.createTime || new Date().toISOString(),
      updateTime: service.updateTime || new Date().toISOString(),
      status: Number(service.status ?? 0),
      files: service.files || []
    }
    matchedNeed.value = matchNeedDirectly(serviceDetail.value.needId)
    console.log('最终匹配结果（mock）：', {
      serviceDetail: serviceDetail.value,
      matchedNeed: matchedNeed.value
    })
  } else {
    serviceDetail.value = null
    matchedNeed.value = {}
    ElMessage.warning(`未找到ID为【${props.id}】的服务详情（本地mock）`)
  }
}

/**
 * 后端
 */
const getApiServiceDetail = async () => {
  try {
    if (resolvedServiceId === null) {
      ElMessage.error('服务ID无效，无法请求详情')
      serviceDetail.value = null
      matchedNeed.value = {}
      return
    }

    isLoading.value = true
    //获取服务详情（使用解析后的数字 id）
    const serviceRes = await axios.get(`/api/service/detail/${resolvedServiceId}`, {
      headers: { Authorization: `Bearer ${userStore.token || sessionStorage.getItem('token') || ''}` }
    })
    if (serviceRes.data.code !== 200) {
      serviceDetail.value = null
      matchedNeed.value = {}
      ElMessage.error(serviceRes.data.msg || '获取服务详情失败')
      return
    }

    // normalize backend response to frontend-friendly fields
    const raw = serviceRes.data.data || {}
    serviceDetail.value = {
      serviceId: normalizeId(raw.id ?? raw.serviceId),
      needId: normalizeId(raw.needId ?? raw.need_id),
      serviceType: raw.serviceType ?? raw.service_type,
      title: raw.title,
      content: raw.content,
      userId: raw.userId ?? raw.user_id,
      createTime: raw.createTime ?? raw.create_time,
      updateTime: raw.updateTime ?? raw.update_time,
      status: Number(raw.status ?? 0),
      files: raw.files || [],
      // accept backend-provided userName if present
      userName: raw.userName ?? raw.user_name ?? ''
    }

    // populate service publisher: prefer backend's userName, otherwise fetch by userId
    if (serviceDetail.value && serviceDetail.value.userName) {
      servicePublisher.value = { username: serviceDetail.value.userName }
    } else if (serviceDetail.value && serviceDetail.value.userId) {
      try {
        const u = await fetchUserById(serviceDetail.value.userId)
        servicePublisher.value = u || {}
      } catch (e) {
        servicePublisher.value = {}
      }
    } else {
      servicePublisher.value = {}
    }

    if (serviceDetail.value.needId) {
      const needRes = await axios.get(`/api/need/detail/${serviceDetail.value.needId}`, {
        headers: { Authorization: `Bearer ${userStore.token || sessionStorage.getItem('token') || ''}` }
      })
      if (needRes.data.code === 200) {
        matchedNeed.value = needRes.data.data
        // populate need publisher: prefer backend's userName, otherwise fetch
        try {
          const needUserName = matchedNeed.value.userName || matchedNeed.value.username || matchedNeed.value.user_name
          if (needUserName) {
            needPublisher.value = { username: needUserName }
          } else {
            const needUserId = matchedNeed.value.userId ?? matchedNeed.value.user_id
            if (needUserId) {
              const needUser = await fetchUserById(needUserId)
              needPublisher.value = needUser || {}
            } else {
              needPublisher.value = {}
            }
          }
        } catch (e) {
          needPublisher.value = {}
        }
        console.log('后端模式匹配需求成功：', matchedNeed.value)
      } else {
        matchedNeed.value = {}
        needPublisher.value = {}
        ElMessage.warning(`未找到ID为【${serviceDetail.value.needId}】的需求`)
      }
    } else {
      matchedNeed.value = {}
      needPublisher.value = {}
      ElMessage.warning('该服务自荐未关联任何需求')
    }
  } catch (error) {
    serviceDetail.value = null
    matchedNeed.value = {}
    ElMessage.error('网络错误，无法获取服务详情')
    console.error('获取服务详情失败：', error)
  } finally {
    isLoading.value = false
  }
}

// 统一获取服务详情
const getServiceDetail = async () => {
  isLoading.value = true
  try {
    if (isMock) {
      getMockServiceDetail()
    } else {
      await getApiServiceDetail()
    }
  } catch (e) {
    serviceDetail.value = null
    matchedNeed.value = {}
    ElMessage.error('加载详情失败：' + e.message)
  } finally {
    isLoading.value = false
  }
}

// 页面挂载
onMounted(async () => {
  userStore.initLoginState()

  if (!props.id) {
    ElMessage.error('服务ID为空，无法查看详情')
    serviceDetail.value = null
    matchedNeed.value = {}
    isLoading.value = false
    return
  }

  await getServiceDetail()
})

// 返回上一页
const goBack = () => {
  router.back()
}

// 根据用户ID获取用户信息（后端接口）
const fetchUserById = async (userId) => {
  if (!userId) return null
  const idNum = normalizeToNumberId(userId)
  if (!idNum) return null

  try {
    const baseUrl = process.env.VUE_APP_API_BASE_URL || 'http://127.0.0.1:8000'
    const res = await axios.get(`${baseUrl}/api/user/detail/${idNum}`, {
      headers: { Authorization: `Bearer ${userStore.token || sessionStorage.getItem('token') || ''}` }
    })
    if (res && res.data && res.data.code === 200 && res.data.data) {
      return res.data.data
    }
  } catch (e) {
    console.warn('fetchUserById backend lookup failed:', e && e.message)
  }

  // Do NOT fallback to local mock store; return null to indicate backend unavailable
  return null
}

// 预览相关
const previewVisible = ref(false)
const previewFile = ref({ url: '' })
const previewType = ref('')

const openPreview = (url, type = 'image') => {
  previewFile.value = { url }
  previewType.value = type
  previewVisible.value = true
}
</script>

<style scoped>
/* 页面容器 */
.service-detail-container {
  width: 100%;
  min-height: 100vh;
  padding: 20px;
  background-color: #BFD7EA;
  display: flex;
  justify-content: center;
  align-items: flex-start;
  overflow: auto;
}

/* 卡片样式 */
.service-detail-card {
  width: 90%;
  max-width: 1000px;
  padding: 30px;
  box-shadow: 0 1px 6px rgba(0, 0, 0, 0.05) !important;
  border-radius: 12px !important;
  border: none !important;
  background-color: #FFFFFF !important;
  min-height: 500px;
}

/* 头部样式 */
.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 15px;
  border-bottom: 1px solid #D9CFB8;
}

.detail-title {
  color: #9A7B68;
  font-weight: 500;
  font-size: 20px;
  letter-spacing: 0.3px;
  margin: 0;
}

.back-btn {
  background-color: #9A7B68 !important;
  border-color: #9A7B68 !important;
  border-radius: 8px !important;
  font-size: 14px;
  padding: 8px 16px;
}
.back-btn:hover {
  background-color: #8A6B58 !important;
  border-color: #8A6B58 !important;
}

/* 详情内容布局 */
.detail-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.detail-row {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
  gap: 10px;
}

.detail-label {
  width: 120px;
  font-weight: 500;
  color: #4A5568;
  flex-shrink: 0;
}

.detail-value {
  flex: 1;
  color: #666;
  line-height: 1.6;
}

/* 内容字段 */
.content-value {
  white-space: pre-wrap;
  word-break: break-all;
  background-color: #F8F6F0;
  padding: 10px 15px;
  border-radius: 8px;
  border: 1px solid #D9CFB8;
}

/* 状态标签 */
.status-tag {
  border: none !important;
}
:deep(.el-tag--warning) {
  background-color: #F3E8CE !important;
  color: #9A7B68 !important;
}
:deep(.el-tag--success) {
  background-color: #E8F5E9 !important;
  color: #4CAF50 !important;
}
:deep(.el-tag--danger) {
  background-color: #FFEBEE !important;
  color: #F44336 !important;
}

/* 文件预览容器 */
.file-container {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  padding: 10px 0;
}

.file-item {
  width: 200px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.file-name {
  font-size: 14px;
  color: #9A7B68;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.preview-img {
  width: 100%;
  height: 150px;
  object-fit: cover;
  border-radius: 8px;
  border: 1px solid #D9CFB8;
}

.preview-video {
  width: 100%;
  height: 150px;
  border-radius: 8px;
  border: 1px solid #D9CFB8;
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

/* 空数据提示 */
.empty-tip {
  text-align: center;
  padding: 60px 0;
  color: #9A7B68;
  font-size: 16px;
  width: 100%;
  height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>