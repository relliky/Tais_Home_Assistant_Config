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
  1. Lepro Wifi Bulbs (Colour/White) E27/E16
  2. Yeelight Wifi Bulbs (Colou) E27
  3. Meross Homekit Wifi Bulbs (Colou) E27
  4. Meross Homekit Wifi Sockets
  5. Meross Homekit LED Strips 
  6. Magic Home LED Strips 
  7. BENEXMART Blind Motors
  8. Xiaomi Vacuum Robot 
  9. Samsung Smart TVs
  10. Fire TV sticks/cubes
  11. Sonos soundbar and speakers
  12. iPhones, iPads
  13. Amazon Echo Dots
  14. Eufy Cameras
  15. Xiaomi Gateway v1/v3

Zigbee Devices 
  1. IKEA white spectrum GU10 
  2. IKEA colour GU10 
  3. Xiaomi/Aqara Motion Sensors
  4. Xiaomi/Aqara Door&Window Contact Sensors
  5. Xiaomi Wireless Buttons
  6. Aqara B1 Curtain Motors
  7. Xiaomi Light Sensors
  8. Aqara Smart Wall Switches

BLE Devices
  1. Xiaomi Motion Sensors
  2. Xiaomi Temperature and Humidity Sensors
  3. Xiaomi White Temperature Bulb E27

Proprietary Protocol
  1. Tado thermostat radiator valves

Ethernet 
  1. Google Mesh Wifi
  2. Linksys Mesh Wifi
  3. Raspberry Pis
  4. Windows Machines
  5. QNAP NAS
  6. Philips Hue Bridge
  
