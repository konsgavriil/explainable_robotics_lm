import re
import pandas as pd


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
    elif 10.0 < dist <= 19.0:
        return "nearby"
    elif 19.0 < dist <= 30.0:
        return "medium distance"
    elif 30.0 < dist < 40.0:
        return "far"
    elif 51.0 <= dist:
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
    pattern = r'pts={(.*?)}.*?label=(\w)'
    match = re.search(pattern, input_string)
    direction, label = "none", "none"

    if match:
        coordinates = match.group(1)
        label = "obstacle_{}".format(match.group(2))
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


def extract_wpt_values(wpt_string):
    pattern = r"behavior-name=([^,]+),index=([^,]+)"
    match = re.search(pattern, wpt_string)
    if match:
        behaviour = match.group(1)
        ind = match.group(2)
        if behaviour == "waypt_return":
            return "start"
        else:
            return ind
    else:
        return "none"


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


log_data = open("persistance/moos_ivp_logs/s1_alpha_d.alog", "r").read()
# Split the log data into lines and process each line
lines = log_data.split("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")[-1]
lines = lines.strip().split('\n')

# Dictionary to store data
data_dict = {"deploy": [], "return": [], "next_point": [], "feedback_msg": [], "obstacle_name": [], "obstacle_proximity": [],
             "obstacle_resolved": [], "name": [], "speed": [], "heading": [], "next_point_direction": [],
             "obstacle_direction": [], "ivphelm_bhv_active": [], "vehicle_longitude": [],
             "vehicle_latitude": []}
current_state = {"name": "alpha", "deploy": "false", "return": "false", "speed": "none", "heading": "none",
                 "vehicle_longitude": "none", "vehicle_latitude": "none", "next_point": "none", "next_point_direction": "none",
                 "obstacle_name": "none", "obstacle_direction": "none", "obstacle_proximity": "none",
                 "obstacle_resolved": "false", "feedback_msg": "none", "ivphelm_bhv_active": "none"}

index_map_a = {"start": [0, -20], "0": [60, -40], "1": [180, -100], "2": [150, -40]}
index_map_b = {"start": [0, -20], "0": [60, -40], "1": [60, -160], "2": [180, -100], "3": [150, -40]}
index_map_c = {"start": [0, -20], "0": [60, -40], "1": [60, -160], "2": [150, -160], "3": [180, -100], "4": [150, -40]}
index_map_d = {"start": [0, -20], "0": [60, -40], "1": [60, -160], "2": [110, -160], "3": [150, -160], "4": [180, -100], "5": [150, -40]}

# Process each line and populate the dictionary
for line in lines:
    parts = line.split()
    key = parts[1].lower()
    current_state["obstacle_resolved"] = "false"

    if key == "moos_debug" or key =="ivphelm_bhv_running":
        continue
    elif key == "obstacle_alert":
        value = parts[3] if len(parts) == 4 else "none"
        obstacle_dir, obs_name = extract_obstacle_coordinates(value, current_state["vehicle_longitude"], current_state["vehicle_latitude"])
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
    elif key == "wpt_stat":
        value = parts[3] if len(parts) == 4 else "none"
        index = extract_wpt_values(value)
        if index != "none":
            current_state["next_point"] = "point{}".format(index)
            current_state["next_point_direction"] = extract_point_direction(index_map_d[index],
                                                                        current_state["vehicle_longitude"],
                                                                        current_state["vehicle_latitude"])
        else:
            current_state["next_point"] = "none"
            current_state["next_point_direction"] = "none"
    elif key == "obstacle_resolved":
        value = parts[3] if len(parts) == 4 else "none"
        current_state["obstacle_resolved"] = "true"
        current_state["obstacle_name"] = "none"
        current_state["obstacle_direction"] = "none"
        current_state["obstacle_proximity"] = "none"
    elif key == "os_dist_to_poly":
        value = parts[3] if len(parts) == 4 else "none"
        if current_state["obstacle_name"] != "none":
            current_state["obstacle_proximity"] = extract_obs_dist_range(value)
    else:
        value = parts[3] if len(parts) == 4 else "none"
        current_state[key] = value

    for key, value in current_state.items():
        data_dict[key].append(value)

data_dict.pop("vehicle_longitude")
data_dict.pop("vehicle_latitude")
df = pd.DataFrame.from_dict(data_dict)
print("Done")
df.to_csv("s1_alpha_d.csv", index=False)
