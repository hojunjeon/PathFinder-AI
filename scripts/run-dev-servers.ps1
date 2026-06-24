param(
    [Alias("h")]
    [switch]$Help
)

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
$BackendDir = Join-Path $Root "backend"
$FrontendDir = Join-Path $Root "frontend"
$LlmDir = Join-Path $Root "llm_server"
$LogDir = Join-Path $Root "logs\dev-servers"

$BackendPort = if ($env:BACKEND_PORT) { [int]$env:BACKEND_PORT } else { 8080 }
$LlmPort = if ($env:LLM_PORT) { [int]$env:LLM_PORT } else { 8081 }
$FrontendPort = if ($env:FRONTEND_PORT) { [int]$env:FRONTEND_PORT } else { 5173 }
$Node = $null
$ViteEntrypoint = Join-Path $FrontendDir 'node_modules\vite\bin\vite.js'

$Npm = "npm.cmd"

function Show-LauncherHelp {
    Write-Host ""
    Write-Host "PathFinder AI development launcher"
    Write-Host "================================="
    Write-Host ""
    Write-Host "Usage"
    Write-Host "  run-dev.bat"
    Write-Host "  run-dev.bat --help"
    Write-Host ""
    Write-Host "What it starts"
    Write-Host "  - Vue/Vite frontend : http://127.0.0.1:$FrontendPort"
    Write-Host "  - Django backend    : http://127.0.0.1:$BackendPort"
    Write-Host "  - FastAPI LLM server: http://127.0.0.1:$LlmPort"
    Write-Host ""
    Write-Host "What it does"
    Write-Host "  1. Creates missing Python virtual environments on first run."
    Write-Host "  2. Installs missing Python and npm dependencies on first run."
    Write-Host "  3. Runs Django migrations."
    Write-Host "  4. Loads the company fixture into the default DB on first run."
    Write-Host "  5. Starts all three servers together."
    Write-Host "  6. Waits until each server answers its health check."
    Write-Host "  7. Keeps this console attached so Ctrl+C stops everything."
    Write-Host ""
    Write-Host "Prerequisites"
    Write-Host "  - Python 3.11 available as py -3.11, py -3, or python"

    Write-Host "  - Node.js with npm in PATH"
    Write-Host "  - Internet access on first run for dependency installation"

    Write-Host ""
    Write-Host "Optional environment variables"
    Write-Host "  - GMS_KEY             Required only for real roadmap generation."
    Write-Host "  - LLM_INTERNAL_TOKEN  Auto-generated when missing."
    Write-Host "  - BACKEND_PORT        Default: 8080. Uses next free port if occupied."
    Write-Host "  - LLM_PORT            Default: 8081. Uses next free port if occupied."
    Write-Host "  - FRONTEND_PORT       Default: 5173. Uses next free port if occupied."
    Write-Host ""
    Write-Host "Logs"
    Write-Host "  - logs\dev-servers\backend.out.log"
    Write-Host "  - logs\dev-servers\backend.err.log"
    Write-Host "  - logs\dev-servers\llm.out.log"
    Write-Host "  - logs\dev-servers\llm.err.log"
    Write-Host "  - logs\dev-servers\frontend.out.log"
    Write-Host "  - logs\dev-servers\frontend.err.log"
    Write-Host ""
    Write-Host "Stopping"
    Write-Host "  - Press Ctrl+C in this window to stop Vue, FastAPI, and Django together."
    Write-Host ""
}

function Assert-Command($Name, $Hint) {
    $command = Get-Command $Name -ErrorAction SilentlyContinue
    if (-not $command) {
        throw "$Name not found in PATH.`n$Hint"
    }
    return $command
}

