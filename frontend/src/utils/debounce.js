/**
 * 防抖节流工具函数
 * 用于优化高频事件处理
 */

/**
 * 防抖函数
 * 延迟执行函数，在指定时间内再次触发会重新计时
 * 
 * @param {Function} fn - 需要防抖的函数
 * @param {number} delay - 延迟时间（毫秒）
 * @param {boolean} immediate - 是否立即执行
 * @returns {Function} - 防抖后的函数
 */
export function debounce(fn, delay = 300, immediate = false) {
  let timer = null
  
  return function(...args) {
    const context = this
    
    // 立即执行
    if (immediate && !timer) {
      fn.apply(context, args)
    }
    
    // 清除之前的定时器
    if (timer) {
      clearTimeout(timer)
    }
    
    // 设置新的定时器
    timer = setTimeout(() => {
      if (!immediate) {
        fn.apply(context, args)
      }
      timer = null
    }, delay)
  }
}

/**
 * 节流函数
 * 限制函数执行频率，在指定时间内只执行一次
 * 
 * @param {Function} fn - 需要节流的函数
 * @param {number} limit - 限制时间（毫秒）
 * @returns {Function} - 节流后的函数
 */
export function throttle(fn, limit = 200) {
  let inThrottle = false
  
  return function(...args) {
    const context = this
    
    if (!inThrottle) {
      fn.apply(context, args)
      inThrottle = true
      
      setTimeout(() => {
        inThrottle = false
      }, limit)
    }
  }
}

/**
 * 防抖 Promise 版本
 * 返回 Promise 的防抖函数
 * 
 * @param {Function} fn - 需要防抖的函数（返回 Promise）
 * @param {number} delay - 延迟时间（毫秒）
 * @returns {Function} - 防抖后的函数
 */
export function debounceAsync(fn, delay = 300) {
  let timer = null
  let lastPromise = null
  
  return function(...args) {
    const context = this
    
    // 如果有定时器，清除它
    if (timer) {
      clearTimeout(timer)
    }
    
    return new Promise((resolve, reject) => {
      timer = setTimeout(async () => {
        try {
          const result = await fn.apply(context, args)
          resolve(result)
        } catch (error) {
          reject(error)
        }
        timer = null
      }, delay)
    })
  }
}

/**
 * 请求防抖
 * 用于 API 请求的防抖，避免重复请求
 * 
 * @param {Function} fn - API 请求函数（返回 Promise）
 * @param {number} delay - 延迟时间（毫秒）
 * @returns {Function} - 防抖后的函数
 */
export function requestDebounce(fn, delay = 500) {
  let timer = null
  let pendingPromise = null
  
  return function(...args) {
    const context = this
    
    // 如果有定时器，清除它
    if (timer) {
      clearTimeout(timer)
    }
    
    // 如果有挂起的请求，直接返回它
    if (pendingPromise) {
      return pendingPromise
    }
    
    return new Promise((resolve, reject) => {
      timer = setTimeout(async () => {
        try {
          const result = await fn.apply(context, args)
          resolve(result)
        } catch (error) {
          reject(error)
        } finally {
          pendingPromise = null
          timer = null
        }
      }, delay)
    })
  }
}

export default {
  debounce,
  throttle,
  debounceAsync,
  requestDebounce
}
