<template>
  <el-pagination
    @size-change="handleSizeChange"
    @current-change="handleCurrentChange"
    :current-page="props.currentPage"
    :page-sizes="[5, 10, 20, 50]"
    :page-size="props.pageSize"
    layout="total, sizes, prev, pager, next, jumper"
    :total="props.total"
    class="pagination"
  />
</template>

<script setup name="BasePagination">
import { defineProps, defineEmits } from 'vue'

const props = defineProps({
  currentPage: { type: Number, default: 1 },
  pageSize: { type: Number, default: 10 },
  total: { type: Number, default: 0 }
})

const emits = defineEmits(['size-change', 'current-change'])

const handleSizeChange = (val) => {
  emits('size-change', val)
}

const handleCurrentChange = (val) => {
  emits('current-change', val)
}
</script>

<style scoped>
.pagination {
  margin-top: 20px;
  text-align: center;
}
</style>