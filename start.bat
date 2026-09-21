@echo off
chcp 65001
echo ======================================
echo 🎯 练枪看板一键启动
echo ======================================
echo.

echo [1/3] 启动后端服务...
cd /d "%~dp0web\backend"
start "练枪看板-后端" cmd /k "python -m uvicorn app.main:app --host 127.0.0.1 --port 8000"
timeout /t 3 /nobreak >nul

echo [2/3] 启动前端服务...
cd /d "%~dp0web\frontend"
start "练枪看板-前端" cmd /k "npm run dev"
timeout /t 5 /nobreak >nul

echo [3/3] 打开浏览器...
start http://localhost:5173

echo.
echo ✅ 启动完成！
echo.
echo 后端服务：http://127.0.0.1:8000
echo 前端页面：http://localhost:5173
echo API 文档：http://127.0.0.1:8000/docs
echo.
echo 关闭对应窗口即可停止服务
pause
