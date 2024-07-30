import pandas as pd
import math
import json
import pyperclip

def calculate_circle_points(center_x, center_y, center_z, radius, number_positions):
    points = []
    for i in range(number_positions):
        angle = 2 * math.pi * i / number_positions
        x = round(center_x + radius * math.cos(angle), 4)
        z = round(center_z + radius * math.sin(angle), 4)
        points.append((x, center_y, z))
    # Add the first point again to complete the circle
    # points.append(points[0])
    return points

def calculate_camera_orientation(point_x, point_y, point_z, center_x, center_y, center_z):
    dx = center_x - point_x
    dy = center_y - point_y
    dz = center_z - point_z

    distance = math.sqrt(dx**2 + dy**2 + dz**2)
    yaw = round(math.degrees(math.atan2(dz, dx)) - 90, 2)
    pitch = round(math.degrees(math.asin(dy / distance)), 2)
    roll = round(0, 2)  # Assuming no roll for simplicity

    return yaw, pitch, roll

def create_camera_path_dataframe(center_x, center_y, center_z, radius, number_positions, millisec, add_positions=1):
    points = calculate_circle_points(center_x, center_y, center_z, radius, number_positions)
    data = []
    time_interval = millisec / number_positions

    for i, point in enumerate(points):
        x, y, z = point
        yaw, pitch, roll = calculate_camera_orientation(x, y, z, center_x, center_y, center_z)
        time = round(i * time_interval)
        data.append((x, y, z, yaw, pitch, roll, time))

    for i in range(add_positions):

        if i <= len(data):
            data.append(data[i])
            #change the time value of the new row to be the last time value + the time interval
            data[-1] = list(data[-1])
            data[-1][-1] = round(data[-2][-1] + time_interval)

        else:
            return

    df = pd.DataFrame(data, columns=['X', 'Y', 'Z', 'Yaw', 'Pitch', 'Roll', 'Time'])

    # Find the difference in time between the rows and
    # Take the max value of the time column divide it by the number of rows, round up, and redistribute the time values of df
    # max_time = df['Time'].max()
    # time_interval = math.ceil(max_time / len(df))
    # df['Time'] = df.index * time_interval
    return df

def dataframe_to_replaymod_json(df, name, millisec):
    replaymod_json = {
        name: [
            {
                "keyframes": [
                    {
                        "time":0,
                        "properties": {
                            "timestamp": 1000
                        }
                    },
                    {
                        "time":millisec,
                        "properties": {
                            "timestamp": 2000
                        }
                    }
                ],
                "segments": [0],
                "interpolators": [
                    {
                        "type": "linear",
                        "properties": [
                            "timestamp"
                        ]
                    }
                ]
            },
            {
                "keyframes": [],
                "segments": [0] * len(df),
                "interpolators": [
                    {
                        "type": {
                            "type": "catmull-rom-spline",
                            "alpha": 0.5
                        },
                        "properties": [
                            "camera:rotation",
                            "camera:position"
                        ]
                    }
                ]
            }
        ]
    }

    for index, row in df.iterrows():
        keyframe = {
            "time":int(row["Time"]),
            "properties": {
                "camera:rotation": [row["Yaw"], row["Pitch"], row["Roll"]],
                "camera:position": [row["X"], row["Y"], row["Z"]]
            }
        }
        replaymod_json[name][1]["keyframes"].append(keyframe)

    return json.dumps(replaymod_json, indent=3)

## Define some variables to create your circular path

# The X, Y, Z coordinates (from Minecraft) where the circle is centered
center_x, center_y, center_z = 37899, 35, 28566

# The radius of the circle
radius = 200

# The number of camera positions (points) around the circle. Try things out
number_positions = 64

# The number of milliseconds for the camera to complete the path
millisec = 10000

# The number of extra positions for the camera to follow around the same path. Should be at least 1.
# This extends the time the path takes, but does not alter how long the number_positions takes.
# Example: number_positions = 10, add_positions = 5, millisec = 10000 takes 10000 milliseconds to complete around 10 positions
# and then will take another 5000 milliseconds (millisec/number_positions * add_positions) to complete the next 10 positions.
add_positions = 10

# The name for the camera path that you will see in ReplayMod
name = "Circle64"

df = create_camera_path_dataframe(center_x, center_y, center_z, radius, number_positions, millisec, add_positions)
replaymod_json = dataframe_to_replaymod_json(df, name, millisec)

# Copy to your clipboard
pyperclip.copy(replaymod_json)

