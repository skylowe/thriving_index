@echo off
REM Install dependencies for Regional Map feature

echo ========================================
echo Installing Regional Map Dependencies
echo ========================================
echo.

echo This will install:
echo   - geopandas (geographic data processing)
echo   - shapely (geometric operations)
echo.

echo Installing via pip...
echo.

python -m pip install --upgrade pip
python -m pip install geopandas shapely

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.

echo Testing installation...
python -c "import geopandas; print('✓ geopandas installed successfully')"
python -c "import shapely; print('✓ shapely installed successfully')"

echo.
echo You can now run the dashboard with: run_dashboard.bat
echo.
pause
