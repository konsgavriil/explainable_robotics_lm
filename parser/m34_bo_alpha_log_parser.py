import re
import pandas as pd


def extract_loiter_point_direction(loiter_point, loiter_points, vhc_x, vhc_y):
    if loiter_points != "none" and loiter_point != "none":
        pairs = loiter_points[1:-1].split(':')
        coordinates_dict = {}
        index = 0
        for pair in pairs:
            lp_x, lp_y = pair.split(',')
            coordinates_dict[index] = [float(lp_x), float(lp_y)]
            index += 1
        return extract_point_direction(coordinates_dict[int(loiter_point[-1])], vhc_x, vhc_y)
    return "none"


def extract_collision_avd_mode(collision_avd_string):
    mode = "none"
    mode_pattern = r'Mode:((\w+):(\w+))'
    mode_match = re.search(mode_pattern, collision_avd_string)

    if mode_match:
        mode = mode_match.group(1)

    return mode

def extract_loiter_points(bhv_settings_string):
    name, pts = "none", "none"
    name_pattern = r"name=([^,]+)"
    pts_pattern = r"pts=({[^}]+})"

    name_match = re.search(name_pattern, bhv_settings_string)
    pts_match = re.search(pts_pattern, bhv_settings_string)

    if pts_match and "loiter" in name_match.group(1):
        pts = pts_match.group(1)

    return pts


def extract_contact_info(contact_string):
    # Extract vname
    vname_match = re.search(r'vname=([^,]+)', contact_string)
    vname = vname_match.group(1) if vname_match else "none"

    # Extract range
    range_match = re.search(r'range=([^,]+)', contact_string)
    range_value = float(range_match.group(1)) if range_match else "none"

    return vname, range_value


def extract_point_direction(point_coord: list, vhc_x, vhc_y):
    point_dir_list = []

    if point_coord[1] > float(vhc_y):
        point_dir_list.append("north")
    elif point_coord[1] < float(vhc_y):
        point_dir_list.append("south")

    if point_coord[0] > float(vhc_x):
        point_dir_list.append("east")
    elif point_coord[0] < float(vhc_x):
        point_dir_list.append("west")

    direction = "".join(point_dir_list)

    return direction


def extract_obs_dist_range(distance):
    dist = float(distance)
    if dist == 0.0:
        return "on obstacle"
    elif 0 < dist <= 5.0:
        return "very close"
    elif 5.0 < dist <= 10.0:
        return "close"
    elif 10.0 < dist <= 20.0:
        return "nearby"
    elif 20.0 < dist < 25.0:
        return "far"
    elif 25.0 <= dist:
        return "very far"
    return "none"


def extract_contact_dist_range(distance):
    dist = float(distance)
    if dist == 0.0:
        return "on vehicle"
    elif 0 < dist <= 8.0:
        return "very close"
    elif 8.0 < dist <= 11.0:
        return "close"
    elif 11.0 < dist <= 15.0:
        return "medium"
    elif 15.0 < dist <= 20.0:
        return "nearby"
    elif 20.0 < dist < 40.0:
        return "far"
    elif 40.0 <= dist:
        return "very far"
    return "none"


def extract_speed_range(s):
    spd = float(s)
    if spd == 0.0:
        return "idle"
    elif 0 < spd <= 0.5:
        return "low"
    elif 0.5 < spd <= 1.0:
        return "moderate"
    elif 1.0 < spd <= 1.5:
        return "fast"
    elif 1.5 < spd < 2.0:
        return "very fast"
    elif spd == 2.0:
        return "max speed"
    return "none"


def extract_heading_range(h):
    hdg = float(h)
    if hdg == 0.0:
        return "north"
    elif hdg == 90.0:
        return "east"
    elif hdg == 180.0:
        return "south"
    elif hdg == 270.0:
        return "west"
    elif 0.0 < hdg < 90.0:
        return "northeast"
    elif 90.0 < hdg < 180.0:
        return "southeast"
    elif 180.0 < hdg < 270.0:
        return "southwest"
    elif 270.0 < hdg <= 359.99:
        return "northwest"
    return hdg


def extract_obstacle_coordinates(input_string, vhc_x, vhc_y):
    pattern = r'pts={(.*?)}.*?label=(\w+)'
    match = re.search(pattern, input_string)

    if match:
        coordinates = match.group(1)
        label = "obstacle_{}".format(match.group(2)[-1])
        coordinates_list = [tuple(map(float, pair.split(','))) for pair in coordinates.split(':')]

        sum_x = sum(coord[0] for coord in coordinates_list)
        sum_y = sum(coord[1] for coord in coordinates_list)

        mean_obs_x = sum_x / len(coordinates_list)
        mean_obs_y = sum_y / len(coordinates_list)

        obstacle_list = []

        if mean_obs_y > float(vhc_y):
            obstacle_list.append("north")
        elif mean_obs_y < float(vhc_y):
            obstacle_list.append("south")

        if mean_obs_x > float(vhc_x):
            obstacle_list.append("east")
        elif mean_obs_x < float(vhc_x):
            obstacle_list.append("west")

        direction = "".join(obstacle_list)

        return direction, label


