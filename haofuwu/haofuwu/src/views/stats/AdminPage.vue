<template>
  <div class="stats-page-container">
    <el-card class="stats-card">
      <!-- 顶部标题 + 退出按钮 -->
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px;">
        <h2 class="stats-title" style="margin: 0;">管理端统计页面</h2>
        <el-button
          type="primary"
          @click="handleLogout"
          style="background-color: #9A7B68; border-color: #9A7B68;"
        >
          退出登录
        </el-button>
      </div>

      <!-- 筛选条件区域 -->
      <div class="filter-form">
        <el-form :model="filterForm" inline @submit.prevent="fetchStatsData">
          <el-form-item label="起始年月">
            <el-date-picker
              v-model="filterForm.startMonth"
              type="month"
              placeholder="选择起始年月"
              format="YYYY-MM"
              value-format="YYYY-MM"
              :disabled-date="disabledPastDate"
              style="width: 200px;"
            ></el-date-picker>
          </el-form-item>
          <el-form-item label="终止年月">
            <el-date-picker
              v-model="filterForm.endMonth"
              type="month"
              placeholder="选择终止年月"
              format="YYYY-MM"
              value-format="YYYY-MM"
              :disabled-date="disabledPastDate"
              style="width: 200px;"
            ></el-date-picker>
          </el-form-item>
          <el-form-item label="服务地域">
            <!-- 按回车可触发查询 -->
            <el-input
              v-model="filterForm.region"
              placeholder="请输入服务地域关键词搜索（如：东城、海淀）"
              clearable
              style="width: 280px;"
              @keyup.enter="fetchStatsData"
            ></el-input>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="fetchStatsData" class="query-btn">查询</el-button>
            <el-button @click="resetFilter" class="reset-btn">重置</el-button>
          </el-form-item>
        </el-form>
      </div>

      <!-- 统计概览 -->
      <div class="stats-overview">
        <el-row :gutter="20">
          <el-col :span="6">
            <div class="overview-item">
              <p class="overview-label">累计发布需求数</p>
              <p class="overview-value">{{ overviewData.totalNeed }}</p>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="overview-item">
              <p class="overview-label">累计响应成功数</p>
              <p class="overview-value">{{ overviewData.totalServiceSuccess }}</p>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="overview-item">
              <p class="overview-label">查询时间段</p>
              <p class="overview-value">{{ filterForm.startMonth || '近6个月' }} - {{ filterForm.endMonth || '当前月' }}</p>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="overview-item">
              <p class="overview-label">查询地域</p>
              <p class="overview-value">{{ filterForm.region || '全部地域' }}</p>
            </div>
          </el-col>
        </el-row>
      </div>

      <!-- 统计列表 -->
      <div class="stats-table">
        <h3 class="table-title">按年月/地域统计明细</h3>
        <el-table :data="statsTableData" border stripe style="width: 100%">
          <el-table-column prop="month" label="统计年月" align="center"></el-table-column>
          <el-table-column prop="region" label="服务地域" align="center"></el-table-column>
          <el-table-column prop="monthNeedCount" label="月累计发布需求数" align="center"></el-table-column>
          <el-table-column prop="monthServiceSuccessCount" label="月累计响应成功数" align="center"></el-table-column>
          <el-table-column prop="cumulativeNeedCount" label="累计发布需求数" align="center"></el-table-column>
          <el-table-column prop="cumulativeServiceSuccessCount" label="累计响应成功数" align="center"></el-table-column>
        </el-table>
      </div>

      <!-- 图表区域 -->
      <div class="charts-container">
        <div class="chart-item">
          <h3 class="chart-title">月度累计需求/响应成功数趋势</h3>
          <div id="monthTrendChart" class="chart-box"></div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useUserStore } from '@/store/userStore'
import { useRouter } from 'vue-router'
import * as echarts from 'echarts'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'

const isMock = false

const router = useRouter()
const userStore = useUserStore()
let monthTrendChart = null

const handleLogout = async () => {
  try {
    const result = await ElMessageBox.confirm(
      '确定要退出登录吗？',
      '退出确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'info'
      }
    )

    if (result === 'confirm') {
      userStore.$reset()
      localStorage.clear()
      sessionStorage.clear()
      await router.replace({ path: '/login' })
      window.location.reload()
      ElMessage.success('退出登录成功')
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('退出登录失败，请重试')
      console.error('退出登录错误：', error)
      router.replace('/login')
      window.location.reload()
    }
  }
}

