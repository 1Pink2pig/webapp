<template>
  <div v-if="!$route.meta.noAuth && userStore.isLogin && !$route.meta.requireAdmin" class="app-container">
    <!-- 顶部导航栏 -->
    <header class="app-header">
      <div class="header-title">好服务系统</div>
      <div class="header-user">
        <div class="user-avatar-btn" @click="goToPersonal">
          <el-avatar :size="36" src="https://cube.elemecdn.com/9/c2/f0ee8a3c7c9638a5494058f6881c260jpeg.jpeg" class="avatar"></el-avatar>
          <span class="username">我的</span>
        </div>
        <el-button type="text" @click="handleLogout" class="logout-btn">退出</el-button>
      </div>
    </header>

    <!-- 主体布局 -->
    <div class="app-main">
      <!-- 左侧侧边栏 -->
      <aside class="app-sidebar">
        <el-menu
          :default-active="$route.name"
          class="sidebar-menu"
          @select="handleMenuSelect"
          unique-opened
          style="height: 100%; overflow-y: auto;"
        >
          <el-menu-item index="Home">
            <el-icon class="menu-icon"><House /></el-icon>
            <span class="menu-text">首页</span>
          </el-menu-item>
          <el-menu-item index="UserDetail">
            <el-icon class="menu-icon"><User /></el-icon>
            <span class="menu-text">个人信息</span>
          </el-menu-item>
          <el-menu-item index="NeedList">
            <el-icon class="menu-icon"><List /></el-icon>
            <span class="menu-text">我需要列表</span>
          </el-menu-item>
          <el-sub-menu index="MyService">
            <template #title>
              <el-icon class="menu-icon"><Service /></el-icon>
              <span class="menu-text">我服务列表</span>
            </template>
            <el-menu-item index="MyServiceList">
              <span class="sub-menu-text">需求列表</span>
            </el-menu-item>
            <el-menu-item index="ServiceList">
              <span class="sub-menu-text">我的服务</span>
            </el-menu-item>
          </el-sub-menu>
        </el-menu>
      </aside>

      <!-- 主内容区 -->
      <main class="content-wrap">
        <div class="content-card">
          <router-view></router-view>
        </div>
      </main>
    </div>

    <!-- 右下角当前时间 -->
    <div class="current-time">{{ nowTime }}</div>
  </div>

  <!-- 登录/注册页 -->
  <router-view v-else></router-view>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/store/userStore'
import { ElMessage, ElMessageBox } from 'element-plus'
import { House, User, List, Service } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

// 实时更新当前时间
const nowTime = ref('')
let timer = null
const formatTime = () => {
  const date = new Date()
  nowTime.value = date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false
  })
}

onMounted(() => {
  formatTime()
  timer = setInterval(formatTime, 1000)
  if (!route.meta.noAuth) {
    userStore.initLoginState()
  }
})

onUnmounted(() => {
  clearInterval(timer)
})

// 侧边栏菜单跳转
const handleMenuSelect = (index) => {
  const routeConfig = index === 'UserDetail'
    ? { name: index, params: { id: userStore.userInfo?.id || 1 } }
    : { name: index }

  router.push(routeConfig).catch(err => {
    if (err.name !== 'NavigationDuplicated') {
      ElMessage.error('页面不存在')
      console.error('路由跳转错误：', err)
    }
  })
}

// 头像点击跳转个人信息
const goToPersonal = () => {
  if (!userStore.isLogin) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }
  const userId = userStore.userInfo?.id || 1
  router.push({
    name: 'UserDetail',
    params: { id: userId }
  }).catch(err => {
    if (err.name !== 'NavigationDuplicated') {
      ElMessage.error('跳转个人信息失败，请检查路由配置或用户ID')
      console.error('个人信息跳转错误：', err)
    }
  })
}

// 退出登录逻辑
const handleLogout = async () => {
  try {
    const result = await ElMessageBox.confirm(
      '确定要退出登录吗？',
      '退出确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'info'
      }
    )

    if (result === 'confirm') {
      userStore.$reset()
      localStorage.clear()
      sessionStorage.clear()
      await router.replace({ path: '/login' })
      window.location.reload()
      ElMessage.success('退出登录成功')
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('退出登录失败，请重试')
      console.error('退出登录错误：', error)
    }
  }
}
</script>

<style scoped>
* {
  font-family: 'Inter', 'PingFang SC', 'Microsoft YaHei', sans-serif;
  letter-spacing: 0.2px;
  box-sizing: border-box;
}

/* 通用容器 */
.app-container {
  width: 100%;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #F7F8FA;
}

