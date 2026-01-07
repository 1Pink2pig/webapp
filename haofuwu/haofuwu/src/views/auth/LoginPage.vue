<template>
  <div class="login-container">
    <el-card class="login-card">
      <h2 class="login-title">好服务系统登录</h2>
      <el-form :model="form" :rules="rules" ref="formRef" label-width="65px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" placeholder="请输入用户名"></el-input>
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input
           v-model="form.password"
           type="password"
           placeholder="请输入密码"
           prefix-icon="Lock"
           show-password
           >
          </el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="submitForm" class="login-btn">登录</el-button>
          <el-link type="primary" @click="goToRegister">没有账号？去注册</el-link>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup name="LoginPage">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/store/userStore'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const isMock = false

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const formRef = ref(null)

// 表单数据
const form = ref({
  username: '',
  password: ''
})

// 表单规则
const rules = ref({
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
})

onMounted(() => {
  userStore.initLoginState()
  if (userStore.isLogin) {
    // 判断是否是系统管理员
    const isAdmin = userStore.userInfo.userType === '系统管理员'
    router.push(isAdmin ? '/admin' : (route.query.redirect || '/need/list'))
  }
})

// 后端
const apiLogin = async () => {
  try {
    const base = 'http://127.0.0.1:8000'

    // 获取 token（OAuth2 密码模式，表单提交）
    const params = new URLSearchParams()
    params.append('username', form.value.username)
    params.append('password', form.value.password)

    const tokenRes = await axios.post(`${base}/api/auth/token`, params, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    })
    const tokenData = tokenRes.data

    // DEBUG
    console.log('login.response', tokenData)

    const accessToken = tokenData?.access_token || tokenData?.data?.access_token || tokenData?.token || tokenData?.data?.token
    if (!accessToken) {
      ElMessage.error('登录失败：未获取到 token')
      return false
    }

    // 临时设置 axios header 以便获取用户信息
    axios.defaults.headers.common['Authorization'] = `Bearer ${accessToken}`

    // 尝试获取当前用户信息（me 接口），优先使用后端返回的 user 数据
    let fetchedUser = null
    try {
      const meRes = await axios.get(`${base}/api/user/me`, {
        headers: { Authorization: `Bearer ${accessToken}` }
      })
      // 后端可能返回 { code:200, data: {...} } 或直接返回对象
      fetchedUser = meRes.data?.data || meRes.data || null
    } catch (meErr) {
      // 无法获取 user 信息时不阻塞登录，但会保留 token
      console.warn('获取当前用户信息失败（/api/user/me）：', meErr)
      fetchedUser = null
    }

    // 如果后端没有返回完整 user 信息，再尝试从 tokenRes 的其它字段解析
    let userInfo = fetchedUser || tokenData?.data?.userInfo || tokenData?.userInfo || { username: form.value.username }

    // 如果 userInfo 中没有 userId字段，尝试解码 JWT 获取 sub/id
    if ((!userInfo || !userInfo.userId) && accessToken) {
      try {
        const payload = accessToken.split('.')[1]
        // atob may fail on unicode, use decodeURIComponent trick
        const json = decodeURIComponent(Array.prototype.map.call(atob(payload), c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2)).join(''))
        const decoded = JSON.parse(json)
        const possibleId = decoded.sub || decoded.user_id || decoded.id
        if (possibleId) {
          userInfo = userInfo || {}
          userInfo.userId = possibleId
        }
      } catch (e) {
        // ignore decode errors
        console.warn('JWT 解析用户 id 失败：', e)
      }
    }

    // 如果 userInfo 中没有 userId 字段且我们拿到了 accessToken，存 token 但不要把 malformed user 写入 store
    if (!userInfo || !userInfo.userId) {
      // 若没有 userId，尽量 avoid storing incomplete user; instead store token and then request me later when needed
      // 但为了兼容现有逻辑，我们 prefer to setLoginSuccess only if we have a userId
      // 存储 token 到 localStorage，后续 initLoginState/页面可尝试用 token 拉取 user
      localStorage.setItem('token', accessToken)
      // 确保 axios 有 header
      axios.defaults.headers.common['Authorization'] = `Bearer ${accessToken}`

      // 如果我们 did fetch a user object without userId, attach a provisional userId if possible (从 username 生成)，否则 keep it minimal
      if (userInfo && !userInfo.userId && userInfo.username) {
        // 生成一个临时标识（仅作兼容），但最好由后端返回真实 id
        userInfo.userId = userInfo.userId || (`u_${userInfo.username}`)
      }
    }

    // 如果我们确实拿到了 userId，则调用 setLoginSuccess 保存 token + user
    if (userInfo && userInfo.userId) {
      userStore.setLoginSuccess(accessToken, userInfo)
    } else {
      // 没有 userId 的情况下仍然写入 token 到 store (isLogin=false) — 保持 token，以便后续请求可用
      // 这里我们仍然 set token into store so axios and other modules can use it
      userStore.token = accessToken
      try {
        axios.defaults.headers.common['Authorization'] = `Bearer ${accessToken}`
      } catch (e) {
        // Log the error to avoid silent failure and satisfy ESLint (no-empty)
        // This can help diagnose environments where axios.defaults isn't writable
        // eslint-disable-next-line no-console
        console.warn('Failed to set axios default Authorization header:', e)
      }
    }

    ElMessage.success('登录成功')
    return true
  } catch (error) {
    console.error('后端登录请求失败：', error)
    if (error.response) {
      ElMessage.error('后端报错：' + (error.response.data?.detail || error.response.data?.msg || '登录失败'))
    } else if (error.request) {
      ElMessage.error('网络错误，请检查后端服务器是否启动')
    } else {
      ElMessage.error('请求出错：' + error.message)
    }
    return false
  }
}

// 提交表单
const submitForm = async () => {
  try {
    await formRef.value.validate()
    let loginSuccess = false
    if (isMock) {
      // 本地
      loginSuccess = userStore.login(form.value.username, form.value.password)
    } else {
      // 后端
      loginSuccess = await apiLogin()
    }

    if (loginSuccess) {
      ElMessage.success('登录成功')
      // 判断是否是系统管理员
      const isAdmin = userStore.userInfo.userType === '系统管理员'
      const targetPath = isAdmin ? '/admin' : (route.query.redirect || '/home')
      router.push(targetPath)
    } else {
      ElMessage.error('用户名或密码错误')
    }
  } catch (error) {
    console.error('表单验证失败：', error)
  }
}


// 跳转到注册页
const goToRegister = () => {
  router.push('/register')
}
</script>

<style scoped>
.login-container
{
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #BFD7EA;
}

.login-card
{
  width: 600px;
  height: 600px;
  padding: 30px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.login-title
{
  text-align: center;
  margin-top: 20px;
  margin-bottom: 80px;
  color: #79B0D9;
  font-weight: 900;
  font-size: 36px;
}

.login-btn
{
  width: 90%;
  background-color: #79B0D9;
}

.el-form-item
{
  margin-bottom: 50px;
  width: 90%;
}

.el-link
{
  display: block;
  text-align: center;
  margin-top: 30px;
  color: #79B0D9;
}

:deep(.el-icon-view) {
  color: #79B0D9;
}
</style>