// 筛选表单数据（默认近6个月）
const filterForm = ref({
  startMonth: '',
  endMonth: '',
  region: ''
})

// 统计概览数据
const overviewData = ref({
  totalNeed: 0,
  totalServiceSuccess: 0
})

// 统计列表数据
const statsTableData = ref([])

// 禁用未来日期
const disabledPastDate = (date) => {
  return date > new Date()
}

// 初始化默认时间（近6个月）
const initDefaultTime = () => {
  const now = new Date()
  const endMonth = now.getFullYear() + '-' + (now.getMonth() + 1).toString().padStart(2, '0')
  const startMonth = new Date(now.setMonth(now.getMonth() - 5)).getFullYear() + '-' + (now.getMonth() + 1).toString().padStart(2, '0')

  filterForm.value.startMonth = startMonth
  filterForm.value.endMonth = endMonth
}

// 重置筛选条件
const resetFilter = () => {
  filterForm.value = {
    startMonth: '',
    endMonth: '',
    region: ''
  }
  initDefaultTime()
  fetchStatsData()
}

//后端
const apiGetStatsData = async (params) => {
  try {
    const baseUrl = process.env.VUE_APP_API_BASE_URL || 'http://127.0.0.1:8000'
    const res = await axios.post(
      `${baseUrl}/api/admin/stats`,
      params,
      {
        headers: {
          'Authorization': `Bearer ${userStore.userInfo.token || ''}`,
          'Content-Type': 'application/json'
        },
        timeout: 10000
      }
    )
    if (res.data.code === 200) {
      return res.data.data
    } else {
      ElMessage.error(`获取统计数据失败：${res.data.msg || '接口返回异常'}`)
      return null
    }
  } catch (error) {
    console.error('后端统计接口请求失败：', error)
    if (error.code === 'ECONNABORTED') {
      ElMessage.error('请求超时：请检查后端服务器是否启动')
    } else if (error.response) {
      ElMessage.error(`后端报错[${error.response.status}]：${error.response.data?.msg || '统计数据获取失败'}`)
    } else {
      ElMessage.error('网络异常：无法连接后端服务器')
    }
    return null
  }
}

