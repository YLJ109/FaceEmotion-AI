/**
 * 防抖节流工具单元测试
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { debounce, throttle, debounceAsync, requestDebounce } from '@/utils/debounce'

describe('Debounce & Throttle', () => {
  beforeEach(() => {
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.useRealTimers()
    vi.clearAllMocks()
  })

  describe('debounce', () => {
    it('should delay function execution', () => {
      const fn = vi.fn()
      const debouncedFn = debounce(fn, 100)

      debouncedFn()
      expect(fn).not.toHaveBeenCalled()

      vi.advanceTimersByTime(100)
      expect(fn).toHaveBeenCalledTimes(1)
    })

    it('should reset timer when called multiple times', () => {
      const fn = vi.fn()
      const debouncedFn = debounce(fn, 100)

      debouncedFn()
      debouncedFn()
      debouncedFn()

      vi.advanceTimersByTime(50)
      expect(fn).not.toHaveBeenCalled()

      vi.advanceTimersByTime(60)
      expect(fn).toHaveBeenCalledTimes(1)
    })

    it('should execute immediately when immediate is true', () => {
      const fn = vi.fn()
      const debouncedFn = debounce(fn, 100, true)

      debouncedFn()
      expect(fn).toHaveBeenCalledTimes(1)

      vi.advanceTimersByTime(100)
      expect(fn).toHaveBeenCalledTimes(1)
    })

    it('should maintain correct this context', () => {
      const obj = {
        value: 42,
        getValue: function() {
          return this.value
        }
      }
      const debouncedGet = debounce(obj.getValue.bind(obj), 100)

      let result
      const fn = vi.fn(() => {
        result = debouncedGet()
      })

      fn()
      vi.advanceTimersByTime(100)

      expect(result).toBe(42)
    })
  })

  describe('throttle', () => {
    it('should limit function execution frequency', () => {
      const fn = vi.fn()
      const throttledFn = throttle(fn, 100)

      throttledFn()
      throttledFn()
      throttledFn()

      expect(fn).toHaveBeenCalledTimes(1)

      vi.advanceTimersByTime(100)
      throttledFn()

      expect(fn).toHaveBeenCalledTimes(2)
    })

    it('should execute immediately on first call', () => {
      const fn = vi.fn()
      const throttledFn = throttle(fn, 100)

      throttledFn()
      expect(fn).toHaveBeenCalledTimes(1)
    })

    it('should maintain correct this context', () => {
      const obj = {
        value: 42,
        getValue: function() {
          return this.value
        }
      }
      const throttledGet = throttle(obj.getValue.bind(obj), 100)

      let result
      throttledGet()
      result = throttledGet()

      expect(result).toBe(42)
    })
  })

  describe('debounceAsync', () => {
    it('should return a promise that resolves after delay', async () => {
      const fn = vi.fn().mockResolvedValue('result')
      const debouncedFn = debounceAsync(fn, 100)

      const promise = debouncedFn()
      
      vi.advanceTimersByTime(100)
      
      const result = await promise
      expect(result).toBe('result')
      expect(fn).toHaveBeenCalledTimes(1)
    })

    it('should reset timer when called multiple times', async () => {
      const fn = vi.fn().mockResolvedValue('result')
      const debouncedFn = debounceAsync(fn, 100)

      debouncedFn()
      debouncedFn()
      
      vi.advanceTimersByTime(50)
      expect(fn).not.toHaveBeenCalled()
      
      vi.advanceTimersByTime(60)
      expect(fn).toHaveBeenCalledTimes(1)
    })
  })

  describe('requestDebounce', () => {
    it('should prevent duplicate API calls', async () => {
      const fn = vi.fn().mockResolvedValue('response')
      const debouncedFn = requestDebounce(fn, 100)

      const promise1 = debouncedFn()
      const promise2 = debouncedFn()
      const promise3 = debouncedFn()

      // 所有调用应该共享同一个promise
      expect(promise1).toBe(promise2)
      expect(promise2).toBe(promise3)

      vi.advanceTimersByTime(100)
      
      const result = await promise1
      expect(result).toBe('response')
      expect(fn).toHaveBeenCalledTimes(1)
    })
  })
})
