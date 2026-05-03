import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue({
      template: {
        compilerOptions: {
          // ✅ 允许运行时编译模板
          isCustomElement: (tag) => false
        }
      }
    })
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      // ✅ 修复: 使用包含编译器的完整 Vue 版本
      'vue': 'vue/dist/vue.esm-bundler.js'
    }
  }
})
