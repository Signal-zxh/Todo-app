# Todo App

一个基于 Flask 的简易待办事项 Web 应用，支持用户注册 / 登录、个人任务管理、任务完成/取消、任务删除。

## 功能

- 用户注册
- 用户登录
- 用户登出
- 每个用户只查看自己的任务
- 添加任务
- 删除任务
- 切换任务完成状态

## 技术栈

- Flask
- Flask-Login
- Flask-WTF
- Flask-SQLAlchemy
- Flask-Migrate
- SQLite

## 运行说明

1. 创建并激活虚拟环境

```bash
python -m venv venv
source venv/bin/activate
```

2. 安装依赖

```bash
pip install -r requirements.txt
```

3. 创建实例配置文件

```bash
cp instance/config.py.example instance/config.py
```

4. 启动应用

```bash
python app.py
```

5. 打开浏览器访问

```text
http://127.0.0.1:5001
```

## 配置

`instance/config.py` 中的配置项示例：

- `SECRET_KEY`：Flask 会话和 CSRF 的密钥
- `SQLALCHEMY_DATABASE_URI`：数据库 URI，默认使用 `instance/todo.db`

项目同时支持环境变量覆盖：

- `SECRET_KEY`
- `DATABASE_URL`

## 数据库初始化

如果需要手动初始化数据库：

```bash
python init_db.py
```