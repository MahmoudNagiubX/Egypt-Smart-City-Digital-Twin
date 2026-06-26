# prepare_space_copy.ps1
# Script to compile a clean deployment folder for Hugging Face Spaces.

$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Definition
$projectRoot = Resolve-Path "$scriptPath\..\.."
$buildDir = "$projectRoot\deploy\huggingface_space_build"

Write-Host "Preparing Hugging Face Space Build Folder..." -ForegroundColor Cyan

# 1. Clean previous build directory if exists
if (Test-Path $buildDir) {
    Write-Host "Removing existing build folder: $buildDir" -ForegroundColor Yellow
    Remove-Item -Recurse -Force $buildDir
}

# 2. Create clean directories
New-Item -ItemType Directory -Path $buildDir | Out-Null
New-Item -ItemType Directory -Path "$buildDir\backend" | Out-Null
New-Item -ItemType Directory -Path "$buildDir\frontend" | Out-Null
New-Item -ItemType Directory -Path "$buildDir\docs" | Out-Null
New-Item -ItemType Directory -Path "$buildDir\deliverables" | Out-Null

# 3. Copy files and directories (excluding git, venv, node_modules, caches, and built dist folders)
Write-Host "Copying backend modules..." -ForegroundColor Gray
Copy-Item -Recurse "$projectRoot\backend\*" "$buildDir\backend" -Exclude ".venv", "__pycache__", ".pytest_cache"

Write-Host "Copying frontend sources..." -ForegroundColor Gray
Copy-Item -Recurse "$projectRoot\frontend\*" "$buildDir\frontend" -Exclude "node_modules", "dist"

Write-Host "Copying documentation..." -ForegroundColor Gray
Copy-Item -Recurse "$projectRoot\docs\*" "$buildDir\docs"

Write-Host "Copying deliverables..." -ForegroundColor Gray
Copy-Item -Recurse "$projectRoot\deliverables\*" "$buildDir\deliverables"

Write-Host "Copying configuration files..." -ForegroundColor Gray
Copy-Item "$projectRoot\docker-compose.yml" "$buildDir\"
if (Test-Path "$projectRoot\requirements.txt") {
    Copy-Item "$projectRoot\requirements.txt" "$buildDir\"
}

# 4. Copy Dockerfile and README from deploy package to root of build folder
Write-Host "Copying deployment descriptors to root..." -ForegroundColor Gray
Copy-Item "$scriptPath\Dockerfile" "$buildDir\Dockerfile"
Copy-Item "$scriptPath\README.md" "$buildDir\README.md"

# 5. Clean up Python caches in the copied folders
Write-Host "Cleaning cache folders in target..." -ForegroundColor Gray
Get-ChildItem -Path $buildDir -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force
Get-ChildItem -Path $buildDir -Recurse -Directory -Filter ".pytest_cache" | Remove-Item -Recurse -Force

Write-Host "Build folder prepared successfully at: $buildDir" -ForegroundColor Green