function Resolve-Python3 {
    $minimumVersion = [Version]'3.11'
    $candidates = @()

    $py = Get-Command py.exe -ErrorAction SilentlyContinue
    if ($py) {
        $candidates += @{ Command = $py.Source; Args = @('-3.11') }
        $candidates += @{ Command = $py.Source; Args = @('-3') }
    }

    $python = Get-Command python.exe -ErrorAction SilentlyContinue
    if ($python) {
        $candidates += @{ Command = $python.Source; Args = @() }
    }

    foreach ($candidate in $candidates) {
        $versionArgs = @($candidate.Args) + @('-c', "import sys; print('.'.join(map(str, sys.version_info[:3])))")
        try {
            $output = & $candidate.Command @versionArgs 2>$null
        } catch {
            continue
        }
        if ($LASTEXITCODE -ne 0 -or -not $output) {
            continue
        }

        $versionText = $output.Trim()
        try {
            $version = [Version]$versionText
        } catch {
            continue
        }

        if ($version -ge $minimumVersion) {
            return @{ Command = $candidate.Command; Args = $candidate.Args; Version = $versionText }
        }
    }

    throw "Python 3.11+ not found.`nInstall Python 3.11 or newer and reopen this terminal."
}

function Ensure-PythonEnvironment($ProjectDir, $RequirementsFile, $Label, $PythonSpec) {
    $venvDir = Join-Path $ProjectDir 'venv'
    $venvPython = Join-Path $venvDir 'Scripts\python.exe'
    $stampFile = Join-Path $venvDir '.requirements-installed'
    $needsInstall = $false

    if (-not (Test-Path -LiteralPath $venvPython)) {
        Write-Host "Creating $Label virtual environment..."
        & $PythonSpec.Command @($PythonSpec.Args + @('-m', 'venv', $venvDir))
        if ($LASTEXITCODE -ne 0) {
            throw "Failed to create $Label virtual environment."
        }
        $needsInstall = $true
    }

    if (-not (Test-Path -LiteralPath $stampFile)) {
        $needsInstall = $true
    } elseif ((Get-Item -LiteralPath $RequirementsFile).LastWriteTimeUtc -gt (Get-Item -LiteralPath $stampFile).LastWriteTimeUtc) {
        $needsInstall = $true
    }

    if ($needsInstall) {
        Write-Host "Installing $Label Python dependencies..."
        & $venvPython -m pip install --disable-pip-version-check -r $RequirementsFile | Out-Host

        if ($LASTEXITCODE -ne 0) {
            throw "Failed to install $Label Python dependencies."
        }
        Set-Content -LiteralPath $stampFile -Value (Get-Date).ToString('o') -Encoding ASCII
    }

    return $venvPython
}

function Resolve-Node {
    $node = Assert-Command 'node.exe' "Install Node.js, then reopen this terminal."
    return $node.Source
}

function Assert-Path($Path, $Hint) {
    if (-not (Test-Path -LiteralPath $Path)) {
        throw "$Path not found.`n$Hint"
    }
}

function Ensure-FrontendDependencies($ProjectDir) {
    $packageJson = Join-Path $ProjectDir 'package.json'
    $packageLock = Join-Path $ProjectDir 'package-lock.json'
    $nodeModules = Join-Path $ProjectDir 'node_modules'
    $stampFile = Join-Path $nodeModules '.install-stamp'
    $needsInstall = -not (Test-Path -LiteralPath $nodeModules)

    if (-not $needsInstall -and (Test-Path -LiteralPath $stampFile)) {
        $packageJsonTime = (Get-Item -LiteralPath $packageJson).LastWriteTimeUtc
        $stampTime = (Get-Item -LiteralPath $stampFile).LastWriteTimeUtc
        if ($packageJsonTime -gt $stampTime) {
            $needsInstall = $true
        }
        if ((Test-Path -LiteralPath $packageLock) -and ((Get-Item -LiteralPath $packageLock).LastWriteTimeUtc -gt $stampTime)) {
            $needsInstall = $true
        }
    } elseif (-not $needsInstall) {
        $needsInstall = $true
    }

    if ($needsInstall) {
        Write-Host "Installing frontend npm dependencies..."
        Push-Location $ProjectDir
        try {
            & $Npm install | Out-Host
            if ($LASTEXITCODE -ne 0) {
                throw "npm install failed."
            }
        } finally {
            Pop-Location
        }
        New-Item -ItemType Directory -Force -Path $nodeModules | Out-Null
        Set-Content -LiteralPath $stampFile -Value (Get-Date).ToString('o') -Encoding ASCII
    }
}

