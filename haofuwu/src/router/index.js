// ...existing code...
router.beforeEach((to, from, next) => {
  // ...existing code...
  const token = localStorage.getItem('token') || (store && store.state && store.state.auth && store.state.auth.token);
  // 防止同一路径反复 next 导致的循环
  if (to.fullPath === from.fullPath) {
    return next();
  }

  // 如果目标页面不需要鉴权，直接放行
  if (!to.meta || !to.meta.requiresAuth) {
    // 已登录但去登录页 -> 跳到默认页（need/list）
    if (to.name === 'login' && token) {
      return next({ name: 'NeedList' });
    }
    return next();
  }

  // 需要鉴权但没有 token -> 去登录，并带上原始目标用于登录后跳回
  if (!token) {
    return next({ name: 'login', query: { redirect: to.fullPath } });
  }

  // 已登录且目标是登录页 -> 跳到默认页或 redirect
  if (to.name === 'login' && token) {
    return next({ name: 'NeedList' });
  }

  next();
});
// ...existing code...

