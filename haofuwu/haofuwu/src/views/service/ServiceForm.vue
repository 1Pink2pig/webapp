<template>
  <div class="service-form-container" v-loading="isLoading" element-loading-text="处理中...">
    <el-card class="service-form-card">
      <!-- 标题：服务自荐 -->
      <h2 class="service-form-title">{{ isEdit ? '编辑服务自荐' : '发布服务自荐' }}</h2>
      <el-form :model="form" :rules="rules" ref="formRef" label-width="120px">
        <!-- 需求主题 -->
        <el-form-item label="需求主题" disabled>
          <el-input v-model="form.needTitle" placeholder="加载中..." readonly></el-input>
        </el-form-item>
        <!-- 服务类型 -->
        <el-form-item label="服务类型" prop="serviceType" v-if="!isEdit">
          <el-select v-model="form.serviceType" placeholder="请选择服务类型">
            <el-option label="居家维修" value="居家维修"></el-option>
            <el-option label="生活照料" value="生活照料"></el-option>
            <el-option label="清洁保洁" value="清洁保洁"></el-option>
            <el-option label="出行就医" value="出行就医"></el-option>
            <el-option label="餐食服务" value="餐食服务"></el-option>
            <el-option label="其它" value="其它"></el-option>
          </el-select>
        </el-form-item>
        <!-- 服务主题 -->
        <el-form-item label="服务主题" prop="title">
          <el-input v-model="form.title" placeholder="请输入服务自荐主题（如：水管维修服务自荐）"></el-input>
        </el-form-item>
        <!-- 自荐描述 -->
        <el-form-item label="自荐描述" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="5"
            placeholder="请详细描述你的服务能力、可服务时间、优势等"
          ></el-input>
        </el-form-item>
        <!-- 文件上传 -->
        <el-form-item label="上传证明文件">
          <FileUpload
            v-model:fileList="form.files"
            @upload-success="handleUploadSuccess"
          />
          <div class="file-preview">
            <h4>文件预览：</h4>
            <div class="file-list">
              <div v-for="(file, index) in form.files" :key="index" class="file-item">
                <template v-if="(file.type && file.type.startsWith('image')) || (!file.type && file.url && file.url.match(/\.(jpg|jpeg|png|gif|bmp|webp)(\?|$)/i))">
                  <img :src="file.url" alt="图片" class="file-img" @click="openPreview(file.url, 'image')">
                </template>
                <template v-else-if="(file.type && file.type.startsWith('video')) || (!file.type && file.url && file.url.match(/\.(mp4|webm|ogg|mov|mkv)(\?|$)/i))">
                  <video :src="file.url" controls class="file-video" @click="openPreview(file.url, 'video')"></video>
                </template>
              </div>
              <div v-if="form.files.length === 0" class="no-file">暂无上传文件</div>
            </div>
          </div>
        </el-form-item>
        <!-- 操作按钮 -->
        <el-form-item>
          <el-button type="primary" @click="submitForm" class="submit-btn">
            {{ isEdit ? '保存修改' : '发布自荐' }}
          </el-button>
          <el-button @click="goBack" class="cancel-btn">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/store/userStore'
import FileUpload from '@/components/FileUpload.vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const isMock = false

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const formRef = ref(null)
const isLoading = ref(false) // 加载状态

const needId = route.params.needId
const serviceId = route.params.serviceId
const isEdit = ref(!!serviceId)

const getValidNeedByType = (serviceType) => {
  if (!serviceType) return {}
  return userStore.needList.find(item => item.serviceType === serviceType) || {}
}

const targetNeed = computed(() => {
  if (isEdit.value) {
    const service = userStore.serviceSelfList.find(item => item.serviceId === serviceId)
    if (service) {
      if (service.needId) {
        return userStore.needList.find(item => item.needId === service.needId) || {}
      }
      return getValidNeedByType(service.serviceType)
    }
  }
  // 发布
  if (!needId || needId === 'none') return {}
  return userStore.needList.find(item => item.needId === needId) || {}
})

// 表单数据（匹配userStore的serviceSelfList字段结构）
const form = ref({
  needId: needId || '',       // 关联的需求ID
  needTitle: '',              // 需求主题
  serviceType: targetNeed.value.serviceType || '', // 服务类型
  title: '',                  // 服务自荐主题
  description: '',            // 自荐描述
  files: []
})

