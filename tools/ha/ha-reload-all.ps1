. (Join-Path $PSScriptRoot 'common.ps1')
Invoke-HaService 'homeassistant' 'reload_core_config'
Invoke-HaService 'automation' 'reload'
Invoke-HaService 'script' 'reload'
Invoke-HaService 'scene' 'reload'
Invoke-HaService 'template' 'reload'