function Get-DjangoCompanyCount($BackendPython, $ProjectDir) {
    Push-Location $ProjectDir
    try {
        $output = & $BackendPython manage.py shell -v 0 -c "from companies.models import Company; print(Company.objects.count())" 2>&1
        if ($LASTEXITCODE -ne 0) {
            throw "Failed to check company fixture state.`n$output"
        }
    } finally {
        Pop-Location
    }

    $countLine = $output | Where-Object { $_ -match '^\d+$' } | Select-Object -Last 1
    if (-not $countLine) {
        throw "Failed to parse company count from Django output.`n$output"
    }

    return [int]$countLine
}

function Ensure-CompanyFixtureLoaded($BackendPython, $ProjectDir, $LoadOnFirstRun) {
    $fixturePath = Join-Path $ProjectDir "companies\fixtures\companies.json"
    if (-not (Test-Path -LiteralPath $fixturePath)) {
        throw "Company fixture not found: $fixturePath"
    }

    $companyCount = Get-DjangoCompanyCount $BackendPython $ProjectDir
    if (-not $LoadOnFirstRun -and $companyCount -gt 0) {
        Write-Host "Company fixture already loaded ($companyCount companies)."
        return
    }

    Write-Host "Loading company fixture into default database..."
    Push-Location $ProjectDir
    try {
        & $BackendPython manage.py loaddata companies
        if ($LASTEXITCODE -ne 0) {
            throw "Django loaddata companies failed with exit code $LASTEXITCODE"
        }
    } finally {
        Pop-Location
    }

    $companyCount = Get-DjangoCompanyCount $BackendPython $ProjectDir
    Write-Host "Company fixture ready ($companyCount companies)."
}


function Assert-PortFree($Port) {
    $listener = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
    if ($listener) {
        $owners = ($listener | Select-Object -ExpandProperty OwningProcess -Unique) -join ", "
        throw "Port $Port is already in use by process id(s): $owners"
    }
}

function Stop-ProcessTree($ProcessId) {
    $children = Get-CimInstance Win32_Process -Filter "ParentProcessId=$ProcessId" -ErrorAction SilentlyContinue
    foreach ($child in $children) {
        Stop-ProcessTree -ProcessId $child.ProcessId
    }
    $proc = Get-Process -Id $ProcessId -ErrorAction SilentlyContinue
    if ($proc) {
        Stop-Process -Id $ProcessId -Force -ErrorAction SilentlyContinue
    }
}

function Wait-Http($Name, $Url, $Headers) {
    $deadline = (Get-Date).AddSeconds(45)
    while ((Get-Date) -lt $deadline) {
        try {
            Invoke-WebRequest -Uri $Url -Headers $Headers -UseBasicParsing -TimeoutSec 3 | Out-Null
            Write-Host "$Name ready: $Url"
            return
        } catch {
            $status = $null
            if ($_.Exception.Response) {
                $status = $_.Exception.Response.StatusCode.value__
            }
            if ($status -in @(401, 403, 404, 405)) {
                Write-Host "$Name ready: $Url returned $status"
                return
            }
            Start-Sleep -Milliseconds 500
        }
    }
    throw "$Name did not become ready: $Url"
}

function Import-DotEnv($Path) {
    $values = @{}
    if (-not (Test-Path -LiteralPath $Path)) {
        return $values
    }

    foreach ($line in Get-Content -LiteralPath $Path) {
        $trimmed = $line.Trim()
        if (-not $trimmed -or $trimmed.StartsWith("#") -or -not $trimmed.Contains("=")) {
            continue
        }

        $name, $value = $trimmed.Split("=", 2)
        $name = $name.Trim()
        if (-not $name) {
            continue
        }

        $cleanValue = $value.Trim().Trim('"').Trim("'")
        $values[$name] = $cleanValue
    }

    return $values
}

