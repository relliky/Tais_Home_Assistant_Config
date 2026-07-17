$ErrorActionPreference = 'Stop'

$script:HaHost = '192.168.1.8'
$script:HaSshHost = 'home-192-168-1-8'
$script:HaUrl = "http://${script:HaHost}:8123"
$script:TokenFile = Join-Path $PSScriptRoot '.ha_token'

function Get-HaToken {
    if ($env:HA_TOKEN) {
        return $env:HA_TOKEN.Trim()
    }

    if (Test-Path $script:TokenFile) {
        return (Get-Content -Raw -Path $script:TokenFile).Trim()
    }

    throw "Missing Home Assistant token. Set `$env:HA_TOKEN or create $script:TokenFile containing a Long-Lived Access Token."
}

function Invoke-HaApiPost {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path,

        [hashtable]$Body = @{}
    )

    $token = Get-HaToken
    $headers = @{ Authorization = "Bearer $token" }
    $json = $Body | ConvertTo-Json -Depth 10

    Invoke-RestMethod -Method Post -Uri "$script:HaUrl$Path" -Headers $headers -ContentType 'application/json' -Body $json
}

function Invoke-HaService {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Domain,

        [Parameter(Mandatory = $true)]
        [string]$Service,

        [hashtable]$Body = @{}
    )

    Invoke-HaApiPost -Path "/api/services/$Domain/$Service" -Body $Body | Out-Null
    Write-Host "Called $Domain.$Service"
}

function Invoke-HaConfigCheck {
    $result = Invoke-HaApiPost -Path '/api/config/core/check_config'
    $result | ConvertTo-Json -Depth 10

    if ($result.result -ne 'valid') {
        throw 'Home Assistant configuration is not valid.'
    }
}

function Invoke-HaSsh {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Command
    )

    ssh $script:HaSshHost $Command
    if ($LASTEXITCODE -ne 0) {
        throw "SSH command failed with exit code $LASTEXITCODE"
    }
}
