import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import { ElMessage, ElMessageBox } from 'element-plus'
import router from './router'
import App from './App.vue'

// 全局挂载工具
const app = createApp(App)
app.use(createPinia())
app.use(ElementPlus)
app.use(router)
app.config.globalProperties.$message = ElMessage
app.config.globalProperties.$confirm = ElMessageBox.confirm

app.mount('#app')