/* 顶部导航 */
.app-header {
  height: 64px;
  background-color: #FFFFFF;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
  padding: 0 32px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-title {
  font-size: 20px;
  font-weight: 500;
  color: #2D3748;
  letter-spacing: 0.5px;
}

.header-user {
  display: flex;
  align-items: center;
  gap: 24px;
}

.user-avatar-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  border-radius: 24px;
  cursor: pointer;
  transition: all 0.2s ease-in-out;
}

.user-avatar-btn:hover {
  background-color: #F0F2F5;
}

.avatar {
  border: 1px solid #F0F2F5;
}

.username {
  font-size: 14px;
  color: #4A5568;
  font-weight: 400;
  white-space: nowrap;
}

.logout-btn {
  font-size: 14px;
  color: #718096;
  transition: color 0.2s ease;
}

.logout-btn:hover {
  color: #2D3748;
}

/* 主体布局 */
.app-main {
  flex: 1;
  display: flex;
}

/* 侧边栏核心 */
.app-sidebar {
  width: 200px;
  min-height: calc(100vh - 64px);
  background-color: #F5F0E8;
  flex-shrink: 0;
}

.sidebar-menu {
  height: 100%;
  border-right: none !important;
  background-color: transparent !important;
  padding: 8px 0 !important;
}

/* 菜单统一样式 */
:deep(.el-menu-item),
:deep(.el-sub-menu .el-sub-menu__title) {
  margin: 4px 8px !important;
  border-radius: 8px !important;
  height: 80px !important;
  display: flex;
  align-items: center;
  padding-left: 16px !important;
  transition: all 0.2s ease;
}

/* 菜单图标 */
.menu-icon {
  font-size: 18px !important;
  margin-right: 8px !important;
  color: #7A6B58 !important;
  flex-shrink: 0;
}

/* 菜单文字 */
.menu-text {
  font-size: 15px;
  color: #4A5568;
  font-weight: 400;
  white-space: nowrap;
}

.sub-menu-text {
  font-size: 14px;
  color: #4A5568;
  font-weight: 400;
  white-space: nowrap;
}

/* 菜单交互样式 */
:deep(.el-menu-item:hover),
:deep(.el-sub-menu .el-sub-menu__title:hover) {
  background-color: #E8E0D5 !important;
}

:deep(.el-menu-item.is-active) {
  background-color: #EFE6D8 !important;
}

:deep(.el-menu-item.is-active .menu-icon),
:deep(.el-menu-item.is-active .menu-text),
:deep(.el-menu-item.is-active .sub-menu-text),
:deep(.el-menu-item:hover .menu-icon),
:deep(.el-menu-item:hover .menu-text),
:deep(.el-menu-item:hover .sub-menu-text),
:deep(.el-sub-menu .el-sub-menu__title:hover .menu-icon),
:deep(.el-sub-menu .el-sub-menu__title:hover .menu-text) {
  color: #9A7B68 !important;
  font-weight: 500;
}

/* 子菜单样式 */
:deep(.el-sub-menu) {
  margin: 0 !important;
  border-radius: 8px !important;
}

:deep(.el-sub-menu .el-menu) {
  background-color: #F5F0E8 !important;
  padding-left: 8px !important;
  margin-left: 0 !important;
}

:deep(.el-sub-menu .el-menu-item) {
  height: 56px !important;
  margin: 2px 8px !important;
  border-radius: 6px !important;
  padding-left: 24px !important;
}

/* 主内容区 */
.content-wrap {
  flex: 1;
  padding: 24px 32px;
}

.content-card {
  background-color: #FFFFFF;
  border-radius: 12px;
  box-shadow: 0 1px 6px rgba(0, 0, 0, 0.05);
  padding: 24px;
  min-height: calc(100% - 0px);
}

/* 右下角时间 */
.current-time {
  position: fixed;
  right: 32px;
  bottom: 32px;
  padding: 8px 16px;
  background-color: rgba(255, 255, 255, 0.9);
  border-radius: 8px;
  font-size: 12px;
  color: #718096;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
  letter-spacing: 0.2px;
}

/* 色系变量 */
:root {
  --morandi-orange-light: #F5F0E8;
  --morandi-orange-hover: #E8E0D5;
  --morandi-orange-active: #EFE6D8;
  --morandi-text-light: #718096;
  --morandi-text-medium: #4A5568;
  --morandi-text-dark: #2D3748;
  --morandi-bg-light: #F7F8FA;
  --morandi-bg-white: #FFFFFF;
}
</style>