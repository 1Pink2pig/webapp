<template>
  <!-- 加载状态覆盖整个页面 -->
  <div class="user-detail-page" v-loading="isLoading" element-loading-text="加载中...">
    <!-- 独立卡片：用户基本信息 -->
    <el-card class="info-card">
      <h2 class="card-title">用户基本信息</h2>
      <el-table
        :data="userInfoTableData"
        border
        :show-header="false"
        style="width: 100%; margin-bottom: 24px"
      >
        <el-table-column
          prop="label"
          width="120"
          align="right"
          :cell-style="{ background: '#F3E8CE', color: '#4A5568', fontWeight: 400 }"
        />
        <el-table-column
          prop="value"
          align="left"
          :cell-style="{ color: '#2D3748', paddingLeft: '16px' }"
        />
      </el-table>
      <!-- 操作按钮：编辑 + 返回 -->
      <div class="btn-group">
        <el-button
          type="primary"
          @click="goToEditProfile"
          class="edit-btn"
          :disabled="!userStore.isLogin"
        >
          编辑
        </el-button>
        <el-button
          type="primary"
          @click="goBack"
          class="back-btn"
          plain
        >
          返回
        </el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/store/userStore'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const isMock = false

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

// 状态定义
const isLoading = ref(false)          // 加载状态
const loginUserId = ref('')           // 当前登录用户ID
const userInfo = ref({})              // 用户基本信息

// 用户基本信息表格数据
const userInfoTableData = computed(() => [
  { label: '用户名', value: userInfo.value.username || '-' },
  { label: '真实姓名', value: userInfo.value.realName || '-' },
  { label: '用户类型', value: userInfo.value.userType || '普通用户' },
  { label: '注册时间', value: userInfo.value.registerTime || '-' },
  { label: '最后修改时间', value: userInfo.value.updateTime || '-' },
  { label: '用户简介', value: userInfo.value.intro || '暂无简介' },
  { label: '手机号', value: userInfo.value.phone || '-' }
])

