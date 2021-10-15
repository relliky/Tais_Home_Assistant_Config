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
