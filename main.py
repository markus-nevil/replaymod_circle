import pandas as pd
import math
import json
import pyperclip

def calculate_circle_points(center_x, center_y, center_z, radius, number_positions):
    points = []
    for i in range(number_positions):
        angle = 2 * math.pi * i / number_positions
        x = round(center_x + radius * math.cos(angle))
        z = round(center_z + radius * math.sin(angle))
        points.append((x, center_y, z))
    # Add the first point again to complete the circle
    points.append(points[0])
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

def create_camera_path_dataframe(center_x, center_y, center_z, radius, number_positions, millisec):
    points = calculate_circle_points(center_x, center_y, center_z, radius, number_positions)
    data = []
    time_interval = millisec / number_positions

    for i, point in enumerate(points):
        x, y, z = point
        yaw, pitch, roll = calculate_camera_orientation(x, y, z, center_x, center_y, center_z)
        time = round(i * time_interval)
        data.append((x, y, z, yaw, pitch, roll, time))

    df = pd.DataFrame(data, columns=['X', 'Y', 'Z', 'Yaw', 'Pitch', 'Roll', 'Time'])
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

# Example usage
center_x, center_y, center_z = 37899, 35, 28566
radius = 200
number_positions = 32
millisec = 20000
df = create_camera_path_dataframe(center_x, center_y, center_z, radius, number_positions, millisec)
name = "Circle32_new"
replaymod_json = dataframe_to_replaymod_json(df, name, millisec)

pyperclip.copy(replaymod_json)
print(replaymod_json)
