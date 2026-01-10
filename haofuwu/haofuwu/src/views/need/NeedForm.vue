<template>
  <div class="need-form-container" v-loading="isLoading" element-loading-text="处理中...">
    <el-card class="need-form-card">
      <h2 class="need-form-title">{{ isEdit ? '编辑需求' : '发布新需求' }}</h2>
      <el-form :model="form" :rules="rules" ref="formRef" label-width="120px">
        <!-- 服务类型 -->
        <el-form-item label="服务类型" prop="serviceType">
          <el-select v-model="form.serviceType" placeholder="请选择服务类型">
            <el-option label="居家维修" value="居家维修"></el-option>
            <el-option label="生活照料" value="生活照料"></el-option>
            <el-option label="清洁保洁" value="清洁保洁"></el-option>
            <el-option label="出行就医" value="出行就医"></el-option>
            <el-option label="餐食服务" value="餐食服务"></el-option>
            <el-option label="其它" value="其它"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="需求主题" prop="title">
          <el-input v-model="form.title" placeholder="请输入需求主题"></el-input>
        </el-form-item>
        <el-form-item label="需求描述" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="5" placeholder="请详细描述需求"></el-input>
        </el-form-item>
        <el-form-item label="上传文件">
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
        <el-form-item>
          <el-button type="primary" @click="submitForm" class="submit-btn">
            {{ isEdit ? '保存修改' : '发布需求' }}
          </el-button>
          <el-button @click="goBack" class="cancel-btn">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/store/userStore'
import FileUpload from '@/components/FileUpload.vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const baseUrl = process.env.VUE_APP_API_BASE_URL || 'http://127.0.0.1:8000'

const isMock = false

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const formRef = ref(null)
const isLoading = ref(false)

// Normalize and validate route param id to ensure we only use a positive integer
const rawNeedId = route.params.id || ''
let needId = ''
if (rawNeedId !== null && rawNeedId !== undefined) {
  const parsed = Number(rawNeedId)
  if (!Number.isFinite(parsed) || Number.isNaN(parsed)) {
    needId = ''
  } else {
    needId = Number.isInteger(parsed) ? parsed : Math.floor(parsed)
  }
}
const isEdit = ref(!!needId) // 是否是编辑模式

// 表单数据
const form = ref({
  serviceType: '',
  title: '',
  description: '',
  files: [],
  region: ''
})

// 表单规则
const rules = ref({
  serviceType: [{ required: true, message: '请选择服务类型', trigger: 'change' }],
  title: [
    { required: true, message: '请输入需求主题', trigger: 'blur' },
    { max: 50, message: '主题长度不超过50字', trigger: 'blur' }
  ],
  description: [
    { required: true, message: '请输入需求描述', trigger: 'blur' },
    { min: 10, message: '描述长度不少于10字', trigger: 'blur' }
  ]
})

const getMockNeedDetail = () => {
  return userStore.needList.find(item => item.needId === needId) || null
}

/**
 * 获取需求详情
 */
