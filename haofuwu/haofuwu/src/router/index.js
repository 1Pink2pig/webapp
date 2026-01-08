import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/store/userStore'

// 导入所有页面
import HomePage from '@/views/user/HomePage.vue'
import LoginPage from '@/views/auth/LoginPage.vue'
import RegisterPage from '@/views/auth/RegisterPage.vue'
import NeedList from '@/views/need/NeedList.vue'
import UserDetail from '@/views/user/UserDetail.vue'
import EditProfile from '@/views/auth/EditProfile.vue'
import MyServiceList from '@/views/service/MyServiceList.vue'
import NeedDetail from '@/views/detail/NeedDetail.vue'
import ServiceForm from '@/views/service/ServiceForm.vue'
import NeedForm from '@/views/need/NeedForm.vue'
import ServiceList from '@/views/service/ServiceList.vue'
import ServiceDetail from '@/views/detail/ServiceDetail.vue'
import ServiceConfirm from '@/views/service/ServiceConfirm.vue'
import AdminPage from '@/views/stats/AdminPage.vue'

const routes = [
  // 根路由
  { path: '/', redirect: '/login' },

  //首页
  {
    path: '/home',
    name: 'Home',
    component: HomePage
  },

  // 登录页
  {
    path: '/login',
    name: 'Login',
    component: LoginPage,
    meta: { noAuth: true }
  },

  // 注册页
  {
    path: '/register',
    name: 'Register',
    component: RegisterPage,
    meta: { noAuth: true }
  },

  // 需求列表
    {
      path: '/login',
      name: 'NeedList',
      component: NeedList
    },

  // 用户详情
     {
       path: '/user-detail/:id',
       name: 'UserDetail',
       component: UserDetail,
       props: true
     },

  // 个人资料编辑
  {
    path: '/edit-profile',
    name: 'EditProfile',
    component: EditProfile
  },

  // 我的服务列表
   {
     path: '/service/my-list',
     name: 'MyServiceList',
     component: MyServiceList
   },

   // 需求详情
     {
       path: '/need/detail/:id',
       name: 'NeedDetail',
       component: NeedDetail,
       props: true
     },

   // 服务表单
     {
       path: '/service/form/:needId/:serviceId?',
       name: 'ServiceForm',
       component: ServiceForm,
       props: true
     },

   // 需求表单（新增/编辑）
     {
       path: '/need/form/:id?',
       name: 'NeedForm',
       component: NeedForm,
       props: true
     },

   // 服务列表
     {
       path: '/service/list',
       name: 'ServiceList',
       component: ServiceList
     },

   // 服务详情
     {
       path: '/service/detail/:id',
       name: 'ServiceDetail',
       component: ServiceDetail,
       props: true
     },

   // 服务确认
     {
       path: '/service/confirm/:serviceId',
       name: 'ServiceConfirm',
       component: ServiceConfirm,
       props: true
     },

   // 统计页面
     {
       path: '/admin',
       name: 'Admin',
       component: AdminPage,
       meta: { requireAdmin: true } // 标记需要管理员权限
     }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  // 初始化登录状态（读取 localStorage），确保 guard 能正确识别已登录用户
  if (typeof userStore.initLoginState === 'function') {
    try {
      userStore.initLoginState()
    } catch (e) {
      // ignore
    }
  }

  const isLogin = userStore.isLogin

  // DEBUG: 打印路由与登录态信息，便于定位循环跳转
  try {
    // eslint-disable-next-line no-console
    console.debug('[ROUTER GUARD] to=', to.fullPath, 'from=', from.fullPath, 'isLogin=', isLogin, 'user=', userStore.userInfo)
  } catch (e) {
    // ignore
  }

  // 无需登录的页面
  if (to.meta.noAuth) {
    next()
    return
  }

  // 未登录
  if (!isLogin) {
    next(`/login?redirect=${encodeURIComponent(to.path)}`) // encodeURIComponent处理特殊路径
    return
  }

  // 需要管理员权限的页面 -> 非管理员用户重定向到 /home（避免 UI/路由循环）
  if (to.meta.requireAdmin) {
    const isAdmin = userStore.userInfo && userStore.userInfo.userType === '系统管理员'
    if (!isAdmin) {
      next('/home')
      return
    }
  }

  // 已登录且无特殊权限要求 → 正常放行
  next()
})

export default router