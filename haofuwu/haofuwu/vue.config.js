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
  transpileDependencies: true
})