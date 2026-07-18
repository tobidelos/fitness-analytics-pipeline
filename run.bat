@echo off
echo =========================================
echo 🚀 Fitness Data Pipeline Runner
echo =========================================
echo.

echo 1. Instalando Dependencias y Tests...
pip install -r requirements.txt
echo.

echo 2. Corriendo Pruebas Unitarias (TDD)...
pytest tests/
echo.

echo 3. Ejecutando Pipeline Principal (ETL, EDA, DB Export)...
python main.py
echo.

echo 4. Levantando el Dashboard Interactivo...
streamlit run src/dashboard.py
echo.
pause