if ($Help) {
    Show-LauncherHelp
    exit 0
}

try {

Show-LauncherHelp
Write-Host "Launching development servers..."
Write-Host ""

$null = Assert-Command $Npm "Install Node.js, then reopen this terminal."
$Node = Resolve-Node
$pythonSpec = Resolve-Python3
$BackendPython = Ensure-PythonEnvironment $BackendDir (Join-Path $BackendDir 'requirements.txt') 'backend' $pythonSpec
$LlmPython = Ensure-PythonEnvironment $LlmDir (Join-Path $LlmDir 'requirements.txt') 'llm_server' $pythonSpec
Ensure-FrontendDependencies $FrontendDir
Assert-Path $ViteEntrypoint "Run npm install in the frontend directory so Vite is available."

$DotEnvValues = Import-DotEnv (Join-Path $Root ".env")

$BackendPort = Resolve-AvailablePort "Backend" $BackendPort
$LlmPort = Resolve-AvailablePort "LLM server" $LlmPort @($BackendPort)
$FrontendPort = Resolve-AvailablePort "Frontend" $FrontendPort @($BackendPort, $LlmPort)

New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

$oldToken = $env:LLM_INTERNAL_TOKEN
$oldGmsKey = $env:GMS_KEY
$oldLlmServerUrl = $env:LLM_SERVER_URL
$oldCorsAllowedOrigins = $env:DJANGO_CORS_ALLOWED_ORIGINS
$oldViteApiBaseUrl = $env:VITE_API_BASE_URL
$runtimeToken = if ($oldToken) { $oldToken } else { [Guid]::NewGuid().ToString("N") }
$gmsKeyForLlm = if ($oldGmsKey) { $oldGmsKey } else { $DotEnvValues["GMS_KEY"] }

if (-not $gmsKeyForLlm) {
    Write-Host "GMS_KEY is not set. The app will start with mock roadmap generation."
}

Write-Host "Applying Django migrations..."
Remove-Item Env:\GMS_KEY -ErrorAction SilentlyContinue
$env:LLM_INTERNAL_TOKEN = $runtimeToken
$DatabasePath = Join-Path $BackendDir "db.sqlite3"
$DatabaseExistedBeforeMigrate = Test-Path -LiteralPath $DatabasePath
Push-Location $BackendDir
try {
    & $BackendPython manage.py migrate --noinput
    if ($LASTEXITCODE -ne 0) {
        throw "Django migrate failed with exit code $LASTEXITCODE"
    }
} finally {
    Pop-Location
    Remove-Item Env:\LLM_INTERNAL_TOKEN -ErrorAction SilentlyContinue
}

$env:LLM_INTERNAL_TOKEN = $runtimeToken
try {
    Ensure-CompanyFixtureLoaded $BackendPython $BackendDir (-not $DatabaseExistedBeforeMigrate)
} finally {
    Remove-Item Env:\LLM_INTERNAL_TOKEN -ErrorAction SilentlyContinue
}

$processes = @()
try {
    Remove-Item Env:\GMS_KEY -ErrorAction SilentlyContinue
    $env:LLM_INTERNAL_TOKEN = $runtimeToken
    $env:LLM_SERVER_URL = "http://127.0.0.1:$LlmPort"
    $env:DJANGO_CORS_ALLOWED_ORIGINS = "http://localhost:$FrontendPort,http://127.0.0.1:$FrontendPort"
    Write-Host "Starting Django backend..."
    $processes += Start-Process -FilePath $BackendPython `
        -ArgumentList @("manage.py", "runserver", "127.0.0.1:$BackendPort", "--noreload") `
        -WorkingDirectory $BackendDir `
        -WindowStyle Hidden `
        -RedirectStandardOutput (Join-Path $LogDir "backend.out.log") `
        -RedirectStandardError (Join-Path $LogDir "backend.err.log") `
        -PassThru

    Remove-Item Env:\LLM_INTERNAL_TOKEN -ErrorAction SilentlyContinue
    if ($gmsKeyForLlm) {
        $env:GMS_KEY = $gmsKeyForLlm
    }
    $env:LLM_INTERNAL_TOKEN = $runtimeToken
    Write-Host "Starting FastAPI LLM server..."
    $processes += Start-Process -FilePath $LlmPython `
        -ArgumentList @("-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "$LlmPort") `
        -WorkingDirectory $LlmDir `
        -WindowStyle Hidden `
        -RedirectStandardOutput (Join-Path $LogDir "llm.out.log") `
        -RedirectStandardError (Join-Path $LogDir "llm.err.log") `
        -PassThru

    Remove-Item Env:\GMS_KEY -ErrorAction SilentlyContinue
    Remove-Item Env:\LLM_INTERNAL_TOKEN -ErrorAction SilentlyContinue
    Remove-Item Env:\LLM_SERVER_URL -ErrorAction SilentlyContinue
    Remove-Item Env:\DJANGO_CORS_ALLOWED_ORIGINS -ErrorAction SilentlyContinue
    $env:VITE_API_BASE_URL = "http://localhost:$BackendPort"
    Write-Host "Starting Vue/Vite frontend..."
    $processes += Start-Process -FilePath $Node `
        -ArgumentList @($ViteEntrypoint, "--host", "127.0.0.1", "--port", "$FrontendPort") `
        -WorkingDirectory $FrontendDir `
        -WindowStyle Hidden `
        -RedirectStandardOutput (Join-Path $LogDir "frontend.out.log") `
        -RedirectStandardError (Join-Path $LogDir "frontend.err.log") `
        -PassThru

    Wait-Http "Backend" "http://127.0.0.1:$BackendPort/api/health/" @{}
    Wait-Http "LLM server" "http://127.0.0.1:$LlmPort/health" @{ "X-Internal-Token" = $runtimeToken }
    Wait-Http "Frontend" "http://127.0.0.1:$FrontendPort/health" @{}

    Write-Host ""
    Write-Host "PathFinder AI is running."
    Write-Host "Frontend: http://127.0.0.1:$FrontendPort"
    Write-Host "Backend:  http://127.0.0.1:$BackendPort"
    Write-Host "LLM:      http://127.0.0.1:$LlmPort"
    Write-Host "Logs:     $LogDir"
    Write-Host ""
    Write-Host "Press Ctrl+C in this window to stop all servers."

    while ($true) {
        foreach ($proc in @($processes)) {
            if ($proc.HasExited) {
                throw "Server process exited early: pid=$($proc.Id)"
            }
        }
        Start-Sleep -Seconds 1
    }
} finally {
    Write-Host ""
    Write-Host "Stopping PathFinder AI servers..."
    foreach ($proc in @($processes)) {
        Stop-ProcessTree -ProcessId $proc.Id
    }
    if ($oldToken) {
        $env:LLM_INTERNAL_TOKEN = $oldToken
    } else {
        Remove-Item Env:\LLM_INTERNAL_TOKEN -ErrorAction SilentlyContinue
    }
    if ($oldGmsKey) {
        $env:GMS_KEY = $oldGmsKey
    } else {
        Remove-Item Env:\GMS_KEY -ErrorAction SilentlyContinue
    }
    if ($oldLlmServerUrl) {
        $env:LLM_SERVER_URL = $oldLlmServerUrl
    } else {
        Remove-Item Env:\LLM_SERVER_URL -ErrorAction SilentlyContinue
    }
    if ($oldCorsAllowedOrigins) {
        $env:DJANGO_CORS_ALLOWED_ORIGINS = $oldCorsAllowedOrigins
    } else {
        Remove-Item Env:\DJANGO_CORS_ALLOWED_ORIGINS -ErrorAction SilentlyContinue
    }
    if ($oldViteApiBaseUrl) {
        $env:VITE_API_BASE_URL = $oldViteApiBaseUrl
    } else {
        Remove-Item Env:\VITE_API_BASE_URL -ErrorAction SilentlyContinue
    }
    Write-Host "Stopped."
}
}
catch {
    Write-Host ""
    Write-Host $_.Exception.Message
    exit 1
}
