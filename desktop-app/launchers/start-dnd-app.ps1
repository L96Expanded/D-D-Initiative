# D&D Initiative Tracker Startup Script
# This script starts Docker, activates the environment, builds and runs the application

param(
    [switch]$ShowConsole = $false
)

# Function to write colored output
function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

# Set the working directory to the project root
$ProjectPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectPath

Write-ColorOutput Green "Starting D&D Initiative Tracker..."
Write-ColorOutput Yellow "Project Path: $ProjectPath"

# Check if Docker Desktop is running
Write-ColorOutput Cyan "Checking Docker status..."
try {
    $dockerInfo = docker info 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "Docker not running"
    }
    Write-ColorOutput Green "Docker is running"
} catch {
    Write-ColorOutput Yellow "Starting Docker Desktop..."
    
    # Try to start Docker Desktop
    $dockerPath = "${env:ProgramFiles}\Docker\Docker\Docker Desktop.exe"
    if (Test-Path $dockerPath) {
        Start-Process $dockerPath
        Write-ColorOutput Yellow "Waiting for Docker to start (this may take a minute)..."
        
        # Wait for Docker to be ready (max 2 minutes)
        $timeout = 120
        $elapsed = 0
        do {
            Start-Sleep -Seconds 5
            $elapsed += 5
            try {
                docker info 2>$null | Out-Null
                if ($LASTEXITCODE -eq 0) {
                    Write-ColorOutput Green "Docker Desktop is now running"
                    break
                }
            } catch {
                # Continue waiting
            }
            
            if ($elapsed -ge $timeout) {
                Write-ColorOutput Red "Timeout waiting for Docker to start"
                Write-ColorOutput Red "Please start Docker Desktop manually and try again"
                Read-Host "Press Enter to exit"
                exit 1
            }
            
            Write-ColorOutput Yellow "   Still waiting... ($($elapsed) seconds)"
        } while ($true)
    } else {
        Write-ColorOutput Red "Docker Desktop not found at expected location"
        Write-ColorOutput Red "Please install Docker Desktop or start it manually"
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# Activate Python virtual environment if it exists
if (Test-Path ".venv\Scripts\Activate.ps1") {
    Write-ColorOutput Cyan "Activating Python virtual environment..."
    & ".\.venv\Scripts\Activate.ps1"
    Write-ColorOutput Green "Virtual environment activated"
}

# Stop any existing containers
Write-ColorOutput Cyan "Stopping any existing containers..."
docker-compose down 2>$null

# Build and start the application
Write-ColorOutput Cyan "Building and starting D&D Initiative Tracker..."
Write-ColorOutput Yellow "This may take a few minutes on first run..."

# Run docker-compose up --build
$process = Start-Process -FilePath "docker-compose" -ArgumentList "up", "--build" -NoNewWindow -PassThru

# Wait a moment for containers to start
Start-Sleep -Seconds 10

# Check if containers are running
$attempts = 0
$maxAttempts = 60
$frontendReady = $false
$backendReady = $false

Write-ColorOutput Yellow "Waiting for application to be fully ready..."

do {
    $attempts++
    Start-Sleep -Seconds 2
    
    # Check if the frontend is responding
    if (-not $frontendReady) {
        try {
            $frontendResponse = Invoke-WebRequest -Uri "http://localhost:3000" -TimeoutSec 5 -UseBasicParsing 2>$null
            if ($frontendResponse.StatusCode -eq 200) {
                Write-ColorOutput Green "Frontend is ready!"
                $frontendReady = $true
            }
        } catch {
            # Continue checking
        }
    }
    
    # Check if the backend API is responding
    if (-not $backendReady) {
        try {
            $backendResponse = Invoke-WebRequest -Uri "http://localhost:8000/docs" -TimeoutSec 5 -UseBasicParsing 2>$null
            if ($backendResponse.StatusCode -eq 200) {
                Write-ColorOutput Green "Backend API is ready!"
                $backendReady = $true
            }
        } catch {
            # Continue checking
        }
    }
    
    # Both services are ready
    if ($frontendReady -and $backendReady) {
        Write-ColorOutput Green "Application is fully ready!"
        break
    }
    
    # Check if docker-compose process is still running
    if ($process.HasExited) {
        Write-ColorOutput Red "Docker-compose process exited unexpectedly"
        Write-ColorOutput Yellow "Please check the logs for errors"
        Read-Host "Press Enter to exit"
        exit 1
    }
    
    if ($attempts -ge $maxAttempts) {
        Write-ColorOutput Yellow "Taking longer than expected, but continuing..."
        Write-ColorOutput Yellow "Frontend ready: $frontendReady, Backend ready: $backendReady"
        break
    }
    
    $statusMessage = "Waiting for services... ($($attempts)/$($maxAttempts))"
    if ($frontendReady) {
        $statusMessage += " [Frontend: OK]"
    } else {
        $statusMessage += " [Frontend: Loading...]"
    }
    if ($backendReady) {
        $statusMessage += " [Backend: OK]"
    } else {
        $statusMessage += " [Backend: Loading...]"
    }
    Write-ColorOutput Yellow "   $statusMessage"
} while ($true)

# Open the application in default browser
Write-ColorOutput Cyan "Opening D&D Initiative Tracker in your browser..."
Start-Process "http://localhost:3000"

Write-ColorOutput Green "D&D Initiative Tracker is now running!"
Write-ColorOutput Yellow ""
Write-ColorOutput Yellow "Application URLs:"
Write-ColorOutput White "  - Frontend: http://localhost:3000"
Write-ColorOutput White "  - Backend API: http://localhost:8000"
Write-ColorOutput White "  - API Docs: http://localhost:8000/docs"
Write-ColorOutput Yellow ""
Write-ColorOutput Yellow "To stop the application:"
Write-ColorOutput White "  - Close this window, or"
Write-ColorOutput White "  - Press Ctrl+C, or"
Write-ColorOutput White "  - Run: docker-compose down"
Write-ColorOutput Yellow ""

if (-not $ShowConsole) {
    Write-ColorOutput Cyan "This window will remain open to keep the application running."
    Write-ColorOutput Cyan "You can minimize it if you'd like."
}

# Keep the script running so containers stay up
try {
    Write-ColorOutput Green "Ready for your D&D session! Press Ctrl+C to stop."
    
    # Wait for the docker-compose process to exit or user interruption
    while (-not $process.HasExited) {
        Start-Sleep -Seconds 5
    }
} catch {
    Write-ColorOutput Yellow "Shutting down..."
} finally {
    # Clean shutdown
    Write-ColorOutput Cyan "Stopping containers..."
    docker-compose down
    Write-ColorOutput Green "Stopped successfully. Happy adventuring!"
}