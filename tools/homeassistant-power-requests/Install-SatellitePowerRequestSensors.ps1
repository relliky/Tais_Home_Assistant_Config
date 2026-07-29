$ErrorActionPreference = 'Stop'

$serviceName = 'HASS.Agent Satellite Service'
$configPath = 'C:\Program Files (x86)\LAB02 Research\HASS.Agent Satellite Service\config\sensors.json'
$logPath = 'C:\ProgramData\HomeAssistantPowerRequests\install.log'

New-Item -ItemType Directory -Force -Path (Split-Path -Parent $configPath) | Out-Null
New-Item -ItemType Directory -Force -Path (Split-Path -Parent $logPath) | Out-Null

function Write-InstallLog {
    param([string]$Message)

    $timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    Add-Content -LiteralPath $logPath -Value "[$timestamp] $Message" -Encoding UTF8
}

try {
    if (Test-Path -LiteralPath $configPath) {
        $backupPath = "$configPath.bak.$(Get-Date -Format 'yyyyMMddHHmmss')"
        Copy-Item -LiteralPath $configPath -Destination $backupPath -Force
        $sensors = Get-Content -LiteralPath $configPath -Raw -Encoding UTF8 | ConvertFrom-Json
        if ($null -eq $sensors) {
            $sensors = @()
        }
        if ($sensors -isnot [System.Array]) {
            $sensors = @($sensors)
        }
        Write-InstallLog "Backed up existing sensors file to $backupPath"
    } else {
        $sensors = @()
        Write-InstallLog "No existing sensors file found; creating a new one"
    }

    $namesToReplace = @(
        'tais_pc_power_sleep_block_state',
        'tais_pc_power_sleep_block_details'
    )

    $sensors = @($sensors | Where-Object { $namesToReplace -notcontains $_.Name })

    $sensors += [pscustomobject]@{
        Type           = 'PowershellSensor'
        Id             = 'f1eb58c1-a2b2-4c6d-b6c1-b868f72a5eb2'
        FriendlyName   = 'TAIS PC Power Sleep Block State'
        UpdateInterval = 30
        Query          = 'C:\ProgramData\HomeAssistantPowerRequests\Get-PowerRequestsState.ps1'
        Scope          = ''
        WindowName     = ''
        Category       = ''
        Counter        = ''
        Instance       = ''
        Name           = 'tais_pc_power_sleep_block_state'
        ApplyRounding  = $false
        Round          = $null
    }

    $sensors += [pscustomobject]@{
        Type           = 'PowershellSensor'
        Id             = '5f5a75c0-e607-4094-8235-424cc9f9fef6'
        FriendlyName   = 'TAIS PC Power Sleep Block Details'
        UpdateInterval = 30
        Query          = 'C:\ProgramData\HomeAssistantPowerRequests\Get-PowerRequestsDetails.ps1'
        Scope          = ''
        WindowName     = ''
        Category       = ''
        Counter        = ''
        Instance       = ''
        Name           = 'tais_pc_power_sleep_block_details'
        ApplyRounding  = $false
        Round          = $null
    }

    $json = $sensors | ConvertTo-Json -Depth 8
    Set-Content -LiteralPath $configPath -Value $json -Encoding UTF8
    Write-InstallLog "Stored $(@($sensors).Count) service sensor(s)"

    Restart-Service -Name $serviceName -Force
    Write-InstallLog "Restarted $serviceName"

    Start-Sleep -Seconds 5
    $svc = Get-Service -Name $serviceName
    Write-InstallLog "$serviceName status: $($svc.Status)"
    exit 0
} catch {
    Write-InstallLog "ERROR $($_.Exception.Message)"
    throw
}
