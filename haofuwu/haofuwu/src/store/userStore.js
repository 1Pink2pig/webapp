import { defineStore } from 'pinia'

// 模拟本地存储的用户数据
const mockUsers = [
  {
    userId: '1',
    username: 'admin',
    password: 'Ww123456',
    userType: '系统管理员',
    realName: '管理员',
    phone: '13800138000',
    intro: '系统管理员账号',
    registerTime: '2025-01-01',
    updateTime: '2025-01-01'
  },
  {
    userId: '2',
    username: '扑通扑通',
    password: 'Aa123456',
    userType: '普通用户',
    realName: '周深',
    phone: '13900139000',
    intro: '什么？你怎么知道我是生米？',
    registerTime: '2025-01-02',
    updateTime: '2025-01-02'
  },
  {
    userId: '3',
    username: '口袋狸',
    password: 'Bb123456',
    userType: '普通用户',
    realName: '不告诉你',
    phone: '13700137000',
    intro: '求你了让我过吧',
    registerTime: '2025-01-03',
    updateTime: '2025-01-03'
  }
]

//地域池/需求描述池/生成需求
const regionPool = [
  '北京市朝阳区', '北京市海淀区', '上海市浦东新区', '上海市静安区',
  '广州市天河区', '广州市越秀区', '深圳市南山区', '深圳市福田区',
  '杭州市西湖区', '杭州市滨江区', '成都市锦江区', '成都市武侯区'
]
const descPool = {
  '居家维修': [
    '家里水管漏水严重，需要上门维修，最好今天下午有空',
    '电路跳闸多次，怀疑线路老化，需要专业电工检修',
    '马桶堵塞无法冲水，急需疏通，要求师傅带工具',
    '窗户合页生锈，开关卡顿，需要更换合页并润滑',
    '热水器不出热水，排查是否是加热管故障，需维修',
    '空调制冷效果差，需要清洗滤网并加氟',
    '油烟机油污过多，需要深度清洗，包括内部风轮',
    '燃气灶打不着火，检查是否是电池或燃气阀问题',
    '暖气片漏水，需要补漏并排气，保证供暖',
    '衣柜铰链松动，柜门下垂，需要调整并加固'
  ],
  '生活照料': [
    '独居老人80岁，需要日常陪护，包括买菜、做饭、聊天',
    '老人三餐无法自理，需要上门制作清淡易消化的餐食',
    '术后老人需要协助洗澡、穿衣，要求护理经验丰富',
    '老人子女不在身边，需要每天上门陪聊解闷，时长2小时',
    '每周三次接送老人去医院复诊，路程约5公里',
    '照顾术后康复老人，协助做康复训练，需有护理证',
    '帮老人代购慢性病药品，需凭处方到指定药店购买',
    '每月两次上门整理家务，主要是打扫房间、整理衣物',
    '老人忘记按时吃药，需要每天电话提醒+上门确认',
    '帮老人照顾宠物（猫咪），每天喂食、铲屎，时长1小时',
    '辅助脑梗老人做康复训练，需专业康复师，每周5次'
  ],
  '清洁保洁': [
    '全屋深度清洁，包括厨房、卫生间、卧室，要求无死角',
    '厨房重油污清理，重点是灶台、抽油烟机、橱柜内部',
    '卫生间瓷砖缝隙发霉，需要除霉并消毒，用环保清洁剂',
    '全屋玻璃擦拭，包括落地窗、阳台门，要求无水印',
    '实木地板打蜡保养，需先清洁再上蜡，共100平',
    '窗帘拆洗+安装，共4幅，材质为棉麻，需手洗',
    '沙发和地毯有污渍，需要专业清洗，去除异味',
    '冰箱内部除味+清洁，包括冷冻层，要求断电操作',
    '空调滤网拆卸清洗，共3台，包括挂机和柜机',
    '阳台杂物堆积，需要整理归类，部分物品需丢弃',
    '新房开荒保洁，刚装修完，需清理灰尘和胶迹'
  ],
  '出行就医': [
    '陪同老人去三甲医院挂号就诊，需帮忙排队、取号',
    '接送化疗病人往返医院，每周两次，车程约30分钟',
    '代取老人的检查报告，需凭就诊卡到医院打印',
    '陪诊时记录医生医嘱，整理成文字版给家属',
    '协助老人办理住院手续，包括缴费、填资料',
    '用轮椅接送行动不便的老人出门，范围5公里内',
    '异地就医陪同，需跟随老人去上海就诊，时长3天'
  ],
  '餐食服务': [
    '定制老年营养餐，低盐低脂，每天配送三餐',
    '每日三餐配送，针对糖尿病患者，控糖食谱',
    '术后流食制作，包括小米粥、蔬菜泥等，每日配送',
    '中秋家宴制作，需做8菜1汤，偏江浙口味',
    '每周5次午餐配送，针对独居老人，热菜热饭'
  ],
  '其它': [
    '帮忙搬运衣柜（双门），从5楼到1楼，无电梯',
    '网购家具组装，包括书桌、衣柜，需带工具',
    '帮老人代寄快递，需上门取件并打包，共3件',
    '教老人使用智能手机，包括微信、视频通话、扫码',
    '家电简单调试，电视连不上WiFi，需要排查问题'
  ]
}
const mockImgUrl = 'https://picsum.photos/400/300?random='
const mockVideoUrl = 'https://example.com/video/'

