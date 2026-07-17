. (Join-Path $PSScriptRoot 'common.ps1')
Invoke-HaService 'homeassistant' 'reload_core_config'

