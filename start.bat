@echo off
echo ========================================
echo   PATATAG - Rastreador GPS para Pets
echo ========================================
echo.

REM Verificar se o ambiente virtual existe
if not exist ".venv\Scripts\activate.bat" (
    echo Criando ambiente virtual...
    python -m venv .venv
    echo.
)

REM Ativar ambiente virtual
echo Ativando ambiente virtual...
call .venv\Scripts\activate.bat
echo.

REM Instalar dependências se necessário
echo Verificando dependências...
pip install -r requirements.txt --quiet
echo.

REM Iniciar servidor
echo ========================================
echo   Servidor iniciando...
echo   Acesse: http://localhost:5000
echo ========================================
echo.
echo Pressione Ctrl+C para parar o servidor
echo.

python app.py

pause