// 生成32条需求
const generateInitNeeds = () => {
  const needs = []
  let needId = 1
  //居家维修
  for (let i = 0; i < 10; i++) {
    const randomRegion = regionPool[Math.floor(Math.random() * regionPool.length)]
    needs.push({
      needId: `need_${needId++}`,
      userId: '1',
      region: randomRegion,
      serviceType: '居家维修',
      title: descPool['居家维修'][i].split('，')[0],
      description: descPool['居家维修'][i],
      imgUrls: [`${mockImgUrl}${needId}`, `${mockImgUrl}${needId + 100}`],
      videoUrl: i % 3 === 0 ? `${mockVideoUrl}${needId}` : '',
      createTime: '2025-09-01',
      updateTime: '2025-09-01',
      status: i % 4 === 0 ? '1' : '0',
      hasResponse: i % 2 === 0
    })
  }
  //清洁保洁
  for (let i = 0; i < 11; i++) {
    const randomRegion = regionPool[Math.floor(Math.random() * regionPool.length)]
    needs.push({
      needId: `need_${needId++}`,
      userId: '2',
      region: randomRegion,
      serviceType: '清洁保洁',
      title: descPool['清洁保洁'][i].split('，')[0],
      description: descPool['清洁保洁'][i],
      imgUrls: [`${mockImgUrl}${needId}`, `${mockImgUrl}${needId + 100}`],
      videoUrl: i % 3 === 0 ? `${mockVideoUrl}${needId}` : '',
      createTime: '2025-09-02',
      updateTime: '2025-09-02',
      status: i % 5 === 0 ? '1' : '0',
      hasResponse: i % 3 === 0
    })
  }
  //生活照料
  for (let i = 0; i < 11; i++) {
    const randomRegion = regionPool[Math.floor(Math.random() * regionPool.length)]
    needs.push({
      needId: `need_${needId++}`,
      userId: '3',
      region: randomRegion,
      serviceType: '生活照料',
      title: descPool['生活照料'][i].split('，')[0],
      description: descPool['生活照料'][i],
      imgUrls: [`${mockImgUrl}${needId}`, `${mockImgUrl}${needId + 100}`],
      videoUrl: i % 3 === 0 ? `${mockVideoUrl}${needId}` : '',
      createTime: '2025-09-03',
      updateTime: '2025-09-03',
      status: i % 6 === 0 ? '1' : '0',
      hasResponse: i % 4 === 0
    })
  }
  return needs
}

// 初始化
const initNeedList = () => {
  const storedNeeds = localStorage.getItem('mockNeedList')
  return storedNeeds ? JSON.parse(storedNeeds) : generateInitNeeds()
}

