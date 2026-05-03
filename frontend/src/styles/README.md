# 全局样式系统

## 📁 文件结构

```
src/styles/
├── global.css              # 全局样式入口（统一导入）
├── variables.css           # CSS 变量和主题定义
├── animations.css          # 动画和过渡效果
├── layout.css             # 布局相关样式（背景、粒子、主布局等）
├── components.css         # 组件级别样式（检测器、统计卡片等）
├── pages.css              # 页面级别样式（主题页、设置页等）
├── element-overwatch.css  # Element Plus 组件覆盖样式
└── index.js               # 样式模块导出（可选）
```

## 🎯 设计理念

### 1. **集中管理**
- 所有样式集中在 `src/styles/` 目录
- 避免样式分散在各个组件中导致的冲突和维护困难
- 单一入口 `global.css`，在 `main.js` 中统一导入

### 2. **模块化组织**
- **variables.css**: 设计令牌（颜色、圆角、过渡时间等）
- **animations.css**: 所有动画定义（fadeIn、pulseGlow 等）
- **layout.css**: 全局布局和背景样式
- **components.css**: 通用组件样式（可复用）
- **pages.css**: 页面特定样式（主题页、设置页等）
- **element-overwatch.css**: Element Plus 主题覆盖

### 3. **CSS 变量驱动**
- 所有颜色使用 CSS 变量（如 `var(--primary)`）
- 主题切换时只需更新 CSS 变量值
- 避免硬编码颜色，确保一致性

### 4. **Element Plus 兼容**
- 保留 Element Plus 组件库
- 通过 `element-overrides.css` 完全覆盖默认样式
- 确保 Element Plus 组件跟随主题切换

## 🔧 使用方法

### 在 main.js 中导入

```javascript
import './styles/global.css'
```

### 添加新样式

1. **判断样式类型**：
   - 全局变量 → `variables.css`
   - 动画定义 → `animations.css`
   - 布局相关 → `layout.css`
   - 通用组件 → `components.css`
   - 页面特定 → `pages.css`
   - Element Plus 覆盖 → `element-overwatch.css`

2. **添加到对应文件**

3. **在 `global.css` 中确认已导入**（通常自动完成）

### 修改主题色

直接修改 `variables.css` 中的 CSS 变量：

```css
:root {
  --primary: #7139FF;
  --background: #05020A;
  /* ... */
}
```

## ✨ 优势

### 1. **消除闪烁问题**
- ✅ 所有样式在页面加载时一次性应用
- ✅ 避免组件挂载时的样式跳变
- ✅ 主题切换平滑流畅

### 2. **易于维护**
- ✅ 样式集中管理，查找方便
- ✅ 模块化组织，职责清晰
- ✅ CSS 变量统一管理，修改一处生效全局

### 3. **性能优化**
- ✅ 减少重复样式代码
- ✅ 浏览器缓存单个 CSS 文件
- ✅ 避免多个 `<style>` 标签的解析开销

### 4. **开发体验**
- ✅ 统一的样式规范
- ✅ 清晰的模块划分
- ✅ 便于团队协作

## 📝 注意事项

1. **不要在各组件中使用 `<style scoped>`**
   - 所有样式应添加到全局样式文件中
   - 使用语义化的类名避免冲突

2. **优先使用 CSS 变量**
   - 不要硬编码颜色值
   - 使用 `var(--primary)` 而非 `#7139FF`

3. **保持模块化**
   - 根据样式类型选择正确的文件
   - 不要在 `layout.css` 中添加组件样式

4. **Element Plus 覆盖**
   - 所有 Element Plus 样式覆盖放在 `element-overwatch.css`
   - 使用 `!important` 确保优先级

## 🚀 迁移指南

如果之前有组件使用了 `<style scoped>`，迁移步骤：

1. 提取样式到对应的全局样式文件
2. 确保类名具有唯一性（如 `.theme-page` 而非 `.page`）
3. 删除组件中的 `<style>` 标签
4. 测试样式是否正常应用

## 📊 当前状态

- ✅ 全局样式系统已建立
- ✅ App.vue 样式已迁移
- ✅ Element Plus 覆盖已完成
- ✅ 主题切换无闪烁
- ✅ 所有组件使用全局样式
