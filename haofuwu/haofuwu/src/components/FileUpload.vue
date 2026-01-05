<template>
  <div class="file-upload-container">
    <!-- 上传组件 -->
    <el-upload
      ref="uploadRef"
       class="upload-demo custom-upload"
      :action="uploadUrl"
      :on-preview="handlePreview"
      :on-remove="handleRemove"
      :file-list="fileList"
      :auto-upload="false"
      :on-success="handleUploadSuccess"
      :on-error="handleUploadError"
      :before-upload="beforeUpload"
    >
      <div class="upload-trigger">
        <i class="el-icon-plus upload-icon"></i>
        <p class="upload-text">点击选择文件</p>
      </div>
    </el-upload>

    <el-button type="primary" @click="submitUpload" style="margin-top: 10px;">上传文件</el-button>

    <!-- 预览弹窗 -->
    <el-dialog v-model="previewVisible" title="文件预览" width="800px" append-to-body>
      <!-- 图片预览 -->
      <el-image-viewer
        v-if="previewType === 'image'"
        :url-list="[previewFile.url]"
        :initial-index="0"
        @close="previewVisible = false"
      />
      <!-- 视频预览 -->
      <video
        v-if="previewType === 'video'"
        :src="previewFile.url"
        controls
        width="100%"
        style="max-height: 500px;"
      >
        您的浏览器不支持视频播放
      </video>
    </el-dialog>
  </div>
</template>

<script setup>
/* global defineProps, defineEmits */
import { ref, watch } from 'vue'
import { ElMessage, ElDialog, ElImageViewer } from 'element-plus'

const props = defineProps({
  fileList: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['update:fileList', 'upload-success'])

const innerFileList = ref([...props.fileList])
watch(() => props.fileList, (newVal) => {
  innerFileList.value = [...newVal]
}, { deep: true })

watch(innerFileList, (newVal) => {
  emit('update:fileList', [...newVal])
  emit('upload-success', [...newVal])
}, { deep: true })

const uploadRef = ref(null)
const uploadUrl = ref('/api/upload') // 模拟上传接口

// 预览相关状态
const previewVisible = ref(false)
const previewFile = ref({})
const previewType = ref('')

/**
 * 移除文件
 */
const handleRemove = (file, fileList) => {
  innerFileList.value = fileList
  ElMessage.info(`已移除文件：${file.name}`)
  console.log('移除文件：', file, '剩余列表：', fileList)
}

/**
 * 预览文件
 */
const handlePreview = (file) => {
  console.log('预览文件：', file)
  previewFile.value = file

  // 判断文件类型
  const fileType = file.type || ''
  if (fileType.includes('image')) {
    previewType.value = 'image'
  } else if (fileType.includes('video')) {
    previewType.value = 'video'
  } else {
    ElMessage.warning('仅支持图片/视频预览')
    return
  }

  // 打开预览弹窗
  previewVisible.value = true
}

/**
 * 上传前校验
 */
const beforeUpload = (file) => {
  const isImage = file.type.includes('image')
  const isVideo = file.type.includes('video')
  const isAllow = isImage || isVideo

  if (!isAllow) {
    ElMessage.error('仅支持上传图片和视频文件！')
    return false
  }

  return true
}

/**
 * 手动提交上传
 */
const submitUpload = () => {
  if (innerFileList.value.length === 0) {
    ElMessage.warning('请选择要上传的文件')
    return
  }

  // 触发上传
  uploadRef.value.submit()
  ElMessage.info('开始上传文件...')
}

/**
 * 上传成功回调
 */
const handleUploadSuccess = (response, file, fileList) => {
  // 模拟接口返回
  const res = response || { code: 200, data: { url: URL.createObjectURL(file.raw) } }

  if (res.code === 200) {
    // 更新文件列表中的文件URL
    innerFileList.value = fileList.map(item => {
      if (item.uid === file.uid) {
        return { ...item, url: res.data.url }
      }
      return item
    })
    ElMessage.success(`文件 ${file.name} 上传成功！`)
  } else {
    ElMessage.error(`文件 ${file.name} 上传失败：${res.msg || '接口异常'}`)
  }
  console.log('上传成功：', response, file, fileList)
}

/**
 * 上传失败回调
 */
const handleUploadError = (error, file, fileList) => {
  ElMessage.error(`文件 ${file.name} 上传失败：${error.message || '网络错误'}`)
  console.error('上传失败：', error, file, fileList)
}
</script>

<style>
.file-upload-container {
  padding: 10px 0;
}
.custom-upload.upload-demo {
  border: 2px dashed #d9d9d9 !important;
  border-radius: 8px !important;
  padding: 30px 20px !important;
  text-align: center !important;
  cursor: pointer !important;
  background-color: #fafafa !important;
  transition: border-color 0.3s ease !important;
}

.custom-upload.upload-demo:hover {
  border-color: #9A7B68 !important;
}

.upload-trigger {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #9A7B68 !important;
}

.upload-icon {
  font-size: 32px !important; /* 放大图标 */
  margin-bottom: 8px !important;
  color: #9A7B68 !important;
}

.upload-text {
  font-size: 14px !important;
  color: #666 !important;
  margin: 0 !important;
}
</style>