//本地测试
const generateMockStatsData = (startMonth, endMonth, regionKeyword) => {
  // 生成多地域的基础数据（包含北京各城区，模拟真实场景）
  const regions = ['东城区', '西城区', '朝阳区', '海淀区', '丰台区', '石景山区', '通州区', '昌平区']
  const baseMonths = []
  const now = new Date()

  // 生成近12个月 + 多地域的基础数据
  for (let i = 11; i >= 0; i--) {
    const tempDate = new Date(now.getFullYear(), now.getMonth() - i, 1)
    const monthStr = tempDate.getFullYear() + '-' + (tempDate.getMonth() + 1).toString().padStart(2, '0')

    // 每个月为不同地域生成数据
    regions.forEach(region => {
      const monthNeed = Math.floor(Math.random() * 20) + 5 // 5-25之间随机
      const monthService = Math.floor(Math.random() * (monthNeed - 2)) + 3 // 小于需求数，3-23之间
      baseMonths.push({
        month: monthStr,
        region: region,
        monthNeedCount: monthNeed,
        monthServiceSuccessCount: monthService,
        cumulativeNeedCount: 0,
        cumulativeServiceSuccessCount: 0
      })
    })
  }

  //筛选时间范围
  let filteredData = baseMonths
  if (startMonth && endMonth) {
    filteredData = baseMonths.filter(item => {
      return item.month >= startMonth && item.month <= endMonth
    })
  } else {
    // 默认取近6个月
    filteredData = baseMonths.filter(item => {
      const monthDate = new Date(item.month + '-01')
      const sixMonthsAgo = new Date(now.setMonth(now.getMonth() - 5))
      return monthDate >= sixMonthsAgo
    })
  }

  //筛选地域
  if (regionKeyword) {
    const keyword = regionKeyword.toLowerCase()
    filteredData = filteredData.filter(item => {
      return item.region.toLowerCase().includes(keyword)
    })
  }

  // 按年月+地域分组，汇总数据
  const groupedData = {}
  filteredData.forEach(item => {
    const key = `${item.month}_${item.region}`
    if (!groupedData[key]) {
      groupedData[key] = {
        month: item.month,
        region: item.region,
        monthNeedCount: item.monthNeedCount,
        monthServiceSuccessCount: item.monthServiceSuccessCount,
        cumulativeNeedCount: 0,
        cumulativeServiceSuccessCount: 0
      }
    } else {
      // 同一年月+地域去重
      groupedData[key].monthNeedCount += item.monthNeedCount
      groupedData[key].monthServiceSuccessCount += item.monthServiceSuccessCount
    }
  })

  // 转换为数组并计算累计数
  const resultList = Object.values(groupedData)
  // 按年月排序
  resultList.sort((a, b) => new Date(a.month) - new Date(b.month))

  // 计算累计数（按时间顺序）
  const monthCumulativeMap = {} // 记录每个年月的累计值
  resultList.forEach(item => {
    const monthKey = item.month
    // 初始化该年月的累计值
    if (!monthCumulativeMap[monthKey]) {
      monthCumulativeMap[monthKey] = {
        need: 0,
        service: 0
      }
      // 累加之前所有年月的累计值
      const prevMonths = Object.keys(monthCumulativeMap).filter(m => new Date(m) < new Date(monthKey))
      prevMonths.forEach(m => {
        monthCumulativeMap[monthKey].need += monthCumulativeMap[m].need
        monthCumulativeMap[monthKey].service += monthCumulativeMap[m].service
      })
    }
    // 累加当前月数据
    monthCumulativeMap[monthKey].need += item.monthNeedCount
    monthCumulativeMap[monthKey].service += item.monthServiceSuccessCount
    // 赋值给当前项
    item.cumulativeNeedCount = monthCumulativeMap[monthKey].need
    item.cumulativeServiceSuccessCount = monthCumulativeMap[monthKey].service
  })

  // 总计
  const totalNeed = resultList.reduce((sum, item) => sum + item.monthNeedCount, 0)
  const totalServiceSuccess = resultList.reduce((sum, item) => sum + item.monthServiceSuccessCount, 0)

  return {
    list: resultList,
    totalNeed,
    totalServiceSuccess
  }
}


const fetchStatsData = async () => {
  if (filterForm.value.startMonth && filterForm.value.endMonth) {
    if (new Date(filterForm.value.startMonth) > new Date(filterForm.value.endMonth)) {
      ElMessage.warning('起始年月不能晚于终止年月')
      return
    }
  }

  let statsData = null
  const params = {
    startMonth: filterForm.value.startMonth,
    endMonth: filterForm.value.endMonth,
    regionKeyword: filterForm.value.region // 传递地域搜索关键词
  }

  if (isMock) {
    statsData = generateMockStatsData(params.startMonth, params.endMonth, params.regionKeyword)
  } else {
    statsData = await apiGetStatsData(params)
    if (!statsData) return // 接口失败则直接返回
  }

  // 更新页面数据
  statsTableData.value = statsData.list
  overviewData.value = {
    totalNeed: statsData.totalNeed,
    totalServiceSuccess: statsData.totalServiceSuccess
  }

  // 更新图表
  initTrendChart(statsData.list)
}