def extract_node_values(node_string):
    pattern = r'NAME=(\w+),X=(.*?),Y=(.*?),SPD=(.*?),HDG=(.*?),'
    match = re.search(pattern, node_string)
    if match:
        name = match.group(1)
        nav_x = match.group(2)
        nav_y = match.group(3)
        spd = extract_speed_range(match.group(4))
        hdg = extract_heading_range(match.group(5))

        return name, nav_x, nav_y, spd, hdg
    else:
        return "none"


log_data = open("persistance/moos_ivp_logs/m34_alpha_a.alog", "r").read()
# Split the log data into lines and process each line
lines = log_data.split("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")[-1]
lines = lines.strip().split('\n')

# Dictionary to store data
data_dict = {"objective": [], "deploy": [], "return": [], "station_keep": [], "next_loiter_point": [], "obstacle_name": [],
             "obstacle_proximity": [], "contact_range": [], "contact_resolved": [], "collision_avoidance_mode": [],
             "speed": [], "heading": [], "loiter_point_direction": [], "new_loiter_area": [], "obstacle_direction": [],
             "loiter_points": [], "vehicle_longitude": [], "vehicle_latitude": [], "contact_name": [], "name": [],
             "ivphelm_bhv_active": []}
current_state = {"objective": "Loiter around in different areas which are selected randomly, while avoiding obstacles "
                              "and collision with other vessels. Finally, once the command is provided by the operator,"
                              " return to starting point.", "name": "gilda", "deploy": "false", "return": "false",
                 "speed": "none", "heading": "none", "vehicle_longitude": "none", "vehicle_latitude": "none",
                 "station_keep": "false", "next_loiter_point": "none", "loiter_point_direction": "none",
                 "new_loiter_area": "false", "obstacle_name": "none", "obstacle_direction": "none",
                 "obstacle_proximity": "none", "contact_name": "none", "contact_range": "none",
                 "contact_resolved": "none", "collision_avoidance_mode": "none",
                 "loiter_points": "none", "ivphelm_bhv_active": "none"}

# Process each line and populate the dictionary
for line in lines:
    parts = line.split()
    key = parts[1].lower()
    current_state["contact_resolved"] = "false"
    current_state["new_loiter_area"] = "false"
    current_state["collision_avoidance_mode"] = "none"

    if key == "moos_debug":
        continue
    elif key == "obstacle_alert":
        obstacle_dir, obs_name = extract_obstacle_coordinates(parts[3], current_state["vehicle_longitude"], current_state["vehicle_latitude"]) if len(parts) == 4 else "none"
        current_state["obstacle_name"] = obs_name
        current_state["obstacle_direction"] = obstacle_dir
    elif key == "node_report_local":
        value = parts[3] if len(parts) == 4 else "none"
        if value != "none" and value:
            name, x, y, speed, heading = extract_node_values(value)
            current_state["name"] = name
            current_state["speed"] = speed
            current_state["heading"] = heading
            current_state["vehicle_longitude"] = x
            current_state["vehicle_latitude"] = y
    elif key == "loiter_index_a":
        value = parts[3] if len(parts) == 4 else "none"
        current_state["next_loiter_point"] = "point{}".format(int(float(value)))
        current_state["loiter_point_direction"] = extract_loiter_point_direction(current_state["next_loiter_point"],
                                                                                 current_state["loiter_points"],
                                                                                 current_state["vehicle_longitude"],
                                                                                 current_state["vehicle_latitude"])
    elif key == "contact_info":
        value = " ".join(parts[3:]) if len(parts) > 4 else "none"
        current_state[key] = value
    elif key == "avd_info":
        value = " ".join(parts[3:]) if len(parts) > 4 else "none"
        current_state["collision_avoidance_mode"] = extract_collision_avd_mode(value)
    elif key == "os_dist_to_poly":
        value = parts[3] if len(parts) == 4 else "none"
        current_state["obstacle_proximity"] = extract_obs_dist_range(value)
    elif key == "contacts_recap":
        value = parts[3] if len(parts) == 4 else "none"
        n, r = extract_contact_info(value)
        current_state["contact_name"] = n
        current_state["contact_range"] = extract_contact_dist_range(r) if r != "none" else "none"
    elif key == "bhv_settings":
        value = parts[3] if len(parts) == 4 else "none"
        value = extract_loiter_points(value)
        if value != "none":
            current_state["new_loiter_area"] = "true"
            current_state["loiter_points"] = value
    elif key == "ivphelm_bhv_active":
        value = parts[3] if len(parts) == 4 else "none"
        if "waypt_return" in value or "station-keep" in value:
            current_state["loiter_points"] = "none"
            current_state["next_loiter_point"] = "none"
            current_state["loiter_point_direction"] = "none"
        current_state[key] = value

    else:
        value = parts[3] if len(parts) == 4 else "none"
        current_state[key] = value

    for key, value in current_state.items():
        data_dict[key].append(value)

data_dict.pop("vehicle_longitude")
data_dict.pop("vehicle_latitude")
data_dict.pop("loiter_points")
df = pd.DataFrame.from_dict(data_dict)
print("Done")
df.to_csv("m34_bo_alpha_a.csv", index=False)
