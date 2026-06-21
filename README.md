# 工业备件寄售库存管理系统

## 项目简介

工业备件寄售库存管理系统是一个全栈应用，用于管理工业备件的寄售库存，实现设备部门、供应商和财务三方共同确认库存归属，支持领用、补货、结算全流程管理。

## 技术栈

### 后端
- **框架**: FastAPI (Python)
- **ORM**: SQLAlchemy 2.0
- **数据库**: PostgreSQL
- **认证**: JWT (PyJWT)
- **密码加密**: bcrypt
- **数据验证**: Pydantic v2

### 前端
- **框架**: Vue 3 (Composition API)
- **语言**: TypeScript
- **UI组件库**: PrimeVue 3
- **状态管理**: Pinia
- **路由**: Vue Router 4
- **HTTP客户端**: Axios
- **构建工具**: Vite

## 核心业务功能

### 1. 库存归属三方确认
- 设备部门、供应商、财务三方共同确认库存归属
- 只有三方全部确认后，备件才能被领用
- 支持拒绝归属，重新协商

### 2. 维修单绑定领用
- 设备工程师必须绑定维修单才能领用备件
- 领用单必须选择已归属确认的批次
- 支持审批流程，审批通过后才能出库

### 3. 供应商补货管理
- 供应商创建补货单，维护批次信息
- 支持批次号、生产日期、失效日期、单价等信息
- 补货入库后自动更新库存

### 4. 财务结算管理
- 按实际领用数量结算
- 支持按期间、按供应商结算
- 结算状态跟踪（待审核、已审核、已付款）

### 5. 安全库存预警
- 实时监控库存水平
- 库存低于安全库存时自动创建预警
- 预警处理跟踪

### 6. 月结管理
- 月末结账功能
- 月结后期间的领用记录不能修改
- 支持反结账（限管理员）

### 7. 角色权限控制
- **设备工程师**: 创建维修单、领用备件、确认归属
- **供应商**: 管理补货、维护批次、确认归属
- **财务**: 结算管理、月结管理、确认归属
- **管理员**: 全部权限、用户管理、系统配置

## 数据库设计

### 核心表结构

| 表名 | 说明 |
|------|------|
| users | 用户表 |
| suppliers | 供应商表 |
| spare_parts | 备件表 |
| supplier_batches | 供应商批次表 |
| maintenance_orders | 维修单表 |
| requisitions | 领用单表 |
| requisition_items | 领用明细表 |
| replenishments | 补货单表 |
| replenishment_items | 补货明细表 |
| settlements | 结算单表 |
| stock_ownership_confirmations | 库存归属确认表 |
| monthly_closings | 月结记录表 |
| safety_stock_alerts | 安全库存预警表 |

## 快速开始

### 环境要求

- Python 3.11+
- Node.js 20+
- PostgreSQL 15+

### 方式一：Docker Compose（推荐）

```bash
# 启动所有服务
docker-compose up -d

# 初始化数据库
docker-compose exec backend python init_db.py

# 访问应用
# 前端: http://localhost:5173
# 后端API: http://localhost:8000
# API文档: http://localhost:8000/docs
```

### 方式二：手动安装

#### 后端安装

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，配置数据库连接

# 初始化数据库
python init_db.py

# 启动服务
uvicorn main:app --reload
```

#### 前端安装

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

## 默认测试账号

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 管理员 | admin | admin123 |
| 设备工程师 | engineer | engineer123 |
| 供应商 | supplier1 | supplier123 |
| 财务 | finance | finance123 |

## 目录结构

```
.
├── backend/                    # 后端代码
│   ├── app/
│   │   ├── routers/           # API路由
│   │   ├── config.py          # 配置
│   │   ├── database.py        # 数据库连接
│   │   ├── models.py          # 数据模型
│   │   ├── schemas.py         # Pydantic模式
│   │   ├── crud.py            # CRUD操作
│   │   └── security.py        # 安全认证
│   ├── main.py                # 应用入口
│   ├── init_db.py             # 数据库初始化
│   ├── requirements.txt       # Python依赖
│   ├── .env.example           # 环境变量示例
│   └── Dockerfile
├── frontend/                   # 前端代码
│   ├── src/
│   │   ├── api/               # API接口
│   │   ├── stores/            # Pinia状态管理
│   │   ├── views/             # 页面组件
│   │   ├── layouts/           # 布局组件
│   │   ├── router/            # 路由配置
│   │   ├── types/             # TypeScript类型
│   │   ├── utils/             # 工具函数
│   │   └── styles/            # 样式文件
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## API 文档

启动后端服务后，访问以下地址查看完整的API文档：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 业务规则验证

### 领用单创建检查清单
- [x] 必须绑定有效的维修单
- [x] 维修单不能已关闭
- [x] 领用批次必须已完成三方归属确认
- [x] 领用数量不能超过批次可用库存
- [x] 不能领用已结算期间的批次

### 安全库存检查点
- [x] 补货入库后检查
- [x] 领用出库后检查
- [x] 库存低于安全库存自动创建预警

### 月结控制
- [x] 月结期间的领用记录不能修改
- [x] 月结期间的领用记录不能删除
- [x] 支持反结账（管理员权限）

## 开发说明

### 后端开发规范
- 使用 SQLAlchemy 2.0 异步/同步风格
- API 响应统一使用 Pydantic 模型
- 业务逻辑封装在 CRUD 层
- 使用依赖注入进行权限控制

### 前端开发规范
- 使用 Vue 3 Composition API + `<script setup>`
- 状态管理使用 Pinia
- 表单验证使用 VeeValidate 或 PrimeVue 内置验证
- API 调用统一封装在 `/src/api` 目录

## 许可证

MIT License
