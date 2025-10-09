@echo off
REM D&D Initiative Creature API Docker Setup for Windows

echo 🐉 Setting up D&D Initiative Creature API with Docker...

REM Create local directories if they don't exist
echo 📁 Creating directories...
if not exist "local_creature_images" mkdir local_creature_images
if not exist "docker_data" mkdir docker_data
if not exist "docker_data\database" mkdir docker_data\database
if not exist "docker_data\uploads" mkdir docker_data\uploads

REM Check if local images directory is empty
dir /b local_creature_images 2>nul | findstr "^" >nul
if errorlevel 1 (
    echo 📸 Local images directory is empty. You can add your own creature images here!
    echo    Supported formats: JPG, PNG, GIF, WEBP
    echo    Naming convention: creature_name.ext ^(e.g., ancient_red_dragon.jpg^)
)

REM Build and start the Docker container
echo 🐳 Building and starting Docker container...
docker-compose -f docker-compose.creature-api.yml up --build -d

REM Wait a moment for the container to start
timeout /t 3 /nobreak >nul

REM Check if container is running
docker ps | findstr "dnd-creature-api" >nul
if not errorlevel 1 (
    echo ✅ Container is running successfully!
    echo.
    echo 🎯 API Endpoints available at:
    echo    http://localhost:8000/api/curated-images/get_creature_image
    echo    http://localhost:8000/api/curated-images/list_all_creatures
    echo    http://localhost:8000/api/curated-images/search_creatures
    echo    http://localhost:8000/docs ^(API documentation^)
    echo.
    echo 📁 To add your own creature images:
    echo    1. Place images in .\local_creature_images\ directory
    echo    2. Restart the container: docker-compose -f docker-compose.creature-api.yml restart
    echo.
    echo 🛑 To stop: docker-compose -f docker-compose.creature-api.yml down
) else (
    echo ❌ Container failed to start. Check logs with:
    echo    docker-compose -f docker-compose.creature-api.yml logs
)

pause