// 初始化趋势图表
const initTrendChart = (data) => {
  // 销毁原有图表
  if (monthTrendChart) {
    monthTrendChart.dispose()
  }

  // 按年月汇总图表数据（合并所有地域的当月数据）
  const monthMap = {}
  data.forEach(item => {
    if (!monthMap[item.month]) {
      monthMap[item.month] = {
        need: 0,
        service: 0
      }
    }
    monthMap[item.month].need += item.monthNeedCount
    monthMap[item.month].service += item.monthServiceSuccessCount
  })

  // 提取排序后的年月和对应数据
  const months = Object.keys(monthMap).sort((a, b) => new Date(a) - new Date(b))
  const needData = months.map(month => monthMap[month].need)
  const serviceData = months.map(month => monthMap[month].service)

  // 初始化图表
  monthTrendChart = echarts.init(document.getElementById('monthTrendChart'))
  monthTrendChart.setOption({
    backgroundColor: '#FFFFFF',
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' },
      textStyle: { fontSize: 12 }
    },
    legend: {
      data: ['月累计发布需求数', '月累计响应成功数'],
      top: 0,
      textStyle: { color: '#666' }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: months,
      axisLine: { lineStyle: { color: '#ddd' } },
      axisLabel: { color: '#666' }
    },
    yAxis: {
      type: 'value',
      min: 0,
      axisLine: { lineStyle: { color: '#ddd' } },
      axisLabel: { color: '#666' },
      splitLine: { lineStyle: { color: '#f5f5f5' } }
    },
    series: [
      {
        name: '月累计发布需求数',
        type: 'line',
        data: needData,
        smooth: true,
        itemStyle: { color: '#9A7B68' }, // 莫兰迪棕（主色）
        lineStyle: { width: 2 },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(154, 123, 104, 0.3)' },
            { offset: 1, color: 'rgba(154, 123, 104, 0.05)' }
          ])
        }
      },
      {
        name: '月累计响应成功数',
        type: 'line',
        data: serviceData,
        smooth: true,
        itemStyle: { color: '#79B0D9' }, // 莫兰迪蓝（辅助色）
        lineStyle: { width: 2 },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(121, 176, 217, 0.3)' },
            { offset: 1, color: 'rgba(121, 176, 217, 0.05)' }
          ])
        }
      }
    ]
  })

  // 自适应窗口大小
  window.addEventListener('resize', () => {
    monthTrendChart.resize()
  })
}

// 页面挂载初始化
onMounted(() => {
  // 校验管理员权限（双重保险）
  if (userStore.userInfo?.userType !== '系统管理员') {
    router.push('/login')
    return
  }

  // 初始化默认时间和数据
  initDefaultTime()
  fetchStatsData()
})

// 页面卸载销毁图表
onUnmounted(() => {
  if (monthTrendChart) {
    monthTrendChart.dispose()
  }
  window.removeEventListener('resize', () => {
    monthTrendChart.resize()
  })
})
</script>

<style scoped>

.stats-page-container {
  padding: 20px;
  background-color: #BFD7EA; /* 统一背景色 */
  min-height: 100vh;
}

.stats-card {
  max-width: 1400px;
  margin: 0 auto;
  padding: 30px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05) !important;
  border-radius: 12px !important;
  border: none !important;
  background-color: #FFFFFF !important;
}

/* 标题样式 */
.stats-title {
  text-align: center;
  color: #9A7B68;
  font-weight: 500;
  font-size: 24px;
}

/* 筛选表单 */
.filter-form {
  background-color: #F5F9FF;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
}

/* 统一筛选项高度对齐 */
:deep(.el-form-item__content) {
  display: flex;
  align-items: center;
}

.query-btn {
  background-color: #9A7B68 !important;
  border-color: #9A7B68 !important;
  border-radius: 8px !important;
  width: 100px;
  margin-right: 10px;
}

.reset-btn {
  border-radius: 8px !important;
  width: 100px;
}

/* 统计概览 */
.stats-overview {
  margin-bottom: 30px;
}

.overview-item {
  background-color: #F5F9FF; /* 浅蓝背景 */
  padding: 20px;
  border-radius: 8px;
  text-align: center;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
}

.overview-label {
  font-size: 16px;
  color: #666;
  margin-bottom: 10px;
}

.overview-value {
  font-size: 22px;
  font-weight: bold;
  color: #9A7B68; /* 莫兰迪主色 */
}

/* 统计列表 */
.stats-table {
  margin-bottom: 30px;
}

.table-title {
  font-size: 18px;
  color: #9A7B68;
  margin-bottom: 15px;
  text-align: left;
  font-weight: 500;
}

:deep(.el-table) {
  --el-table-header-text-color: #666;
  --el-table-row-hover-bg-color: #F5F9FF;
  --el-table-border-color: #ddd;
}

:deep(.el-table th) {
  background-color: #F5F9FF !important;
}

/* 图表区域 */
.charts-container {
  margin-top: 20px;
}

.chart-item {
  background-color: #fff;
  padding: 20px;
  border-radius: 8px;
  height: 450px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
}

.chart-title {
  font-size: 18px;
  color: #9A7B68;
  margin-bottom: 15px;
  text-align: center;
  font-weight: 500;
}

.chart-box {
  width: 100%;
  height: calc(100% - 40px);
}
</style>