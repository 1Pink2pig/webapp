import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import { ElMessage, ElMessageBox } from 'element-plus'
import router from './router'
import App from './App.vue'
import { useUserStore } from './store/userStore'
import axios from 'axios'

// Add a global handler to ignore the benign ResizeObserver loop error that
// appears in some Chrome versions and shows up in the webpack-dev-server overlay.
// Placing it early ensures it runs before other listeners that might trigger the overlay.
if (typeof window !== 'undefined') {
  window.addEventListener('error', (event) => {
    try {
      const msg = event && event.message ? String(event.message) : ''
      if (msg.includes('ResizeObserver loop limit exceeded') || msg.includes('ResizeObserver loop completed with undelivered notifications')) {
        // stop propagation so dev overlay and console don't display this error
        event.stopImmediatePropagation && event.stopImmediatePropagation()
        event.preventDefault && event.preventDefault()
      }
    } catch (e) {
      // ignore handler failures
    }
  }, true)

  // Some builds surface this as an unhandled rejection; ignore that too if it mentions ResizeObserver
  window.addEventListener('unhandledrejection', (event) => {
    try {
      const reason = event && event.reason ? String(event.reason) : ''
      if (reason.includes('ResizeObserver loop limit exceeded') || reason.includes('ResizeObserver loop completed with undelivered notifications')) {
        event.preventDefault && event.preventDefault()
        event.stopImmediatePropagation && event.stopImmediatePropagation()
      }
    } catch (e) {
      // ignore
    }
  }, true)
}

// 全局挂载工具
const app = createApp(App)
const pinia = createPinia()
app.use(pinia)
app.use(ElementPlus)
app.use(router)
app.config.globalProperties.$message = ElMessage
app.config.globalProperties.$confirm = ElMessageBox.confirm

// 如果本地已有 token，先设置到 axios headers 中，以便 initLoginState 发起的任何请求有头
const savedToken = sessionStorage.getItem('token')
if (savedToken) {
  axios.defaults.headers.common['Authorization'] = `Bearer ${savedToken}`
}

// 将 store 恢复到内存（从 localStorage），并确保 axios header与 store.token 保持一致
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