const { defineConfig } = require('@vue/cli-service')

module.exports = defineConfig({
  configureWebpack: (config) => {
    // 过滤掉 CaseSensitivePathsPlugin，禁用大小写路径校验（Windows 专用）
    config.plugins = config.plugins.filter(
      plugin => plugin.constructor.name !== 'CaseSensitivePathsPlugin'
    )
    // 保留其他必要的 resolve 配置（仅保留 extensions，避免多余属性）
    config.resolve = {
      ...config.resolve,
      extensions: ['.mjs', '.js', '.jsx', '.json', '.vue'] // 仅保留合法属性
    }
  },
  transpileDependencies: true,
  // 开发时把 /api 请求代理到后端，避免在本地未设置 VUE_APP_API_BASE_URL 时出现 404
  devServer: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false,
        ws: false
      }
    },
    client: {
      overlay: false // 关闭 dev server 的错误遮罩（避免 ResizeObserver 错误打断开发）
    }
  }
})