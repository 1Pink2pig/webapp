import axios from 'axios'
import { ElMessage } from 'element-plus'

/**
 * 密码验证规则：不少于6位、含2个数字、不都为大小写
 * @param {string} password - 密码
 * @returns {Promise<boolean>} 验证结果
 */


export const validatePassword = (password) =>
{
  // 长度不少于6位
  if (password.length < 6) return false
  // 包含至少2个数字
  const digitCount = password.match(/\d/g)?.length || 0
  if (digitCount < 2) return false
  // 不都为大写且不都为小写
  const isAllUpper = password === password.toUpperCase()
  const isAllLower = password === password.toLowerCase()
  if (isAllUpper || isAllLower) return false
  return true
}

/**
 * 手机号验证规则：11位数字
 * @param {string} phone - 手机号
 * @returns {boolean} 验证结果
 */
export const validatePhone = (phone) =>
{
  return /^1\d{10}$/.test(phone)
}

/**
 * 用户名验证规则：非空且不重复
 * @param {string} username - 用户名
 * @param {boolean} isMock - 是否本地模拟（true=查localStorage，false=调后端接口）
 * @returns {Promise<boolean>} 验证结果（异步返回：true=唯一，false=重复）
 */
export const validateUsernameUnique = async (username, isMock) =>
{
    if (isMock)
    {
        const mockUsers = JSON.parse(localStorage.getItem('mockUsers') || '[]')
        return !mockUsers.some(u => u.username === username)
    }
  //对接后端模式
    try
    {
        // 调用后端
        const response = await axios.get(
        'http://127.0.0.1:8000/api/check-username',
        { params: { username } } )

        const res = response.data
        if (res.code === 200)
        {
            return res.data.isUnique
        }
        else
        {
            ElMessage.warning(res.msg || '用户名重复')
            return false
        }
    }
    catch (error)
    {
        // 捕获网络错误/后端服务未启动等异常
        console.error('调用用户名查重接口失败：', error)
        ElMessage.error('网络异常，无法校验用户名是否重复')
        return false
    }
}