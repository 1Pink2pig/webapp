// ...existing code...
methods: {
  async handleLogin() {
    // ...existing code...
    const res = await api.login(this.form); // 假设返回 { token: '...' }
    if (res && res.token) {
      localStorage.setItem('token', res.token);
      // 如果使用 vuex，也同步写入
      if (this.$store && this.$store.commit) {
        this.$store.commit('auth/setToken', res.token);
      }
      // 登录成功后跳回原先请求页面或默认 need/list
      const redirect = this.$route.query.redirect || { name: 'NeedList' };
      this.$router.replace(redirect);
    } else {
      // ...existing code...
    }
  }
}
// ...existing code...

