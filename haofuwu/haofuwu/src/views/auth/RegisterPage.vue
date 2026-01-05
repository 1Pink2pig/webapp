<template>
  <div class="register-container">
    <el-card class="register-card">
      <h2 class="register-title">用户注册</h2>
      <el-form :model="form" :rules="rules" ref="formRef" label-width="78px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" placeholder="请输入用户名"></el-input>
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input
          v-model="form.password"
          type="password"
          placeholder="密码需不少于6位,含2个数字,不能都为大写或小写"
          prefix-icon="Lock"
          show-password
          >
          </el-input>
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input
          v-model="form.confirmPassword"
          type="password"
          placeholder="请再次输入密码"
          prefix-icon="Lock"
          show-password
          >
          </el-input>
        </el-form-item>
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="form.phone" placeholder="请输入11位手机号"></el-input>
        </el-form-item>
        <el-form-item label="真实姓名" prop="realName">
          <el-input v-model="form.realName" placeholder="请输入真实姓名"></el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="submitForm" :loading="isSubmitting" class="register-btn">注册</el-button>
        </el-form-item>
        <el-form-item>
          <el-link type="primary" @click="goToLogin" style="vertical-align: middle;">已有账号？去登录</el-link>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/store/userStore'
import { validatePassword, validatePhone, validateUsernameUnique } from '@/utils/validator'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const isMock = false

const router = useRouter()
const userStore = useUserStore()
const formRef = ref(null)
const isSubmitting = ref(false)

// 表单数据
const form = ref({
  username: '',
  password: '',
  confirmPassword: '',
  phone: '',
  realName: ''
})

// 表单规则
const rules = ref({
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在3-20位之间', trigger: 'blur' },
    { validator: async (rule, value) => {
      const isUnique = await validateUsernameUnique(value, isMock)
      if (!isUnique) {
        return Promise.reject('用户名已存在')
      }
      return Promise.resolve()
    }, trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { validator: (rule, value) => {
      if (!validatePassword(value)) {
        return Promise.reject('密码需不少于6位、含2个数字、不都为大小写')
      }
      return Promise.resolve()
    }, trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: (rule, value) => {
      if (value !== form.value.password) {
        return Promise.reject('两次输入密码不一致')
      }
      return Promise.resolve()
    }, trigger: 'blur' }
  ],
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { validator: (rule, value) => {
      if (!validatePhone(value)) {
        return Promise.reject('请输入有效的11位手机号')
      }
      return Promise.resolve()
    }, trigger: 'blur' }
  ],
  realName: [
    { required: true, message: '请输入真实姓名', trigger: 'blur' }
  ]
})

const apiRegister = async () => {
  try {
    // 发送后端注册请求
    const response = await axios.post(
      'http://127.0.0.1:8000/api/register',
      {
        username: form.value.username,
        password: form.value.password,
        phone: form.value.phone,
        realName: form.value.realName
      },
      {
        headers: { 'Content-Type': 'application/json' }
      }
    )

    const res = response.data
    // 后端返回成功
    if (res.code === 200) {
      ElMessage.success(res.msg || '注册成功！')
      return true
    } else {
      // 后端返回业务错误
      ElMessage.error(res.msg || '注册失败，请重试')
      return false
    }
  } catch (error) {
    // 捕获请求异常
    console.error('后端注册请求失败：', error)
    if (error.response) {
      // 后端返回错误状态码
      ElMessage.error('后端报错：' + (error.response.data.msg || '注册失败'))
    } else if (error.request) {
      // 网络错误
      ElMessage.error('网络错误，请检查后端服务器是否启动')
    } else {
      // 其他请求错误
      ElMessage.error('请求出错：' + error.message)
    }
    return false
  }
}

const submitForm = async () => {
  try {
    //前端表单校验
    await formRef.value.validate()
    isSubmitting.value = true
    let registerSuccess = false

    if (isMock) {
      // 本地
      registerSuccess = userStore.register(form.value)
      if (registerSuccess) {
        ElMessage.success('注册成功！即将跳转到登录页')
      } else {
        ElMessage.error('注册失败（用户名已存在/参数错误）')
      }
    } else {
      registerSuccess = await apiRegister()
    }

    //注册成功：跳转登录页
    if (registerSuccess) {
      setTimeout(() => {
        router.push('/login')
      }, 1500)
    }
  } catch (error) {
    // 表单校验失败
    console.error('表单验证失败：', error)
    ElMessage.error('表单填写有误，请检查！')
  } finally {
    isSubmitting.value = false
  }
}

// 跳转到登录页
const goToLogin = () => {
  router.push('/login')
}
</script>

<style scoped>
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #BFD7EA;
}

.register-card {
  width: 600px;
  height: 800px;
  padding: 30px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.register-title {
  text-align: center;
  margin-top: 10px;
  margin-bottom: 70px;
  color: #79B0D9;
  font-weight: 900;
  font-size: 36px;
}

.el-form-item {
  margin-bottom: 50px;
}

.el-link {
  display: block;
  text-align: center;
  margin-left: 0;
  color: #79B0D9;
}

.register-btn {
  width: 80%;
  background-color: #79B0D9;
  border-color: #79B0D9;
}

:deep(.el-icon-view),
:deep(.el-icon-hide) {
  color: #79B0D9;
}
</style>