const getNeedDetail = async () => {
  try {
    if (!needId) {
      ElMessage.error('无效的需求ID，无法获取详情')
      return router.push('/need/list')
    }

    isLoading.value = true
    const token = userStore.token || sessionStorage.getItem('token') || ''
    const res = await axios.get(`${baseUrl}/api/need/detail/${needId}`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (res.data.code === 200) {
      const data = res.data.data
      form.value = {
        serviceType: data.serviceType,
        title: data.title,
        description: data.description,
        files: data.imgUrls?.map(url => ({ url })) || [], // 适配文件格式
        region: data.region || ''
      }
    } else {
      ElMessage.error(res.data.msg || '获取需求详情失败')
      router.push('/login')
    }
  } catch (error) {
    console.error('getNeedDetail error:', error)
    if (error.response && error.response.status === 422) {
      ElMessage.error('请求参数错误：无效的需求ID')
      router.push('/need/list')
    } else {
      ElMessage.error('网络错误，无法获取需求详情')
      router.push('/login')
    }
  } finally {
    isLoading.value = false
  }
}

/**
 * 提交需求
 */
const submitNeed = async () => {
  try {
    isLoading.value = true
    const submitData = {
      serviceType: form.value.serviceType,
      title: form.value.title,
      description: form.value.description,
      imgUrls: form.value.files.filter(f=> (f.type && f.type.startsWith('image')) || (f.url && f.url.match(/\.(jpg|jpeg|png|gif|bmp|webp)(\?|$)/i))).map(file => file.url),
      videoUrl: (form.value.files.find(f=> (f.type && f.type.startsWith('video')) || (f.url && f.url.match(/\.(mp4|webm|ogg|mov|mkv)(\?|$)/i)))||{}).url || '',
      region: form.value.region
    }

    // Use normalized needId for edit
    const apiUrl = isEdit.value ? `/api/need/${needId}` : '/api/need/'
    const method = isEdit.value ? 'put' : 'post'
    const token = userStore.token || sessionStorage.getItem('token') || ''
    const fullUrl = `${baseUrl}${apiUrl}`

    const res = await axios[method](fullUrl, submitData, {
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    })

    // 兼容后端返回格式
    // Determine success and try to extract created/updated need id.
    if (res.status === 200) {
      // success (FastAPI/axios)
      ElMessage.success(isEdit.value ? '需求修改成功' : '需求发布成功')

      // Try to extract id from multiple possible response shapes:
      // 1) Envelope: { code:200, data: { id / needId } }
      // 2) Raw resource: { id, ... } (response_model=NeedOut)
      let createdId = null
      try {
        const body = res.data
        if (body) {
          if (body.code === 200 && body.data) {
            const d = body.data
            createdId = d.id ?? d.needId ?? d.id
          } else if (body.id || body.needId) {
            // direct NeedOut object
            createdId = body.id ?? body.needId
          }
        }
      } catch (e) {
        // ignore parse errors
        createdId = null
      }

      if (createdId !== null && createdId !== undefined && String(createdId).trim() !== '') {
        const idNum = Number(createdId)
        if (Number.isFinite(idNum) && !Number.isNaN(idNum)) {
          return router.push(`/need/detail/${idNum}`)
        }
      }

      // fallback to list page if we couldn't extract an id (e.g. update endpoint)
      router.push('/need/list')
    } else {
      ElMessage.error(res.data?.msg || (isEdit.value ? '修改失败' : '发布失败'))
    }
  } catch (error) {
    console.error('submitNeed error:', error)
    // 详细报错提示
    if (error.response && error.response.status === 404) {
       ElMessage.error('接口地址错误 (404)，请检查后端路由')
    } else if (error.response && error.response.status === 422) {
       ElMessage.error('请求参数错误：请检查提交的数据或需求ID')
    } else {
       ElMessage.error('网络错误，提交失败')
    }
  } finally {
    isLoading.value = false
  }
}

onMounted(async () => {
  if (!userStore.isLogin) {
    ElMessage.warning('请先登录')
    return router.push('/login')
  }

  // 编辑模式
  if (isEdit.value) {
    if (!needId) {
      ElMessage.error('无效的需求ID，无法进入编辑页面')
      return router.push('/need/list')
    }

    if (isMock) {
      const need = getMockNeedDetail()
      if (!need) {
        ElMessage.error('需求不存在')
        return router.push('/need/list')
      }
      form.value = {
        serviceType: need.serviceType,
        title: need.title,
        description: need.description,
        files: need.imgUrls?.map(url => ({ url })) || [], // 转换为文件列表格式
        region: need.region || ''
      }
    } else {
      // 后端
      await getNeedDetail()
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
        // 编辑需求
        const updateData = {
          serviceType: form.value.serviceType,
          title: form.value.title,
          description: form.value.description,
          imgUrls: form.value.files.map(file => file.url),
          region: form.value.region || userStore.needList.find(n => n.needId === needId)?.region
        }
        const success = userStore.updateNeed(needId, updateData)
        if (success) {
          ElMessage.success('需求修改成功')
          router.push('/need/list')
        } else {
          ElMessage.error('该需求已有响应，无法修改')
        }
      } else {
        // 发布新需求
        const newNeedData = {
          serviceType: form.value.serviceType,
          title: form.value.title,
          description: form.value.description,
          imgUrls: form.value.files.map(file => file.url),
          region: form.value.region
        }
        userStore.addNeed(newNeedData)
        ElMessage.success('需求发布成功')
        router.push('/need/list')
      }
    } else {
      // 后端
      await submitNeed()
    }
  } catch (error) {
    console.error('表单验证/提交失败：', error)
    ElMessage.error('请完善表单信息后提交')
  }
}

/**
 * 取消返回
 */
const goBack = () => {
  router.back()
}
</script>

<style scoped>

.need-form-container {
  padding: 20px;
  background-color: #BFD7EA;
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: flex-start;
}

/* 卡片 */
.need-form-card {
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
.need-form-title {
  text-align: center;
  margin-bottom: 20px;
  color: #9A7B68;
  font-weight: 500;
  font-size: 20px;
  letter-spacing: 0.3px;
}

/* 表单元素 */
:deep(.el-form-item__label) {
  color: #4A5568 !important;
  font-weight: 400 !important;
}

:deep(.el-input__wrapper),
:deep(.el-select__wrapper) {
  border-radius: 8px !important;
  border: 1px solid #D9CFB8 !important;
  box-shadow: none !important;
}

:deep(.el-input__wrapper:hover),
:deep(.el-select__wrapper:hover) {
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

/* 按钮样式*/
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