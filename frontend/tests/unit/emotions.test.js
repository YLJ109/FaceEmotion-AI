/**
 * 情绪常量单元测试
 */

import { describe, it, expect } from 'vitest'
import { 
  EMOTION_KEYS, 
  EMOTION_NAME_MAP, 
  EMOTION_COLOR_MAP,
  getEmotionName,
  getEmotionColor,
  getEmotionIndex 
} from '@/constants/emotions'

describe('Emotion Constants', () => {
  describe('EMOTION_KEYS', () => {
    it('should contain exactly 7 emotions', () => {
      expect(EMOTION_KEYS.length).toBe(7)
    })

    it('should contain all expected emotion keys', () => {
      expect(EMOTION_KEYS).toContain('happy')
      expect(EMOTION_KEYS).toContain('sad')
      expect(EMOTION_KEYS).toContain('angry')
      expect(EMOTION_KEYS).toContain('surprise')
      expect(EMOTION_KEYS).toContain('fear')
      expect(EMOTION_KEYS).toContain('disgust')
      expect(EMOTION_KEYS).toContain('neutral')
    })
  })

  describe('EMOTION_NAME_MAP', () => {
    it('should have entries for all emotion keys', () => {
      EMOTION_KEYS.forEach(key => {
        expect(EMOTION_NAME_MAP).toHaveProperty(key)
      })
    })

    it('should map to correct Chinese names', () => {
      expect(EMOTION_NAME_MAP['happy']).toBe('开心')
      expect(EMOTION_NAME_MAP['sad']).toBe('悲伤')
      expect(EMOTION_NAME_MAP['angry']).toBe('愤怒')
      expect(EMOTION_NAME_MAP['surprise']).toBe('惊讶')
      expect(EMOTION_NAME_MAP['fear']).toBe('恐惧')
      expect(EMOTION_NAME_MAP['disgust']).toBe('厌恶')
      expect(EMOTION_NAME_MAP['neutral']).toBe('平静')
    })
  })

  describe('EMOTION_COLOR_MAP', () => {
    it('should have entries for all emotion keys', () => {
      EMOTION_KEYS.forEach(key => {
        expect(EMOTION_COLOR_MAP).toHaveProperty(key)
      })
    })

    it('should contain valid hex color values', () => {
      EMOTION_KEYS.forEach(key => {
        const color = EMOTION_COLOR_MAP[key]
        expect(color).toMatch(/^#[0-9A-Fa-f]{6}$/)
      })
    })
  })

  describe('getEmotionName', () => {
    it('should return correct Chinese name for valid key', () => {
      expect(getEmotionName('happy')).toBe('开心')
      expect(getEmotionName('sad')).toBe('悲伤')
      expect(getEmotionName('surprise')).toBe('惊讶')
    })

    it('should return original key for invalid key', () => {
      expect(getEmotionName('unknown')).toBe('unknown')
    })
  })

  describe('getEmotionColor', () => {
    it('should return correct color for valid key', () => {
      expect(getEmotionColor('happy')).toBe('#10B981')
      expect(getEmotionColor('angry')).toBe('#EF4444')
    })

    it('should return default color for invalid key', () => {
      expect(getEmotionColor('unknown')).toBe('#6B7280')
    })
  })

  describe('getEmotionIndex', () => {
    it('should return correct index for valid key', () => {
      expect(getEmotionIndex('happy')).toBe(0)
      expect(getEmotionIndex('sad')).toBe(1)
      expect(getEmotionIndex('neutral')).toBe(6)
    })

    it('should return -1 for invalid key', () => {
      expect(getEmotionIndex('unknown')).toBe(-1)
    })
  })
})
