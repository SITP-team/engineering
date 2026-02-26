@echo off
echo ========================================
echo 正在停止所有服务器进程...
echo ========================================

echo.
echo 1. 停止前端开发服务器 (Node.js)...
taskkill /F /IM node.exe 2>nul
if %errorlevel% equ 0 (
    echo   前端服务器已停止
) else (
    echo   未找到前端服务器进程
)

echo.
echo 2. 停止后端API服务器 (Python)...
taskkill /F /IM python.exe 2>nul
if %errorlevel% equ 0 (
    echo   后端API服务器已停止
) else (
    echo   未找到Python服务器进程
)

echo.
echo 3. 停止特定API服务器进程...
for /f "tokens=2" %%i in ('tasklist /fi "imagename eq python.exe" /fo csv ^| findstr /i "api_server"') do (
    set pid=%%~i
    taskkill /F /PID !pid! 2>nul
    echo   已停止进程ID: !pid!
)

echo.
echo ========================================
echo 服务器关闭完成！
echo ========================================
echo.
echo 按任意键退出...
pause >nul