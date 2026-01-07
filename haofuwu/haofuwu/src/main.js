import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import { ElMessage, ElMessageBox } from 'element-plus'
import router from './router'
import App from './App.vue'
import { useUserStore } from './store/userStore'
import axios from 'axios'
// 全局挂载工具
const app = createApp(App)
const pinia = createPinia()
app.use(pinia)
app.use(ElementPlus)
app.use(router)
app.config.globalProperties.$message = ElMessage
app.config.globalProperties.$confirm = ElMessageBox.confirm

// 如果本地已有 token，先设置到 axios headers 中，以便 initLoginState 发起的任何请求有头
const savedToken = localStorage.getItem('token')
if (savedToken) {
  axios.defaults.headers.common['Authorization'] = `Bearer ${savedToken}`
}

// 将 store 恢复到内存（从 localStorage），并确保 axios header 与 store.token 保持一致
const userStore = useUserStore()
userStore.initLoginState()
if (userStore.token) {
  axios.defaults.headers.common['Authorization'] = `Bearer ${userStore.token}`
}

app.mount('#app')

// Vue CLI sets process.env.NODE_ENV; use that check for dev-only exposure
if (process.env.NODE_ENV === 'development') {
    window.__pinia__ = pinia
    window.getUserStore = () => useUserStore()
    // 方便在控制台直接使用：打开 F12 后可以直接输入 `store` 或 `getUserStore()`
    // 仅在开发模式下暴露，避免生产环境泄露
    window.store = useUserStore()
    // 返回一个纯 JS 对象的快照，避免控制台显示 Proxy/编译后的函数字符串
    window.getUserSnapshot = () => JSON.parse(JSON.stringify(useUserStore().$state || {}))
}