// 表单校验规则
const rules = ref({
  serviceType: [
    { required: true, message: '请选择服务类型', trigger: 'blur' },
  ],
  title: [
    { required: true, message: '请输入服务主题', trigger: 'blur' },
    { min: 2, message: '服务主题长度不少于2字', trigger: 'blur' }
  ],
  description: [
    { required: true, message: '请输入服务自荐描述', trigger: 'blur' },
    { min: 10, message: '自荐描述长度不少于10字', trigger: 'blur' }
  ]
})


/**
 * 获取服务自荐详情
 */
const getServiceDetail = async () => {
  try {
    isLoading.value = true
    const token = userStore.token || sessionStorage.getItem('token') || ''
    const res = await axios.get(`/api/service/detail/${serviceId}`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (res.data.code === 200) {
      const data = res.data.data
      // 回显表单（匹配后端返回结构）
      form.value = {
        needId: data.needId,
        needTitle: data.needTitle,
        serviceType: data.serviceType,
        title: data.title,
        description: data.content,
        files: data.files || []
      }
    } else {
      ElMessage.error(res.data.msg || '获取服务自荐详情失败')
      router.push('/service/list')
    }
  } catch (error) {
    ElMessage.error('网络错误，无法获取服务自荐详情')
    console.error('getServiceDetail error:', error)
    router.push('/service/list')
  } finally {
    isLoading.value = false
  }
}

/**
 * 提交服务自荐
 */
const submitService = async () => {
  try {
    isLoading.value = true
    // Use backend's registered endpoints:
    // - create: POST /api/service/   (services.router.post("/"))
    // - update: PUT  /api/service/{id}  (add RESTful update endpoint on backend if needed)
    const apiUrl = isEdit.value ? `/api/service/${serviceId}` : '/api/service/'
    const method = isEdit.value ? 'put' : 'post'
    const submitData = {
      ...form.value,
      content: form.value.description
    }
    delete submitData.description

    // If creating new service, pre-check the linked need status to avoid posting to closed/answered needs
    if (!isEdit.value && submitData.needId) {
      try {
        const token = userStore.token || sessionStorage.getItem('token') || ''
        const needRes = await axios.get(`/api/need/detail/${submitData.needId}`, {
          headers: { Authorization: `Bearer ${token}` }
        })
        if (!needRes || !needRes.data) {
          ElMessage.error('无法验证关联需求状态，提交已取消')
          return false
        }
        if (needRes.data.code !== 200) {
          ElMessage.error(needRes.data.msg || '关联需求不存在，无法提交')
          return false
        }
        const needData = needRes.data.data || {}
        // need.status '0' means active; hasResponse indicates prior responses
        if (String(needData.status) !== '0') {
          ElMessage.error('该需求已关闭或取消，无法提供服务')
          return false
        }
        if (needData.hasResponse) {
          ElMessage.error('该需求已有响应或已被确认，无法再次提供服务')
          return false
        }
      } catch (e) {
        console.error('验证需求状态失败：', e)
        ElMessage.error('验证需求状态失败，提交已取消')
        return false
      }
    }

    const token = userStore.token || sessionStorage.getItem('token') || ''
    const res = await axios[method](apiUrl, submitData, {
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    })
    if (res.data.code === 200) {
      ElMessage.success(isEdit.value ? '服务自荐修改成功' : '服务自荐发布成功')
      router.push('/service/list')
    } else {
      ElMessage.error(res.data.msg || (isEdit.value ? '修改失败' : '发布失败'))
    }
  } catch (error) {
    ElMessage.error('网络错误，提交失败')
    console.error('submitService error:', error)
  } finally {
    isLoading.value = false
  }
}

onMounted(async () => {
  // 登录态校验
  if (!userStore.isLogin) {
    ElMessage.warning('请先登录')
    return router.push('/login')
  }

  if (isMock) {
    form.value.needTitle = targetNeed.value.title || '无关联需求'

    // 编辑
    if (isEdit.value) {
      const service = userStore.serviceSelfList.find(item => item.serviceId === serviceId)
      if (!service) {
        ElMessage.error('服务自荐记录不存在')
        return router.push('/service/list')
      }
      form.value = {
        needId: service.needId || needId || '',
        needTitle: targetNeed.value.title || '无关联需求', // 复用匹配结果
        serviceType: service.serviceType,
        title: service.title,
        description: service.content,
        files: []
      }
    } else {
      form.value.serviceType = targetNeed.value.serviceType || ''
    }
  } else {
    // 后端
    if (needId && needId !== 'none') {
      try {
        const res = await axios.get(`/api/need/detail/${needId}`, {
          headers: { Authorization: `Bearer ${userStore.token || sessionStorage.getItem('token') || ''}` }
        })
        form.value.needTitle = res.data.code === 200 ? res.data.data.title : '未知需求'
      } catch (error) {
        form.value.needTitle = '未知需求'
      }
    } else {
      form.value.needTitle = '无关联需求'
    }
    if (isEdit.value) {
      await getServiceDetail()
    }
  }
})

/**
 * 文件上传成功回调
 */
const handleUploadSuccess = (fileList) => {
  form.value.files = fileList
}

/**
 * 提交表单
 */
const submitForm = async () => {
  try {
    // 表单校验
    await formRef.value.validate()

    if (isMock) {
      if (isEdit.value) {
        // 编辑模式：调用updateServiceSelf
        const updateSuccess = userStore.updateServiceSelf(serviceId, {
          serviceType: form.value.serviceType,
          title: form.value.title,
          content: form.value.description,
          updateTime: new Date().toLocaleString()
        })
        if (updateSuccess) {
          ElMessage.success('服务自荐修改成功（本地模式）')
          router.push('/service/list')
        } else {
          ElMessage.error('修改失败：仅可修改未被接受的自荐（本地模式）')
        }
      } else {
        // 发布模式
        const newService = userStore.addServiceSelf({
          serviceType: form.value.serviceType,
          title: form.value.title,
          content: form.value.description,
          needId: form.value.needId // 关联需求ID
        })

        if (newService) {
          ElMessage.success('服务自荐发布成功（本地模式）')

          // 更新需求的响应状态
          if (newService.needId && newService.needId !== 'none') {
            const needIndex = userStore.needList.findIndex(item => item.needId === newService.needId)
            if (needIndex !== -1) {
              userStore.needList[needIndex].hasResponse = true
              userStore.needList[needIndex].updateTime = new Date().toLocaleDateString()
              localStorage.setItem('mockNeedList', JSON.stringify(userStore.needList))
              ElMessage.info(`关联需求「${userStore.needList[needIndex].title}」已标记为“有响应”`)
            } else {
              ElMessage.warning('未找到关联的需求，无法更新响应状态')
            }
          }
          router.push('/service/list')
        } else {
          ElMessage.error('发布失败（本地模式）')
        }
      }
    } else {
      await submitService()
    }
  } catch (error) {
    console.error('表单验证/提交失败：', error)
    ElMessage.error('请完善表单信息后提交')
  }
}

/**
 * 返回上一页
 */
const goBack = () => {
  router.back()
}
</script>

<style scoped>

.service-form-container {
  padding: 20px;
  background-color: #BFD7EA;
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: flex-start;
}

/* 卡片 */
.service-form-card {
  width: 90%;
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  box-shadow: 0 1px 6px rgba(0, 0, 0, 0.05) !important;
  border-radius: 12px !important;
  border: none !important;
  background-color: #FFFFFF !important;
}

/* 标题 */
.service-form-title {
  text-align: center;
  margin-bottom: 20px;
  color: #9A7B68;
  font-weight: 500;
  font-size: 20px;
  letter-spacing: 0.3px;
}

/* 表单 */
:deep(.el-form-item__label) {
  color: #4A5568 !important;
  font-weight: 400 !important;
}

:deep(.el-input__wrapper) {
  border-radius: 8px !important;
  border: 1px solid #D9CFB8 !important;
  box-shadow: none !important;
}

:deep(.el-input__wrapper:hover) {
  border-color: #9A7B68 !important;
}

:deep(.el-textarea__wrapper) {
  border-radius: 8px !important;
  border: 1px solid #D9CFB8 !important;
}

/* 文件预览区域 */
.file-preview {
  margin-top: 20px;
}

.file-preview h4 {
  color: #9A7B68;
  font-size: 16px;
  font-weight: 500;
  margin: 0;
}

.file-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 10px;
}

.file-item {
  width: 200px;
  height: 150px;
  overflow: hidden;
  border: 1px solid #D9CFB8 !important;
  border-radius: 8px;
}

.file-img, .file-video {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.no-file {
  color: #9A7B68;
  padding: 20px;
  font-size: 14px;
}

/* 按钮 */
.submit-btn {
  background-color: #9A7B68 !important;
  border-color: #9A7B68 !important;
  border-radius: 8px !important;
  padding: 8px 20px !important;
  font-size: 14px !important;
}

.submit-btn:hover {
  background-color: #8A6B58 !important;
  border-color: #8A6B58 !important;
}

.cancel-btn {
  color: #9A7B68 !important;
  border-color: #9A7B68 !important;
  border-radius: 8px !important;
  padding: 8px 20px !important;
  font-size: 14px !important;
}

.cancel-btn:hover {
  background-color: #F5F0E8 !important;
}

</style>