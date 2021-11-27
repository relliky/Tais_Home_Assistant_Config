This is my configuration of Home Assistant used in the house. 

My whole home supports automations on
- Heating/Lighting/Curtain/TV photo slideshow on-off based on presence (motion sensors) in all rooms
- Heating - Thermostatic radiator valve calibration using external temperature sensor
- Lighting/Curtain/TV off at midnight
- Lighting temperature/color, speakers/TVs default volume changes throughout the day
- Sonos Speakers Grouping/Ungrouping Based On Motion Sensor to achieve music following people 
- Light/Curtain/TV/Scene on-off using physical remote buttons

UI to control:
- Homekit
  - Lighting/Heating/Curtain/TV on-off
- Lovelace 
  - All above + TV remote/Room default temperature scheduler
  
Voice Assistant:
- Alexa (via emulated_hue)

Remote Control:
- WOL on PCs/NAS
- HA instance (DDNS using DuckDNS as primary and NoIP as secondary)


Other smart home features but not done in Home Assistant:
- VNC server (on home server)
- Plex server (on home server)


This is my device list which are connected to HA with 5 protocols 

Wifi Devices
- Lepro Wifi Bulbs (Colour/White) E27/E16
- Yeelight Wifi Bulbs (Colour) E27
- Meross Homekit Wifi Bulbs (Colour) E27
- Meross Homekit Wifi Sockets
- Meross Homekit LED Strips 
- Magic Home LED Strips 
- BENEXMART Blind Motors
- Xiaomi Vacuum Robot 
- Samsung Smart TVs
- Fire TV sticks/cubes
- Sonos soundbar and speakers
- iPhones, iPads
- Amazon Echo Dots - also used as intercom 
- Eufy Cameras
- Xiaomi Gateways v1/v3

Zigbee Devices 
- IKEA white spectrum GU10 
- IKEA colour GU10 
- Xiaomi/Aqara Motion Sensors
- Xiaomi/Aqara Door&Window Contact Sensors
- Xiaomi Wireless Buttons
- Aqara B1 Curtain Motors
- Xiaomi Light Sensors
- Aqara Smart Wall Switches

BLE Devices
- Xiaomi Motion Sensors
- Xiaomi Temperature and Humidity Sensors
- Xiaomi White Temperature Bulb E27

Proprietary Protocol
- Tado thermostat radiator valves

Ethernet 
- Google Mesh Wifi
- Linksys Mesh Wifi
- Raspberry Pi 3b/4b
- Windows Machines
- QNAP NAS
- Philips Hue Bridge
  
