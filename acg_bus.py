# acg_bus.py
# https://www.youtube.com/watch?v=RrPZza_vZ3w

import math
import time
import urllib.request
import webbrowser
import xml.etree.ElementTree as ET

def hav(angle):
    """Return the haversine of an angle (input in radians)"""
    return math.sin(angle/2)**2

def dist_between_coords(lat1, long1, lat2, long2):
    """Use the Haversine formula to calculate distance between two points"""
    # TODO: write test cases!
    r = 3959.0   # Radius of the earth in statute miles 
    lat1 = math.radians(float(lat1))
    long1 = math.radians(float(long1))
    lat2 = math.radians(float(lat2))
    long2 = math.radians(float(long2))
    # Reference https://en.wikipedia.org/wiki/Haversine_formula
    return 2 * r * math.asin(math.sqrt(hav(lat2 - lat1) + math.cos(lat1) \
        * math.cos(lat2) * hav(long2 - long1)))

def dist_from_do(bus):
    """Determine how far a bus is from Dan's office"""
    return dist_between_coords(do_lat, do_long, bus.find('lat').text, 
            bus.find('lon').text)

def print_bus(node):
    """Print the data for a single bus"""
    print(
            node.find('id').text, 
            node.find('rt').text, 
            '{:<3}'.format(node.find('dn').text), 
            '{:4.2f}'.format(float(node.find('lat').text)),
            '{:4.2f}'.format(float(node.find('lon').text)),
            '{:4.2f}'.format(dist_from_do(node)))

def print_buses(bus_list):
    """Print the data for a list of buses"""
    print(
        '{:^4}'.format('id'),
        '{:^3}'.format('rt'),
        '{:^3}'.format('dn'),
        '{:^5}'.format('lat'),
        '{:^5}'.format('lon'),
        '{:^4}'.format('dist'))
    for node in bus_list:
        print_bus(node)

def map_buses(buses):
    """Open browser with static map of a list of buses"""
    # https://developers.google.com/maps/documentation/maps-static/intro 
    map_url = 'https://maps.googleapis.com/maps/api/staticmap?'
    # map_url += 'center=' + str(do_lat) + ',' + str(do_long)
    map_url += '&zoom=13'
    map_url += '&size=600x600'
    map_url += '&maptype=roadmap'
    for bus in buses:
        map_url += '&markers=color:blue%7C' 
        map_url += bus.find('lat').text + ',' + bus.find('lon').text 
    map_url += '&markers=color:red%7Clabel:D%7C' 
    map_url += str(do_lat) + ',' + str(do_long)
    map_url += '&key='
    webbrowser.open(map_url)

# do = Dan's Office
do_lat, do_long = 41.980262, -87.668452

# in seconds
time_delay = 20

# in statute miles
dist_crit = 0.5

file_name = 'rt22.xml'
url = 'http://ctabustracker.com/bustime/map/getBusesForRoute.jsp?route=22'

"""
# Optional way to save the file, then process it
out = open(file_name, 'wb')
out.write(data)
out.close()
tree = ET.parse(file_name)
root = tree.getroot
"""

# Do an initial data grab and set which bus id's we'll be tracking
page = urllib.request.urlopen(url)
data = page.read()
root = ET.fromstring(data)
all_buses = root.findall('bus')
map_buses(all_buses)
# Pick out all the buses that are north of Dan's office and northbound
valid_buses = list(filter(lambda x: 'North' in x.find('d').text and 
    float(x.find('lat').text) > do_lat, root.findall('bus')))
map_buses(valid_buses)
# Store the ids of those buses
# Does converting the bus id to an int actually accomplish anything?
valid_bus_ids = set(map(lambda x: int(x.find('id').text), valid_buses))
print('Initial request made at ' + root.find('time').text + '(Chicago time)')
num_buses_on_route = len(all_buses)
print('{0} {1}'.format(num_buses_on_route, 'total buses currently on route 22'))
print('{0} {1} {2}'.format(len(valid_buses), 'northbound buses found:', 
    valid_bus_ids))
time.sleep(time_delay)

while True:
    page = urllib.request.urlopen(url)
    data = page.read()
    root = ET.fromstring(data)
    all_buses = root.findall('bus')
    valid_buses = list(filter(lambda x: int(x.find('id').text) in valid_bus_ids,
        all_buses))
    valid_close_buses = list(filter(lambda x: dist_from_do(x) < dist_crit, 
        valid_buses))
    if len(valid_close_buses) == 0:
        for bus in valid_buses:
            print('Bus ' + bus.find('id').text + ' is '
                    + '{:4.2f}'.format(dist_from_do(bus)) + 'mi. away.')
    else:
        print('{0} {1}'.format(len(valid_close_buses), 
            'valid close buses found'))
        map_buses(valid_close_buses)
        for bus in valid_close_buses:
            print('Bus ' + bus.find('id').text + ' is '
                    + '{:4.2f}'.format(dist_from_do(bus)) + 'mi. away.')
        break
    if len(all_buses) != num_buses_on_route:
        print('{0} {1}'.format(len(all_buses), 
            'total buses currently on route 22'))
    time.sleep(time_delay)
