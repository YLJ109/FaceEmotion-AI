import { onUnmounted, ref } from 'vue'
import logger from '@/utils/logger'

export function useTimerScheduler() {
    const timers = new Map()
    const isPaused = ref(false)
    let timerIdCounter = 0

    const addInterval = (fn, interval, name = null) => {
        const id = name || `interval_${++timerIdCounter}`
        if (timers.has(id)) {
            logger.warn(`定时器 ${id} 已存在，先清除`)
            clearInterval(timers.get(id))
        }
        const handle = setInterval(() => {
            if (!isPaused.value) fn()
        }, interval)
        timers.set(id, handle)
        return id
    }

    const addTimeout = (fn, delay, name = null) => {
        const id = name || `timeout_${++timerIdCounter}`
        if (timers.has(id)) {
            clearTimeout(timers.get(id))
        }
        const handle = setTimeout(() => {
            timers.delete(id)
            if (!isPaused.value) fn()
        }, delay)
        timers.set(id, handle)
        return id
    }

    const remove = (id) => {
        if (timers.has(id)) {
            const handle = timers.get(id)
            clearInterval(handle)
            clearTimeout(handle)
            timers.delete(id)
        }
    }

    const removeAll = () => {
        timers.forEach((handle) => {
            clearInterval(handle)
            clearTimeout(handle)
        })
        timers.clear()
    }

    const pause = () => {
        isPaused.value = true
    }

    const resume = () => {
        isPaused.value = false
    }

    const has = (id) => timers.has(id)

    const count = () => timers.size

    onUnmounted(() => {
        removeAll()
    })

    return {
        isPaused,
        addInterval,
        addTimeout,
        remove,
        removeAll,
        pause,
        resume,
        has,
        count
    }
}