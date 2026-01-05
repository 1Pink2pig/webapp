<template>
  <div class="home-page">
    <el-card class="home-card" shadow="hover">
      <!-- 欢迎语区域 -->
      <div class="welcome-wrap">
        <h1 class="welcome-title">欢迎使用好服务系统</h1>
        <p class="welcome-desc">用心服务，便捷生活，您的需求我们来满足～</p>
        <div class="home-img">
          <img
            src="@/assets/homepicture.png"
            alt="服务banner"
            loading="lazy"
          />
        </div>

        <!-- 服务分类模块 -->
        <div class="category-wrap">
          <h2 class="category-title">核心服务分类</h2>
          <div class="category-list">
            <!-- 居家维修 -->
            <div class="category-item" @click="goToCategory('居家维修')">
              <el-icon class="category-icon"><Tools /></el-icon>
              <span>居家维修</span>
            </div>
            <!-- 生活照料 -->
            <div class="category-item" @click="goToCategory('生活照料')">
              <el-icon class="category-icon"><UserFilled /></el-icon>
              <span>生活照料</span>
            </div>
            <!-- 清洁保洁 -->
            <div class="category-item" @click="goToCategory('清洁保洁')">
              <el-icon class="category-icon"><Brush /></el-icon>
              <span>清洁保洁</span>
            </div>
            <!-- 出行就医 -->
            <div class="category-item" @click="goToCategory('出行就医')">
              <el-icon class="category-icon"><Van /></el-icon>
              <span>出行就医</span>
            </div>
            <!-- 餐食服务 -->
            <div class="category-item" @click="goToCategory('餐食服务')">
              <el-icon class="category-icon"><Food /></el-icon>
              <span>餐食服务</span>
            </div>
            <!-- 其它 -->
            <div class="category-item" @click="goToCategory('其它')">
              <el-icon class="category-icon"><MoreFilled /></el-icon>
              <span>其它</span>
            </div>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Tools, UserFilled, Brush, Van, Food, MoreFilled } from '@element-plus/icons-vue'

const router = useRouter()

// 分类跳转方法
const goToCategory = (categoryName) => {
  try {
    // 跳转到MyServiceList，携带分类参数 type
    router.push({
      name: 'MyServiceList',
      query: { type: categoryName } // 传递分类参数，供 ServiceList 页面筛选数据
    })

    ElMessage.success(`已为您筛选【${categoryName}】类服务`)
  } catch (error) {
    ElMessage.error(`跳转失败：${error.message || '请检查路由配置'}`)
  }
}
</script>

<style scoped>

.home-page {
  width: 100%;
  min-height: 100vh;
  padding: 20px;
  box-sizing: border-box;
  background-color: #BFD7EA;
  display: flex;
  justify-content: center;
  align-items: center;
}

/* 卡片容器 */
.home-card {
  width: 80%;
  max-width: 1200px;
  max-height: 80vh;
  padding: 50px;
  text-align: center;
  background-color: #fff;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  border-radius: 0;
}

/* 欢迎语样式 */
.welcome-title {
  font-size: 36px;
  color: #79B0D9;
  margin: 0 0 20px 0;
  font-weight: 900;
}
.welcome-desc {
  font-size: 18px;
  color: #79B0D9;
  opacity: 0.8;
  margin: 0 0 30px 0;
  line-height: 1.5;
}

/* 图片 */
.home-img {
  margin-bottom: 30px;
}
.home-img img {
  max-width: 65%;
  border-radius: 0;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}
.home-img img:hover {
  transform: scale(1.02);
}

/* 服务分类模块 */
.category-wrap {
  margin-top: 30px;
  padding-top: 25px;
  border-top: 1px solid #BFD7EA;
}
.category-title {
  font-size: 24px;
  color: #79B0D9;
  margin: 0 0 30px 0;
  font-weight: 900;
}
.category-list {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 30px;
}
.category-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 110px;
  cursor: pointer;
  padding: 20px 15px;
  border-radius: 0;
  transition: all 0.3s ease;
  background-color: #BFD7EA;
}
.category-item:hover {
  background-color: #79B0D9;
  transform: translateY(-4px);
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}
.category-icon {
  font-size: 40px;
  color: #fff;
  margin-bottom: 12px;
}
.category-item span {
  font-size: 15px;
  color: #fff;
  font-weight: 500;
}

.category-item:hover .category-icon,
.category-item:hover span {
  color: #fff;
}

</style>