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
    const params = new URLSearchParams()
    params.append('username', form.value.username)
    params.append('password', form.value.password)

    const response = await axios.post(
      'http://127.0.0.1:8000/api/auth/token',
      params
    )
    const res = response.data

    if (res.code === 200 || res.access_token) {
      const token = res.access_token || res.data?.access_token
      const userInfo = res.data?.userInfo || { username: form.value.username }

      userStore.setLoginSuccess(token, userInfo)

      ElMessage.success('登录成功')
      return true
    } else {
      ElMessage.error(res.msg || '用户名或密码错误')
      return false
    }
  } catch (error) {
    console.error('后端登录请求失败：', error)
    if (error.response) {
      ElMessage.error('后端报错：' + (error.response.data.detail || error.response.data.msg || '登录失败'))
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