//服务自荐
const generateInitServiceSelf = () => {
  // status: 0=未被接受 1=已被接受
  return [
    {
      serviceId: 'service_1',
      needId: 'need_1', // 关联：居家维修-need_1
      userId: '2',
      serviceType: '居家维修',
      title: '管道维修服务自荐',
      content: '本人有5年水管、管道维修经验，可处理漏水、堵塞等问题，响应及时',
      createTime: '2025-09-01 10:20:30',
      updateTime: '2025-09-01 10:20:30',
      status: 0
    },
    {
      serviceId: 'service_2',
      needId: 'need_22', // 关联：生活照料-need_22
      userId: '2',
      serviceType: '生活照料',
      title: '助老服务上门陪护',
      content: '擅长照顾独居老人，可提供买菜、做饭、陪聊、基础护理等服务',
      createTime: '2025-09-05 14:15:20',
      updateTime: '2025-09-05 14:15:20',
      status: 1
    },
    {
      serviceId: 'service_3',
      needId: 'need_11', // 关联：清洁保洁-need_11
      userId: '3',
      serviceType: '清洁保洁',
      title: '新房开荒保洁服务',
      content: '专业开荒保洁团队，自带工具，可处理装修残留污渍、玻璃清洁等',
      createTime: '2025-09-10 09:30:15',
      updateTime: '2025-09-10 09:30:15',
      status: 0
    }
  ]
}

// 初始化
const initServiceSelfList = () => {
  const storedServiceSelf = localStorage.getItem('mockServiceSelfList')
  return storedServiceSelf ? JSON.parse(storedServiceSelf) : generateInitServiceSelf()
}

