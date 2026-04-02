@echo off
chcp 65001 >nul 2>&1
setlocal EnableDelayedExpansion

REM ============================================================
REM rmrb-pdf-fetcher 一键安装脚本 (Windows)
REM 用法: scripts\install.bat
REM ============================================================

echo.
echo ==========================================
echo   人民日报PDF下载器 - 安装向导
echo ==========================================
echo.

REM ---- 项目根目录（scripts 的上级目录）----
set "PROJECT_ROOT=%~dp0.."
cd /d "%PROJECT_ROOT%"

REM ---- 1. 检测 Python ----
echo [INFO] 检测 Python 环境...

where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] 未找到 Python，请先安装 Python ^>= 3.11
    echo   下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

for /f "tokens=*" %%v in ('python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"') do set PY_VERSION=%%v
echo [INFO] Python 版本: %PY_VERSION%

python -c "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)"
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python 版本过低，请升级到 3.11+
    pause
    exit /b 1
)

REM ---- 2. 安装依赖 ----
set "VENV_DIR=%PROJECT_ROOT%\.venv"
set "RUN_PREFIX="

where uv >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo [INFO] 检测到 uv，使用 uv 安装...
    call uv sync
    set "RUN_PREFIX=uv run"
) else (
    echo [INFO] 使用 pip + venv 安装...

    if not exist "%VENV_DIR%" (
        echo [INFO] 创建虚拟环境...
        python -m venv "%VENV_DIR%"
    )

    echo [INFO] 激活虚拟环境并安装依赖...
    call "%VENV_DIR%\Scripts\activate.bat"
    pip install --upgrade pip -q
    pip install -e "%PROJECT_ROOT%"
)

REM ---- 3. 安装 Playwright Chromium ----
echo [INFO] 安装 Playwright Chromium 浏览器（首次安装可能需要几分钟）...
if "%RUN_PREFIX%"=="uv run" (
    uv run playwright install chromium
) else (
    playwright install chromium
)

REM ---- 4. 注册 Claude Code Skill ----
set "SKILL_DIR=%USERPROFILE%\.claude\skills\rmrb-pdf-fetcher"

echo [INFO] 注册 Claude Code Skill...
if not exist "%SKILL_DIR%" mkdir "%SKILL_DIR%"
copy /Y "%PROJECT_ROOT%\SKILL.md" "%SKILL_DIR%\SKILL.md" >nul
echo [INFO] Skill 已安装到: %SKILL_DIR%\SKILL.md

REM ---- 5. 验证安装 ----
echo.
echo [INFO] 验证安装...
if "%RUN_PREFIX%"=="uv run" (
    uv run python -c "from rmrb_fetcher.downloader import download; print('[INFO] Python 包: 正常')"
) else (
    python -c "from rmrb_fetcher.downloader import download; print('[INFO] Python 包: 正常')"
)

if exist "%SKILL_DIR%\SKILL.md" (
    echo [INFO] Skill 注册: 正常
) else (
    echo [WARN] Skill 注册可能失败
)

REM ---- 完成 ----
echo.
echo ==========================================
echo   安装完成！
echo ==========================================
echo.
echo 使用方法：
if "%RUN_PREFIX%"=="uv run" (
    echo   CLI:    uv run rmrb-download --once
    echo   JSON:   uv run rmrb-download --once --output-json
    echo   定时:   uv run rmrb-download
) else (
    echo   CLI:    rmrb-download --once
    echo   JSON:   rmrb-download --once --output-json
    echo   定时:   rmrb-download
)
echo   Skill:  在 Claude Code 中输入 /rmrb
echo.
echo 下载目录: %PROJECT_ROOT%\人民日报下载\
echo.
pause
