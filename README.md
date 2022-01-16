This is my configuration of Home Assistant used in the house. 

My whole home supports automations on
- Heating/Lighting/Curtain/TV photo slideshow on-off based on presence (motion sensors) in all rooms and the garden
- Heating - thermostatic radiator valve calibration using external temperature sensor
- Lighting/Curtain/TV off at midnight
- Lighting temperature/color, speakers volume, TVs startup volume/brightness change throughout the day
- Sonos speakers grouping/ungrouping based on motion sensor to achieve music following people 
- Light/Curtain/TV/Scene on-off using physical remote buttons

UI to control:
- Homekit
  - Lighting/Heating/Curtain/TV on-off
- Lovelace 
  - All above + TV remote/Room default temperature scheduler
  
Voice Assistant:
- Alexa (free alexa services via emulated_hue)
  - Extra commands supported:
    - Alexa, Find my iPhone
      - This will set a "Find My" alert to my iphone. Other apple devices are also supported.

Remote Control:
- WOL on PCs/NAS
- HA instance (free DDNS services using DuckDNS as primary and FreeDNS as secondary)


Other smart home features but not done in Home Assistant:
- VNC server (on home server)
- Plex server (on home server)

<br><br>
This is my device list which are connected to HA with 6 protocols 

- 2.4Ghz Wifi Devices (60+ devices)
  - Lepro Wifi Bulbs (Colour/White) E27/E16/GU10
  - Yeelight Wifi Bulbs (Colour) E27
  - Meross Homekit Wifi Bulbs (Colour) E27
  - Meross Homekit Wifi Sockets
  - Meross Homekit LED Strips 
  - Magic Home LED Strips 
  - BENEXMART Blind Motors
  - Xiaomi Vacuum Robot 
  - Sonos Soundbar and Speakers
  - Eufy Cameras and Doorbells
  - Xiaomi Gateways v1/v3

- 5Ghz Wifi Devices (10+ devices)
  - Fire TV sticks/cubes
  - Samsung Smart TVs (one of them is on 2.4Ghz)
  - Amazon Echo Dots - also used as intercom (one of them is on 2.4Ghz)
  - Apple devices: iPhones, iPads, Macbooks

- Zigbee Devices (80+ devices)
  - IKEA white spectrum GU10 
  - IKEA colour GU10 
  - Xiaomi/Aqara Motion Sensors
  - Xiaomi/Aqara Door Window Contact Sensors
  - Xiaomi Wireless Buttons
  - Aqara B1 Curtain Motors
  - Xiaomi Light Sensors
  - Aqara Smart Wall Switches

- BLE Devices (20+ devices)
  - Xiaomi Motion Sensors 2
  - Xiaomi Door Window Contact Sensors 2
  - Xiaomi Temperature and Humidity Sensors
  - Xiaomi White Temperature Bulb E27
  - Philip Hue Bulbs E27
  
- Proprietary Protocol (10+ devices)
  - Tado Smart Radiator Valves

- Ethernet (10+ devices)
  - Unifi UDM, UAP-AC-PRO, UAP-AC-Lite
  - Linksys Mesh Wifi
  - Raspberry Pi 3/4
  - Intel NUC
  - Gaming PC
  - Old Windows Laptop
  - QNAP NAS
  - Philips Hue Bridge
  - Tado Bridge
  