export const useUserStore = defineStore('user', {
  state: () => ({
    userInfo: {},
    token: localStorage.getItem('token') || '',
    isLogin: !!localStorage.getItem('token'),
    needList: initNeedList(),
    serviceSelfList: initServiceSelfList()
  }),
  actions: {
    setLoginSuccess(token, userInfo) {
      this.token = token
      this.userInfo = userInfo
      this.isLogin = true
      // 持久化存储
      localStorage.setItem('token', token)
      localStorage.setItem('user', JSON.stringify(userInfo))
    },

    // Mock模式登录
    login(username, password) {
      const user = mockUsers.find(u => u.username === username && u.password === password)
      if (user) {
        this.userInfo = { ...user }
        this.isLogin = true
        localStorage.setItem('user', JSON.stringify(user))
        return true
      }
      return false
    },

    // Mock模式注册
    register(userData) {
      const newUser = {
        userId: (mockUsers.length + 1).toString(),
        username: userData.username,
        password: userData.password,
        userType: '普通用户',
        realName: userData.realName || userData.username,
        phone: userData.phone,
        intro: '',
        registerTime: new Date().toLocaleDateString(),
        updateTime: new Date().toLocaleDateString()
      }
      mockUsers.push(newUser)
      localStorage.setItem('mockUsers', JSON.stringify(mockUsers))
      return true
    },

    // 更新用户信息
    updateUser(updatedData) {
      this.userInfo = {
        ...this.userInfo,
        ...updatedData,
        updateTime: new Date().toLocaleDateString()
      }
      // 同步更新 mock 数据
      const index = mockUsers.findIndex(u => u.userId === this.userInfo.userId)
      if (index !== -1) {
        mockUsers[index] = {
          ...mockUsers[index],
          ...updatedData,
          updateTime: this.userInfo.updateTime
        }
        localStorage.setItem('mockUsers', JSON.stringify(mockUsers))
        localStorage.setItem('user', JSON.stringify(this.userInfo))
      }
    },

    logout() {
      this.userInfo = {}
      this.token = '' // 清空内存 token
      this.isLogin = false
      localStorage.removeItem('user')
      localStorage.removeItem('token') // 清除缓存 token
    },

    initLoginState() {
      const storedUser = localStorage.getItem('user')
      const storedToken = localStorage.getItem('token')

      if (storedToken) {
        this.token = storedToken
      }

      if (storedUser) {
        this.userInfo = JSON.parse(storedUser)
        if (this.token) {
           this.isLogin = true
        }
      }
    },


    getUserById(userId) {
      return mockUsers.find(u => u.userId === userId) || null
    },

    //需求操作
    addNeed(needData) {
      let maxId = 0
      this.needList.forEach(item => {
        const idNum = parseInt(item.needId.replace('need_', ''))
        if (!isNaN(idNum) && idNum > maxId) {
          maxId = idNum
        }
      })
      const newNeedId = `need_${maxId + 1}`
      const newNeed = {
        needId: newNeedId,
        userId: this.userInfo.userId,
        region: needData.region || regionPool[Math.floor(Math.random() * regionPool.length)],
        serviceType: needData.serviceType,
        title: needData.title,
        description: needData.description || '',
        imgUrls: needData.imgUrls || [],
        videoUrl: needData.videoUrl || '',
        createTime: new Date().toLocaleDateString(),
        updateTime: new Date().toLocaleDateString(),
        status: '0',
        hasResponse: false
      }
      this.needList.push(newNeed)
      localStorage.setItem('mockNeedList', JSON.stringify(this.needList))
      return newNeed
    },
    deleteNeed(needId) {
      const index = this.needList.findIndex(item => item.needId === needId && !item.hasResponse)
      if (index !== -1) {
        this.needList.splice(index, 1)
        localStorage.setItem('mockNeedList', JSON.stringify(this.needList))
        return true
      }
      return false
    },
    updateNeed(needId, updatedData) {
      const index = this.needList.findIndex(item => item.needId === needId && !item.hasResponse)
      if (index !== -1) {
        this.needList[index] = {
          ...this.needList[index],
          ...updatedData,
          updateTime: new Date().toLocaleDateString()
        }
        localStorage.setItem('mockNeedList', JSON.stringify(this.needList))
        return true
      }
      return false
    },
    cancelNeed(needId) {
      const index = this.needList.findIndex(item => item.needId === needId && item.status === '0')
      if (index !== -1) {
        this.needList[index].status = '1'
        this.needList[index].updateTime = new Date().toLocaleDateString()
        localStorage.setItem('mockNeedList', JSON.stringify(this.needList))
        return true
      }
      return false
    },

    //新增服务自荐
    addServiceSelf(serviceData) {
      let maxId = 0
      this.serviceSelfList.forEach(item => {
        const idNum = parseInt(item.serviceId.replace('service_', ''))
        if (!isNaN(idNum) && idNum > maxId) {
          maxId = idNum
        }
      })
      const newServiceId = `service_${maxId + 1}`

      const newService = {
        serviceId: newServiceId,
        needId: serviceData.needId,
        userId: this.userInfo.userId,
        serviceType: serviceData.serviceType,
        title: serviceData.title,
        content: serviceData.content || '',
        createTime: new Date().toLocaleString(),
        updateTime: new Date().toLocaleString(),
        status: 0 // 默认未被接受
      }
      this.serviceSelfList.push(newService)
      localStorage.setItem('mockServiceSelfList', JSON.stringify(this.serviceSelfList))
      return newService
    },

    //删除服务自荐
    deleteServiceSelf(serviceId) {
      const index = this.serviceSelfList.findIndex(item => item.serviceId === serviceId && item.status === 0)
      if (index !== -1) {
        this.serviceSelfList.splice(index, 1)
        localStorage.setItem('mockServiceSelfList', JSON.stringify(this.serviceSelfList))
        return true
      }
      return false
    },

    //修改服务自荐
    updateServiceSelf(serviceId, updatedData) {
      const index = this.serviceSelfList.findIndex(item => item.serviceId === serviceId && item.status === 0)
      if (index !== -1) {
        this.serviceSelfList[index] = {
          ...this.serviceSelfList[index],
          ...updatedData,
          updateTime: new Date().toLocaleString()
        }
        localStorage.setItem('mockServiceSelfList', JSON.stringify(this.serviceSelfList))
        return true
      }
      return false
    },

    //标记服务自荐为已接受
    acceptServiceSelf(serviceId) {
      const index = this.serviceSelfList.findIndex(item => item.serviceId === serviceId)
      if (index !== -1) {
        this.serviceSelfList[index].status = 1
        this.serviceSelfList[index].updateTime = new Date().toLocaleString()
        localStorage.setItem('mockServiceSelfList', JSON.stringify(this.serviceSelfList))
        return true
      }
      return false
    }
  },
  //计算当前用户的服务自荐列表
  getters: {
    myServiceSelfList: (state) => {
      // 防止未登录时报错
      if (!state.userInfo || !state.userInfo.userId) return []
      return state.serviceSelfList.filter(item => item.userId === state.userInfo.userId)
    }
  }
})