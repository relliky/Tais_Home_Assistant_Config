Follow my activity on 

Home Assistant Community activity https://community.home-assistant.io/u/relliky/summary

在瀚思彼岸HomeAssistant中文论坛也可以关注我的动态 https://bbs.hassbian.com/?41990

我的手机Lovelace界面展示 https://www.bilibili.com/video/BV1hb4y1a76i?share_source=copy_web 

--------------------------------------------------------------------------  

This is my configuration of Home Assistant used in the house. 

All the rooms in my place supports automations on
- Heating/Lighting/Curtain/TV photo slideshow automatically on-off based on presence (motion sensors) in all rooms and the garden
- Heating - smart thermostatic radiator valve calibration using external temperature sensor
- Lighting/Curtain/TV off at midnight
- Lighting temperature/color, speakers volume, TVs startup volume/brightness change throughout the day adaptively
- Sonos speakers grouping/ungrouping based on motion sensor to achieve music/TV audio following people 
- Light/Curtain/TV/Scene on-off using physical remote buttons

GUI to control:
- [OBSOLETE] Apple Home app used by MacBook/iPhone/iPad
  - Lighting/Heating/Curtain/TV on-off
- Home Assistant Dashboard used by any laptops/smart phones/tablets
  - All above + TV remote/Room default temperature scheduler
  - User permission control. Each room user only has access to their rooms and common areas.
  
Voice Assistant:
- Alexa (free alexa integration via Emulated Hue)
  - Support controlling HA appliances and calling HA scripts to set a scene
  - Extra commands supported:
    - Alexa, Find my iPhone
      - This will set a "Find My" alert to my iphone. Other apple devices are also supported.

Remote Control:
- WOL on PCs/NAS
- HA instance (free DDNS services using DuckDNS as primary and FreeDNS as secondary)


Other smart features but not done in Home Assistant:
- Video/Game streaming from a PC to multiple Fire TV devices in sync by using Parsec. Useful to play videos sync living room TV content to dining room TV content wirelessly.
- Game streaming/Video streaming using NVDIA GPU and Moonlight from the gaming PC to TV/computer/phone/tablets/nintendo switch
- Proxmox VE running
  - Home Assistant OS VM
  - Plex Media Server LXC
    - Streamed from multiple Plex client apps from TV/computer/phones/tablets for its video and music library
    - Streamed from Alexa-enabled devices for its music library
    - DLNA server feeding into HA media player
  - Ubuntu LXC
    - Running Airconnect to enable Sonos speakers with Airplay
    - Scheduled Unifi AP reboot
- VNC server (on a gaming PC and an old laptop)
- All TVs supports airplay for casting contents from iPhone/iPad


<br><br>

This is my device list which are connected to HA via 6 protocols 

- 2.4Ghz Wifi Devices (60+ devices) 
  - Tuya/Localtuya/Smartthings integration
    - Lepro Wifi Bulbs (Colour/White) E27/E16/GU10 
    - BENEXMART Blind Motors 
  - Homekit controller integration
    - Meross Homekit Wifi Bulbs (Colour) E27 (Homekit)
    - Meross Homekit Wifi Wall Plugs
    - Meross Homekit LED Strips 
  - Yeelight integration
    - Yeelight Wifi Bulbs (Colour) E27 (Yeelight)
  - Magic Home/SmartThings integration
    - Magic Home LED Strips 
  - Xiaomi IoT/Xiaomi MIoT Auto integration
    - Xiaomi Vacuum Robot 
  - Sonos integration
    - Sonos Soundbar and Speakers
  - Eufy integration
    - Eufy Doorbells
  - WebRTC Camera
    - Eufy Cameras
  - Xiaomi Gateway 3 integration
    - Xiaomi Gateways v3
  - Xiaomi Gateway integration
    - Xiaomi Gateways v1

- 5Ghz Wifi Devices (10+ devices)
  - Andriod TV integration 
    - Fire TV sticks/cubes
  - SamsungTV Smart integration/SmartThings integration
    - Samsung Smart TVs (one of them is on 2.4Ghz)
  - Alexa Media Player integration
    - Amazon Echo Dots - also used as intercom (one of them is on 2.4Ghz)
  - iCloud integration
    - Apple devices: iPhones, iPads, Macbooks
  - WOL integration/RPC addon
    - Windows laptops

- Zigbee Devices (80+ devices)
  - Philps Hue integration
    - IKEA white spectrum GU10 
    - IKEA colour GU10 
  - Xiaomi Gateway 3/Xiaomi Gateway integration
    - Xiaomi/Aqara Motion Sensors
    - Xiaomi/Aqara Door Window Contact Sensors
    - Xiaomi Wireless Buttons
    - Aqara B1 Curtain Motors
    - Xiaomi Light Sensors
    - Aqara Smart Wall Switches

- BLE Devices (20+ devices)
  - Philps Hue integration
    - Philip Hue Bulbs E27
  - Xiaomi Gateway 3 integration
    - Xiaomi Motion Sensors 2
    - Xiaomi Door Window Contact Sensors 2
    - Xiaomi Temperature and Humidity Sensors
    - Xiaomi White Temperature Bulb E27
  
- Proprietary Protocol (10+ devices)
  - Tado integration
    - Tado Smart Radiator Valves

- Ethernet (10+ devices)
  - Ubuiquiti intgration
    - Unifi UDM, U6-LITE
  - WOL integration/RPC addon
    - Intel NUC
    - Gaming PC
    - Old Windows Laptop
  - Synology integration
    - Synology NAS 
  - Philps Hue integration
    - Philips Hue Bridge
  - Tado integration
    - Tado Bridge
  
Other integration I haven't mentioned above. 

- Lighting/Switches
  - Adaptive Lighting

- Climate
  - Met Office
  - Sun

- Phone
  - Mobile App

- Voice control
  - Emulated Hue

- Media
  - DLNA Digital Media Renderer
  - Plex

- Energy
  - Hildebrand Glow (DCC)
  - Meross Cloud IoT

- HA Dashbaord
  - Browser Mod
  - Scheduler

- System Monitoring
  - Certificate Expiry
  - CPU Speed
  - DNS IP
  - Unifi Network
  - Sinology DSM

- HA General
  - Pyscript
  - HACS



