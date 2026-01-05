<template>
  <!-- 加载状态覆盖整个页面 -->
  <div class="edit-profile-container" v-loading="isLoading" element-loading-text="保存中...">
    <!-- 编辑卡片 -->
    <el-card class="edit-profile-card">
      <h2 class="edit-profile-title">修改用户信息</h2>
      <el-form
        :model="form"
        :rules="rules"
        ref="formRef"
        label-width="120px"
        class="edit-profile-form"
      >
        <el-form-item label="用户名" disabled>
          <el-input v-model="form.username" placeholder="用户名"></el-input>
        </el-form-item>
        <el-form-item label="真实姓名" disabled>
          <el-input v-model="form.realName" placeholder="真实姓名"></el-input>
        </el-form-item>
        <el-form-item label="注册时间" disabled>
          <el-input v-model="form.registerTime" placeholder="注册时间"></el-input>
        </el-form-item>
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="form.phone" placeholder="请输入11位手机号"></el-input>
        </el-form-item>
        <el-form-item label="用户简介" prop="intro">
          <el-input v-model="form.intro" type="textarea" :rows="5" placeholder="请输入用户简介（可选）"></el-input>
        </el-form-item>
        <el-form-item label="新密码" prop="newPassword">
          <el-input v-model="form.newPassword" type="password" placeholder="不修改请留空（修改需不少于6位）"></el-input>
        </el-form-item>
        <el-form-item label="确认新密码" prop="confirmNewPassword">
          <el-input v-model="form.confirmNewPassword" type="password" placeholder="不修改请留空"></el-input>
        </el-form-item>
        <!-- 按钮组：保存+取消 -->
        <el-form-item class="edit-profile-btn-group">
          <el-button type="primary" @click="submitForm" class="edit-btn">保存修改</el-button>
          <el-button type="primary" @click="goBack" class="back-btn" plain>取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/store/userStore'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const isMock = false

// 初始化
const userStore = useUserStore()
const formRef = ref(null)
const router = useRouter()
const isLoading = ref(false)

// 表单数据
const form = ref({
  username: '',
  realName: '',
  registerTime: '',
  phone: '',
  intro: '',
  newPassword: '',
  confirmNewPassword: ''
})

// 表单验证规则
const rules = ref({
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    {
      validator: (rule, value) => {
        const phoneReg = /^1\d{10}$/
        if (value && !phoneReg.test(value)) {
          return Promise.reject('请输入有效的11位手机号')
        }
        return Promise.resolve()
      },
      trigger: 'blur'
    }
  ],
  newPassword: [
    {
      validator: (rule, value) => {
        //密码长度不少于6位
        if (value && value.length < 6) {
          return Promise.reject('密码长度不能少于6位')
        }
        //字母不能全为大写或全为小写
        if (value) {
          const hasLetter = /[a-zA-Z]/.test(value)
          if (hasLetter) {
            const isAllUpper = value === value.toUpperCase()
            const isAllLower = value === value.toLowerCase()
            if (isAllUpper || isAllLower) {
              return Promise.reject('密码中的字母不能全部为大写或全部为小写')
            }
          }
        }
        return Promise.resolve()
      },
      trigger: 'blur'
    }
  ],
  confirmNewPassword: [
    {
      validator: (rule, value) => {
        if (form.value.newPassword && value !== form.value.newPassword) {
          return Promise.reject('两次输入密码不一致')
        }
        return Promise.resolve()
      },
      trigger: 'blur'
    }
  ]
})

// 页面挂载
onMounted(() => {
  const userInfo = userStore.userInfo
  form.value = {
    username: userInfo.username || '',
    realName: userInfo.realName || '',
    registerTime: userInfo.registerTime || '',
    phone: userInfo.phone || '',
    intro: userInfo.intro || '',
    newPassword: '',
    confirmNewPassword: ''
  }
})

// 提交表单
const submitForm = async () => {
  try {
    //表单验证
    await formRef.value.validate()
    isLoading.value = true

    //整理提交数据
    const submitData = {
      phone: form.value.phone,
      intro: form.value.intro,
      ...(form.value.newPassword ? { password: form.value.newPassword } : {})
    }

    //本地
    if (isMock) {
      // Mock模式
      userStore.updateUser(submitData)
      ElMessage.success('修改成功！修改密码后请重新登录')
    } else {
      // 后端
      const res = await axios.put(
        '/api/user/me',
        submitData,
        { headers: { Authorization: `Bearer ${userStore.token}` } }
      )
      if (res.data.code === 200) {
        userStore.updateUser(res.data.data)
        ElMessage.success('修改成功！修改密码后请重新登录')
      } else {
        ElMessage.error(res.data.msg || '修改失败')
      }
    }

    //如果修改了密码，强制退出登录
    if (form.value.newPassword) {
      userStore.logout()
      router.push('/login')
    } else {
      goBack()
    }

  } catch (error) {
    console.error('表单提交失败：', error)
    ElMessage.error('提交失败，请检查表单内容')
  } finally {
    isLoading.value = false
  }
}

// 取消/返回：跳转到个人信息页面
const goBack = () => {
  if (window.history.length > 1) {
    router.back()
  } else {
    router.push(`/user-detail/${userStore.userInfo.userId}`)
  }
}
</script>

<style scoped>
.edit-profile-container {
  width: 100%;
  min-height: 100vh;
  padding: 20px;
  background-color: #BFD7EA;
  display: flex;
  justify-content: center;
  align-items: flex-start;
}

.edit-profile-card {
  width: 80%;
  max-width: 800px;
  padding: 20px;
  box-shadow: 0 1px 6px rgba(0, 0, 0, 0.05) !important;
  border-radius: 12px !important;
  border: none !important;
  background-color: #FFFFFF !important;
}

.edit-profile-title {
  text-align: center;
  margin-bottom: 20px;
  color: #9A7B68;
  font-weight: 500;
  font-size: 20px;
  letter-spacing: 0.3px;
}

.edit-profile-form {
  width: 100%;
}
.el-form-item {
  margin-bottom: 20px;
}

.edit-profile-btn-group {
  display: flex;
  gap: 20px;
  justify-content: center;
  margin-top: 8px;
}

.edit-btn {
  width: 140px;
  height: 40px;
  background-color: #9A7B68 !important;
  border-color: #9A7B68 !important;
  border-radius: 8px !important;
  font-size: 14px;
  transition: all 0.2s ease !important;
}
.edit-btn:hover {
  background-color: #8A6B58 !important;
  border-color: #8A6B58 !important;
}

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
</style>