// 后端
const apiGetUserDetail = async () => {
  try {
    const response = await axios.get(
      `http://127.0.0.1:8000/api/user/detail/${loginUserId.value}`,
      {
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${userStore.token}` // 携带登录token
        }
      }
    )

    const res = response.data
    if (res.code === 200) {
      return res.data
    } else {
      ElMessage.error(res.msg || '获取用户信息失败')
      return null
    }
  } catch (error) {
    // 错误分类处理
    if (error.response) {
      ElMessage.error(`后端报错：${error.response.data?.msg || '服务器异常'}`)
    } else if (error.request) {
      ElMessage.error('网络错误：无法连接到服务器，请检查网络')
    } else {
      ElMessage.error(`请求错误：${error.message}`)
    }
    console.error('获取用户信息失败：', error)
    return null
  }
}

// 初始化用户信息
const initUserInfo = async () => {
  try {
    isLoading.value = true

    //检查是否有 Token (最基础的登录凭证)
    // 如果 store 里没有，尝试从 localStorage 拿一次兜底
    const token = userStore.token || localStorage.getItem('token')

    if (!token && !isMock) {
      ElMessage.warning('请先登录')
      router.push('/login')
      return
    }

    // 有 Token 但没 ID，去后端拉取个人信息
    if (!isMock && (!userStore.userInfo?.id && !userStore.userInfo?.userId)) {
      try {
        console.log('检测到用户信息缺失，正在尝试重新获取...')
        const meRes = await axios.get('http://127.0.0.1:8000/api/user/me', {
          headers: { Authorization: `Bearer ${token}` }
        })
        if (meRes.data) {
          // 成功救回！更新 Store 和 本地缓存
          userStore.userInfo = meRes.data
          localStorage.setItem('user', JSON.stringify(meRes.data))
        }
      } catch (err) {
        console.error('自动获取个人信息失败', err)
        // 救不回来了，确实得重新登录
        userStore.logout()
        router.push('/login')
        return
      }
    }

    //获取当前登录用户ID
    loginUserId.value = userStore.userInfo?.id || userStore.userInfo?.userId || ''

    if (!loginUserId.value) {
      ElMessage.error('登录信息异常，请重新登录')
      router.push('/login')
      return
    }

    //路由参数校验（防止访问他人信息）
    const routeUserId = route.params.id
    if (routeUserId && String(routeUserId) !== String(loginUserId.value)) {
       ElMessage.warning('仅可查看自己的个人信息，已自动跳转')
       await router.replace(`/user-detail/${loginUserId.value}`)
       // 注意：跳转后会重新触发路由守卫或生命周期，这里return即可
       return
    }

    let userData = null

    if (isMock) {
      userData = userStore.getUserById(loginUserId.value)
    } else {
      // 后端请求
      userData = await apiGetUserDetail()
    }

    //数据赋值
    if (userData) {
      userInfo.value = userData
    } else {
      // 兜底显示
      userInfo.value = userStore.userInfo || {}
    }

  } catch (error) {
    ElMessage.error('加载个人信息失败')
    console.error('初始化错误：', error)
  } finally {
    isLoading.value = false
  }
}

// 跳转到编辑个人信息页面
const goToEditProfile = () => {
  router.push({
    path: '/edit-profile',
    query: { userId: loginUserId.value }
  }).catch(err => {
    if (err.name !== 'NavigationDuplicated') {
      ElMessage.error('跳转编辑页面失败，请重试')
      console.error('编辑页面跳转错误：', err)
    }
  })
}

// 返回上一页
const goBack = () => {
  if (window.history.length > 1) {
    router.back()
  } else {
    router.push('/')
  }
}

onMounted(() => {
  initUserInfo()
})
</script>

<style scoped>

.user-detail-page {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 24px;
  background-color: #BFD7EA;
  min-height: 100vh;
  padding: 20px;
  align-items: center;
}

/* 通用卡片样式 */
:deep(.el-card) {
  box-shadow: 0 1px 6px rgba(0, 0, 0, 0.05) !important;
  border-radius: 12px !important;
  border: none !important;
  background-color: #FFFFFF !important;
}

/* 用户基本信息卡片 */
.info-card {
  width: 80%;
  padding: 20px;
}

/* 卡片标题 */
.card-title {
  text-align: center;
  color: #9A7B68; /* 莫兰迪深橙色 */
  font-weight: 500;
  font-size: 20px;
  margin-bottom: 20px;
  letter-spacing: 0.3px;
}

/* 表格样式 */
:deep(.el-table) {
  --el-table-border-color: #F5F0E8 !important; /* 表格边框色和原风格统一 */
  --el-table-row-hover-bg-color: #F8F6F0 !important; /* 行悬浮背景 */
}
:deep(.el-table td) {
  border-bottom: 1px solid #F5F0E8 !important;
  padding: 12px 8px !important;
}
:deep(.el-table th) {
  border-bottom: 1px solid #F5F0E8 !important;
}

/* 按钮组 */
.btn-group {
  display: flex;
  gap: 20px;
  justify-content: center;
  margin-top: 8px;
}

/* 编辑按钮 */
.edit-btn {
  width: 140px;
  height: 40px;
  background-color: #9A7B68 !important; /* 莫兰迪深橙色 */
  border-color: #9A7B68 !important;
  border-radius: 8px !important;
  font-size: 14px;
  transition: all 0.2s ease !important;
}

.edit-btn:hover {
  background-color: #8A6B58 !important;
  border-color: #8A6B58 !important;
}

/* 返回按钮 */
.back-btn {
  width: 140px;
  height: 40px;
  color: #9A7B68 !important;
  border-color: #9A7B68 !important;
  border-radius: 8px !important;
  font-size: 14px;
  transition: all 0.2s ease !important;
}

.back-btn:hover {
  background-color: #F5F0E8 !important;
  color: #8A6B58 !important;
  border-color: #8A6B58 !important;
}

/* 加载状态 */
:deep(.el-loading-mask) {
  background-color: rgba(255, 255, 255, 0.9) !important;
  border-radius: 12px !important;
  z-index: 999 !important;
}

:deep(.el-loading-text) {
  color: #9A7B68 !important;
  font-size: 14px !important;
}
</style>