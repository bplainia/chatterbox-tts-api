# Local Docker Build Test Script
# This script helps test Docker builds locally before pushing to GitHub

Write-Host "🐳 Chatterbox TTS API - Local Docker Build Test" -ForegroundColor Cyan
Write-Host "=" * 60

# Change to project root
Set-Location $PSScriptRoot\..\..\

# Function to build and test an image
function Test-DockerBuild {
    param(
        [string]$Name,
        [string]$Dockerfile,
        [string]$Tag
    )
    
    Write-Host "`n📦 Building: $Name" -ForegroundColor Yellow
    Write-Host "Dockerfile: $Dockerfile"
    Write-Host "Tag: $Tag"
    Write-Host "-" * 60
    
    $startTime = Get-Date
    
    try {
        # Build the image
        docker build -f $Dockerfile -t $Tag .
        
        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ Build failed for $Name" -ForegroundColor Red
            return $false
        }
        
        $buildTime = (Get-Date) - $startTime
        Write-Host "✅ Build successful in $($buildTime.TotalSeconds) seconds" -ForegroundColor Green
        
        # Get image size
        $imageSize = docker images $Tag --format "{{.Size}}"
        Write-Host "📊 Image size: $imageSize" -ForegroundColor Cyan
        
        return $true
    }
    catch {
        Write-Host "❌ Error building $Name : $_" -ForegroundColor Red
        return $false
    }
}

# Function to test an image
function Test-DockerImage {
    param(
        [string]$Name,
        [string]$Tag,
        [int]$Port = 4123
    )
    
    Write-Host "`n🧪 Testing: $Name" -ForegroundColor Yellow
    Write-Host "-" * 60
    
    try {
        # Run the container
        Write-Host "Starting container..."
        docker run -d --name test-$Name -p ${Port}:4123 -e DEVICE=cpu $Tag
        
        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ Failed to start container" -ForegroundColor Red
            return $false
        }
        
        # Wait for container to be ready
        Write-Host "Waiting for container to be ready..."
        $maxAttempts = 30
        $attempt = 0
        $ready = $false
        
        while ($attempt -lt $maxAttempts) {
            $attempt++
            Start-Sleep -Seconds 2
            
            try {
                $response = Invoke-WebRequest -Uri "http://localhost:${Port}/health" -TimeoutSec 2 -ErrorAction SilentlyContinue
                if ($response.StatusCode -eq 200) {
                    $ready = $true
                    break
                }
            }
            catch {
                Write-Host "." -NoNewline
            }
        }
        
        Write-Host ""
        
        if ($ready) {
            Write-Host "✅ Container is healthy!" -ForegroundColor Green
            
            # Show logs
            Write-Host "`nContainer logs (last 10 lines):"
            docker logs test-$Name --tail 10
            
            return $true
        }
        else {
            Write-Host "❌ Container failed to become ready" -ForegroundColor Red
            Write-Host "`nContainer logs:"
            docker logs test-$Name
            return $false
        }
    }
    catch {
        Write-Host "❌ Error testing $Name : $_" -ForegroundColor Red
        return $false
    }
    finally {
        # Cleanup
        Write-Host "`nCleaning up..."
        docker stop test-$Name 2>$null | Out-Null
        docker rm test-$Name 2>$null | Out-Null
    }
}

# Main execution
Write-Host "`n🔨 Starting local builds..." -ForegroundColor Cyan

$builds = @(
    @{Name="standard"; Dockerfile="docker/Dockerfile"; Tag="chatterbox-tts:test-standard"},
    @{Name="cpu"; Dockerfile="docker/Dockerfile.cpu"; Tag="chatterbox-tts:test-cpu"},
    @{Name="uv"; Dockerfile="docker/Dockerfile.uv"; Tag="chatterbox-tts:test-uv"}
)

$results = @()

foreach ($build in $builds) {
    $buildSuccess = Test-DockerBuild -Name $build.Name -Dockerfile $build.Dockerfile -Tag $build.Tag
    
    if ($buildSuccess) {
        # Only test CPU and UV builds (they're faster)
        if ($build.Name -in @("cpu", "uv")) {
            $testSuccess = Test-DockerImage -Name $build.Name -Tag $build.Tag -Port (4123 + $builds.IndexOf($build))
            $results += @{Name=$build.Name; Build=$buildSuccess; Test=$testSuccess}
        }
        else {
            $results += @{Name=$build.Name; Build=$buildSuccess; Test=$null}
            Write-Host "⏭️  Skipping test for $($build.Name) (too slow for local testing)" -ForegroundColor Yellow
        }
    }
    else {
        $results += @{Name=$build.Name; Build=$buildSuccess; Test=$null}
    }
}

# Summary
Write-Host "`n" + ("=" * 60) -ForegroundColor Cyan
Write-Host "📊 Build Test Summary" -ForegroundColor Cyan
Write-Host ("=" * 60) -ForegroundColor Cyan

foreach ($result in $results) {
    $buildStatus = if ($result.Build) { "✅ PASS" } else { "❌ FAIL" }
    $testStatus = if ($null -eq $result.Test) { "⏭️  SKIP" } elseif ($result.Test) { "✅ PASS" } else { "❌ FAIL" }
    
    Write-Host "`n$($result.Name.ToUpper())"
    Write-Host "  Build: $buildStatus"
    Write-Host "  Test:  $testStatus"
}

Write-Host "`n" + ("=" * 60) -ForegroundColor Cyan

$allPassed = $results | Where-Object { -not $_.Build } | Measure-Object | Select-Object -ExpandProperty Count
if ($allPassed -eq 0) {
    Write-Host "🎉 All builds completed successfully!" -ForegroundColor Green
    Write-Host "`n💡 You can now push to GitHub to trigger the CI/CD pipeline" -ForegroundColor Cyan
    exit 0
}
else {
    Write-Host "⚠️  Some builds failed. Please review the errors above." -ForegroundColor Red
    exit 1
}
