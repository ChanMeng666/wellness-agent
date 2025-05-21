# 简化版Wellness Agent前端

此版本已禁用所有高级功能，只保留了基本的聊天界面，用于测试与后端的集成。

## 启动方法

1. 确保后端服务器已启动:
   ```
   python run_dev_server.py
   ```

2. 启动前端开发服务器:
   ```
   cd frontend
   pnpm dev
   ```

3. 访问 http://localhost:3000 查看简化后的界面

## 已禁用的功能

- 用户认证和会话管理
- 高级UI组件
- 文档和附件功能
- 高级聊天历史和导出功能

## 重要的修改

1. 已禁用认证中间件 (middleware.ts)
2. 已创建一个简化的not-found页面，自动重定向到主页
3. 添加了控制台日志以帮助诊断问题
4. 配置了API转发，支持与原始后端的通信

## 故障排除

如果遇到问题:

1. 检查浏览器控制台 (F12)，查看是否有任何错误消息
2. 确保后端服务器已在 http://localhost:8000 正常运行
3. 如果看到404错误，刷新页面并等待重定向到主页
4. 如果API请求失败，检查以下几点:
   - .env.local 文件中的 NEXT_PUBLIC_BACKEND_URL 设置正确
   - 后端服务器是否返回正确的CORS头
   - 网络请求是否有其他报错

### 常见问题

如果看到 "Sorry, there was an error processing your request." 消息:
1. 检查控制台日志了解具体错误
2. 确认后端运行于 http://localhost:8000
3. 检查API请求格式是否与后端期望的格式匹配

## 恢复完整功能

若要恢复禁用的功能，请:
1. 删除 .env.local 中的临时 AUTH_SECRET
2. 恢复原始的 middleware.ts 文件
3. 删除 not-found.tsx 文件 