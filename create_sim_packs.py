from pathlib import Path

def make_sdf(kind):
    if kind == "A":
        width, depth = 0.19, 0.14
        color = "0.15 0.38 0.65 1"
        bolts = [
            (-0.07, -0.045),
            (0.07, -0.045),
            (-0.07, 0.045),
            (0.07, 0.045),
        ]
    else:
        width, depth = 0.23, 0.09
        color = "0.70 0.38 0.12 1"
        bolts = [
            (-0.085, 0.02),
            (0.0, 0.02),
            (0.085, 0.02),
        ]

    sdf = f"""
<sdf version="1.7">
  <model name="lib_pack_{kind}">
    <static>true</static>
    <link name="housing">
      <visual name="body">
        <pose>0 0 0.025 0 0 0</pose>
        <geometry>
          <box>
            <size>{width} {depth} 0.05</size>
          </box>
        </geometry>
        <material>
          <ambient>{color}</ambient>
          <diffuse>{color}</diffuse>
        </material>
      </visual>
      <collision name="body_collision">
        <pose>0 0 0.025 0 0 0</pose>
        <geometry>
          <box>
            <size>{width} {depth} 0.05</size>
          </box>
        </geometry>
      </collision>
"""

    for i, (x, y) in enumerate(bolts):
        sdf += f"""
      <visual name="bolt_{i+1}">
        <pose>{x} {y} 0.0545 0 0 0</pose>
        <geometry>
          <cylinder>
            <radius>0.009</radius>
            <length>0.009</length>
          </cylinder>
        </geometry>
        <material>
          <ambient>0.9 0.7 0.2 1</ambient>
          <diffuse>0.9 0.7 0.2 1</diffuse>
        </material>
      </visual>
"""

    sdf += """
    </link>
  </model>
</sdf>
"""
    return sdf

for kind in ("A", "B"):
    filename = Path(f"sim_pack_{kind}.sdf")
    filename.write_text(make_sdf(kind))
    print("作成:", filename)

print("Gazeboモデル作成完了")
