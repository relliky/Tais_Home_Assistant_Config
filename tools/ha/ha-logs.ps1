. (Join-Path $PSScriptRoot 'common.ps1')
Invoke-HaSsh 'tail -n 200 /config/home-assistant.log'

