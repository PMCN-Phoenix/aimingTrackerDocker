@echo off
chcp 65001
echo ======================================
echo 🎯 练枪看板生产模式启动
echo ======================================
echo.

echo [1/2] 检查前端是否已构建...
if not exist "%~dp0web\frontend\dist\index.html" (
    echo ⚠️ 前端未构建，正在构建...
    cd /d "%~dp0web\frontend"
    call npm run build
    if %errorlevel% neq 0 (
        echo ❌ 前端构建失败
        pause
        exit /b 1
    )
    echo ✅ 前端构建完成
) else (
    echo ✅ 前端已构建
)
echo.

echo [2/2] 启动生产服务...
cd /d "%~dp0web\backend"
start "练枪看板-生产模式" cmd /k "python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"
timeout /t 3 /nobreak >nul

echo.
echo ✅ 启动完成！
echo.
echo 访问地址：http://localhost:8000
echo API 文档：http://localhost:8000/docs
echo.
echo 关闭对应窗口即可停止服务
pause
