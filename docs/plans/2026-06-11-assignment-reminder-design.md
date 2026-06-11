# 催孩子写作业系统 - MVP 设计文档

## 概述

家长通过 Web 管理端添加孩子、创建作业并设置提醒时间，系统到点自动发送邮件通知孩子写作业。后续可扩展 QQ 消息等通知渠道。

## 技术选型

| 层级 | 技术 | 说明 |
|------|------|------|
| 前端 | React 18 + Vite + Ant Design | UI 组件库，快速搭建管理界面 |
| 后端 | FastAPI + SQLAlchemy | 异步 API，自动文档 |
| 数据库 | SQLite (MVP) → PostgreSQL (生产) | MVP 零配置 |
| 定时任务 | APScheduler | Python 生态最好的定时任务库 |
| 邮件 | aiosmtplib | 异步 SMTP 发送 |
| 认证 | JWT (简单 Token) | MVP 阶段简化认证 |

## 数据模型

### Parent（家长）
- id: Integer, PK
- username: String, unique
- password_hash: String
- email: String
- created_at: DateTime

### Child（孩子）
- id: Integer, PK
- parent_id: Integer, FK → Parent
- name: String
- qq_number: String（预留，后续扩展 QQ 通知）
- email: String（当前用于接收邮件通知）
- created_at: DateTime

### Assignment（作业）
- id: Integer, PK
- parent_id: Integer, FK → Parent
- child_id: Integer, FK → Child
- title: String
- description: Text
- remind_at: DateTime（提醒时间）
- status: Enum(pending, sent)
- created_at: DateTime

### ReminderLog（提醒记录）
- id: Integer, PK
- assignment_id: Integer, FK → Assignment
- channel: String（email / qq）
- status: Enum(success, failed)
- sent_at: DateTime
- error_message: Text, nullable

## API 设计

### 认证
- POST /api/auth/register — 家长注册
- POST /api/auth/login — 家长登录

### 孩子管理
- GET /api/children — 孩子列表
- POST /api/children — 添加孩子
- PUT /api/children/:id — 编辑孩子
- DELETE /api/children/:id — 删除孩子

### 作业管理
- GET /api/assignments — 作业列表
- POST /api/assignments — 创建作业
- PUT /api/assignments/:id — 编辑作业
- DELETE /api/assignments/:id — 删除作业

### 提醒记录
- GET /api/reminders — 提醒记录列表

## 定时提醒机制

APScheduler 使用 BackgroundScheduler，每分钟执行一次检查：
1. 查询 `remind_at <= now` 且 `status == pending` 的作业
2. 根据孩子邮箱发送邮件通知
3. 更新作业状态为 `sent`
4. 写入 ReminderLog 记录发送结果

## 前端页面

| 页面 | 路由 | 功能 |
|------|------|------|
| 登录/注册 | /login | 家长账号 |
| 仪表盘 | / | 作业总览、今日待提醒 |
| 孩子管理 | /children | 添加/编辑/删除孩子 |
| 作业管理 | /assignments | 创建/编辑作业、设置提醒时间 |
| 提醒记录 | /reminders | 查看历史发送状态 |

## 项目目录结构

```
assignment-reminder-qoder/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI 入口
│   │   ├── config.py        # 配置
│   │   ├── database.py      # 数据库连接
│   │   ├── models/          # SQLAlchemy 模型
│   │   ├── schemas/         # Pydantic 校验
│   │   ├── api/             # 路由
│   │   ├── services/        # 业务逻辑
│   │   └── scheduler/       # APScheduler 定时任务
│   ├── requirements.txt
│   └── alembic/             # 数据库迁移
├── frontend/
│   ├── src/
│   │   ├── pages/           # 页面组件
│   │   ├── components/      # 通用组件
│   │   ├── api/             # API 调用
│   │   └── App.tsx
│   └── package.json
└── README.md
```

## 后续扩展

- QQ 消息通知（通过第三方协议如 Lagrange/OneBot）
- 企业微信 Webhook 通知
- 作业完成确认功能
- 多次提醒（间隔提醒）
- 移动端适配
