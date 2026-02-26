# Plant Simulation 自动化建模工具 - 前端

这是一个基于 React + TypeScript + Ant Design 的工厂生产线模拟自动化建模工具前端。

## 功能特性

- 🎯 **自然语言输入**：通过自然语言描述生产线，自动生成有向图模型
- 📊 **可视化展示**：交互式有向图可视化，支持节点拖拽和属性查看
- 🔧 **模型确认**：可视化确认生产线模型，支持编辑和调整
- 💻 **代码生成**：自动生成 Plant Simulation 代码，支持下载和复制
- 📱 **响应式设计**：适配桌面和移动设备

## 项目结构

```
frontend/
├── src/
│   ├── components/          # 可复用组件
│   │   └── visualization/   # 可视化组件
│   ├── pages/              # 页面组件
│   ├── services/           # API服务
│   ├── stores/            # 状态管理
│   ├── types/             # TypeScript类型定义
│   ├── utils/             # 工具函数
│   ├── App.tsx            # 主应用组件
│   └── main.tsx           # 应用入口
├── public/                # 静态资源
├── index.html             # HTML模板
└── package.json          # 依赖配置
```

## 技术栈

- **React 18** - 前端框架
- **TypeScript** - 类型安全
- **Ant Design 5** - UI组件库
- **D3.js** - 数据可视化
- **Vite** - 构建工具
- **React Router** - 路由管理
- **Axios** - HTTP客户端

## 快速开始

### 安装依赖

```bash
npm install
```

### 开发模式

```bash
npm run dev
```

访问 http://localhost:3000

### 构建生产版本

```bash
npm run build
```

### 代码检查

```bash
npm run lint
```

## 使用流程

1. **输入描述**：在首页输入生产线自然语言描述
2. **生成模型**：系统自动生成有向图数据结构
3. **可视化确认**：查看并调整生产线有向图
4. **生成代码**：确认后生成 Plant Simulation 代码
5. **下载使用**：下载代码并在 Plant Simulation 中运行

## 与后端集成

前端通过 REST API 与后端通信：

- `POST /api/generate` - 从文本生成图数据
- `POST /api/confirm` - 确认图数据并生成代码
- `GET /api/examples` - 获取示例描述

## 开发说明

### 添加新页面

1. 在 `src/pages/` 创建页面组件
2. 在 `src/routes/index.tsx` 中添加路由
3. 在 `src/types/` 中添加相关类型定义

### 添加新组件

1. 在 `src/components/` 创建组件
2. 遵循组件化设计原则
3. 使用 TypeScript 定义 Props 接口

### 样式规范

- 使用 Ant Design 组件和主题
- 自定义样式放在 `src/App.css` 或组件内联样式
- 遵循响应式设计原则

## 部署

### 构建

```bash
npm run build
```

构建产物在 `dist/` 目录中。

### 服务配置

配置反向代理将 `/api` 请求转发到后端服务。

## 许可证

MIT