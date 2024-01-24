import re
import pandas as pd


def extract_waypoint_direction(survey_point, survey_points, vhc_x, vhc_y):
    if survey_points != "none":
        pairs = survey_points[1:-1].split(':')
        coordinates_dict = {}
        index = 0
        for pair in pairs:
            sp_x, sp_y = pair.split(',')
            coordinates_dict[index] = [float(sp_x), float(sp_y)]
            index += 1
        return extract_point_direction(coordinates_dict[int(survey_point)], vhc_x, vhc_y)
    return "none"


def extract_surface_event(at_surface_time):
    return "true" if int(float(at_surface_time)) > 0 else "false"


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


def extract_depth_range(d):
    dep = float(d)
    if dep == 0.0:
        return "on surface"
    elif 0 < dep <= 1.0:
        return "shallow"
    elif 1.0 < dep <= 2.5:
        return "moderate"
    elif 2.5 < dep <= 4.0:
        return "deep"
    elif 4.0 < dep:
        return "very deep"
    elif dep == 199.0:
        return "max depth"
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


def extract_node_values(node_string):
    pattern = r'NAME=(\w+),X=(.*?),Y=(.*?),SPD=(.*?),HDG=(.*?),DEP=(.*?),'
    match = re.search(pattern, node_string)
    if match:
        name = match.group(1)
        nav_x = match.group(2)
        nav_y = match.group(3)
        spd = extract_speed_range(match.group(4))
        hdg = extract_heading_range(match.group(5))
        dep = extract_depth_range(match.group(6))

        return name, nav_x, nav_y, spd, hdg, dep
    else:
        return "none"


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


def extract_bhv_settings_values(bhv_settings_string):
    name, pts = "none", "none"
    name_pattern = r"name=([^,]+)"
    pts_pattern = r"pts=({[^}]+})"

    name_match = re.search(name_pattern, bhv_settings_string)
    pts_match = re.search(pts_pattern, bhv_settings_string)

    if pts_match and "survey" in name_match.group(1):
        pts = pts_match.group(1)

    return pts


def extract_loiter_values(loiter_string):
    pattern = r"index=(\d+),capture_hits=(\d+)"
    match = re.search(pattern, loiter_string)

    if match:
        index = match.group(1)
        return index
    return "none"


log_data = open("persistance/moos_ivp_logs/s4_delta_d.alog", "r").read()
# Split the log data into lines and process each line
lines = log_data.split("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")[-1]
lines = lines.strip().split('\n')

# Dictionary to store data
data_dict = {"objectives": [], "deploy": [], "return": [], "next_waypoint": [], "feedback_msg": [],
             "next_loiter_point": [], "gps_update_received": [], "depth": [], "vehicle_at_surface": [], "periodic_ascend": [],
             "waypoint_direction": [], "loiter_point_direction": [], "vehicle_longitude": [], "vehicle_latitude": [],
             "speed": [], "heading": [], "survey_points": [], "name": [],  "ivphelm_bhv_active": []}
current_state = {"objectives": "Loiter between points 0 to 7 until a survey objective is provided, "
                                                    "then perform the survey and finally return back to starting point",
                 "name": "delta", "deploy": "false", "return": "false", "next_waypoint": "none",
                 "waypoint_direction": "none", "survey_points": "none", "feedback_msg": "none", "next_loiter_point": "none",
                 "loiter_point_direction": "none", "speed": "none", "heading": "none", "depth": "none", "vehicle_longitude": "none",
                 "vehicle_latitude": "none", "gps_update_received": "none", "vehicle_at_surface": "true",
                 "periodic_ascend": "false", "ivphelm_bhv_active": "none"}

starting_point = [0, 0]
# loiter_points_1 = {0: [28, -62], 1: [38, -72], 2: [38, -88], 3: [28, -98], 4: [12, -98], 5: [2, -88], 6: [2, -72], 7: [12, -62]}
# loiter_points_2 = {0: [48, -62], 1: [58, -72], 2: [58, -88], 3: [48, -98], 4: [32, -98], 5: [22, -88], 6: [22, -72], 7: [32, -62]}
# loiter_points_3 = {0: [38, -32], 1: [48, -42], 2: [48, -58], 3: [38, -68], 4: [22, -68], 5: [12, -58], 6: [12, -42], 7: [22, -32]}
loiter_points_4 = {0: [58, -12], 1: [68, -22], 2: [68, -38], 3: [58, -48], 4: [42, -48], 5: [32, -38], 6: [32, -22], 7: [42, -12]}

# Process each line and populate the dictionary
for line in lines:
    parts = line.split()
    key = parts[1].lower()
    current_state["gps_update_received"] = "false"

    if key == "moos_debug" or key == "pending_surface" or key == "psurface":
        continue
    elif key == "node_report_local":
        value = parts[3] if len(parts) == 4 else "none"
        if value != "none" and value:
            name, x, y, speed, heading, depth = extract_node_values(value)
            current_state["name"] = name
            current_state["speed"] = speed
            current_state["heading"] = heading
            current_state["depth"] = depth
            current_state["vehicle_longitude"] = x
            current_state["vehicle_latitude"] = y
    elif key == "wpt_stat":
        value = parts[3] if len(parts) == 4 else "none"
        if value != "none" and extract_wpt_values(value) != "none":
            index = extract_wpt_values(value)
            if index == "start":
                current_state["next_waypoint"] = "{}ing_point".format(index)
                current_state["waypoint_direction"] = extract_point_direction(starting_point,
                                                                                  current_state["vehicle_longitude"],
                                                                                  current_state["vehicle_latitude"])
            else:
                current_state["next_waypoint"] = "point{}".format(index)
                current_state["waypoint_direction"] = extract_waypoint_direction(index,
                                                                                         current_state["survey_points"],
                                                                                         current_state["vehicle_longitude"],
                                                                                         current_state["vehicle_latitude"])
            current_state["next_loiter_point"] = "none"
            current_state["loiter_point_direction"] = "none"
    elif key == "bhv_settings":
        value = parts[3] if len(parts) == 4 else "none"
        points = extract_bhv_settings_values(value)
        current_state["survey_points"] = points
        if points != "none":
            current_state["next_loiter_point"] = "none"
            current_state["loiter_point_direction"] = "none"
    elif key == "gps_update_received":
        current_state["gps_update_received"] = "true"
    elif key == "loiter_report":
        value = parts[3] if len(parts) == 4 else "None"
        loiter_index = extract_loiter_values(value)
        current_state["next_loiter_point"] = "point{}".format(loiter_index)
        current_state["loiter_point_direction"] = extract_point_direction(loiter_points_4[int(loiter_index)],
                                                                          current_state["vehicle_longitude"],
                                                                          current_state["vehicle_latitude"])
        current_state["next_waypoint"] = "none"
        current_state["survey_points"] = "none"
        current_state["feedback_msg"] = "none"
        current_state["waypoint_direction"] = "none"
    elif key == "time_at_surface":
        value = parts[3] if len(parts) == 4 else "None"
        current_state["vehicle_at_surface"] = extract_surface_event(value)
    else:
        value = parts[3] if len(parts) == 4 else "None"
        current_state[key] = value

    for key, value in current_state.items():
        data_dict[key].append(value)


data_dict.pop("vehicle_longitude")
data_dict.pop("vehicle_latitude")
data_dict.pop("survey_points")
df = pd.DataFrame.from_dict(data_dict)
print("Done")
df.to_csv("s4_delta_d.csv", index=False)
