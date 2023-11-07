import json
import requests
from random import choice,shuffle
#represent path data as tuples(Lat,Lon)
START_COORDS = (41.8789, -87.6358)
UNIT_LAT = .002
UNIT_LON = .002

maps_snap_url = "https://roads.googleapis.com/v1/snapToRoads?"
maps_static_url = "https://maps.googleapis.com/maps/api/staticmap?"
maps_key = "***INSERT API KEY HERE***"

file_path = "***INSERT FILE PATH HERE***"

def get_coordinates(start, steps, magnitude = 1,round_trip = False):
    """
    Returns a partial Brownian potion path from the start location
    Parameters
        start (tuple): the lat and lon coordinates of run beginning
        steps (int): number of steps to take
        magnitude (int): how long each step is in terms of UNIT lengths
        round_trip (bool): if path has to form closed loop
    Returns
        points (list): ordered list of lat,long tuples of path
    """
    def make_new_point(last_point,dir):
        """
        Makes lat/lon tuple of a single step
        Parameters
            last_point (tuple): lat/lon before step
            dir (tuple): unit direction of curr step
        returns
            (tuple): lat/long after step taken
        """
        delta = (dir[0] * UNIT_LAT * magnitude, dir[1] * UNIT_LON * magnitude)
        return  (last_point[0] + delta[0], last_point[1] + delta[1])
    def backwards(dir):
        return (-1*dir[0],-1*dir[1])
    def generate_directions(steps):
        directions = [(1, 0)]
        while steps > 0:
            poss_directions = [(-1, 0), (0, 1), (1, 0), (0, -1)]
            poss_directions.remove(backwards(directions[-1]))
            directions.append(choice(poss_directions))
            steps -= 1
        if round_trip:
            ret_directions = directions[:]
            shuffle(ret_directions)
            directions.extend(backwards(ret_dir) for ret_dir in ret_directions)
        return directions
    points = [start]
    for d in generate_directions(steps):
        points.append(make_new_point(points[-1],d))
    return points

def coordinate_params(points):
    """
    Converts a list of coordinate tuples into input for the roads api
    """
    msg_pts = "|".join(str(lat)+","+str(lon) for lat,lon in points)
    params = dict(
        path = msg_pts,
        interpolate = True,
        key = maps_key
    )
    return params

def map_params(text):
    """
    converts JSON data of path into input for the maps static API
    includes blue highlighted path with red marker for start/end
    """
    coords = []
    for point in text["snappedPoints"]:
        coords.append(str(point["location"]["latitude"]) + "," + str(point["location"]["longitude"]))
    msg_pts = "color:0x0000ff|weight:2"+"|".join(coords)
    params = dict(
        path = msg_pts,
        markers="size:small|color=0xFFFFCC|41.823770,-87.783570",
        center=START_COORDS,
        zoom=14,
        size="400x400",
        key = maps_key
    )
    return params

def create_map(steps,magnitude,round_trip):
    """
    saves a png of map path
    """
    snap_params = coordinate_params(get_coordinates(START_COORDS,steps,magnitude,round_trip))
    snap_request = requests.get(maps_snap_url,params = snap_params)
    static_params = map_params(snap_request.json())
    static_request = requests.get(maps_static_url,params = static_params)
    with open(file_path,"wb") as file:
        file.write(static_request.content)
    return ("Success")

print(create_map(8,2,True))