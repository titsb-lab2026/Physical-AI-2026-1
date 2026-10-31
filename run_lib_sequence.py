import sys
from pathlib import Path

import rclpy

from ai_crane_demo import predict_pack, CraneController

BASE = Path(__file__).resolve().parent

VERTICAL = [0.0, 0.0, 0.0, 0.0]
HOME = [0.0, -1.16, -2.01, -0.73]

# 型式別の模擬作業位置（関節1の角度、単位rad）
# 実際の締結部座標ではない
WORK_ANGLES = {
    "A": [0.00, 0.03, 0.07, 0.10],
    "B": [0.10, 0.05, 0.00],
}


def main():
    if len(sys.argv) != 2:
        print("使用方法: python3 run_lib_sequence.py images/pack_A.png")
        sys.exit(1)

    image_path = Path(sys.argv[1])

    if not image_path.is_file():
        print("画像が見つかりません:", image_path)
        sys.exit(1)

    print("================================")
    print("Physical AI 模擬LiB解体システム")
    print("================================")

    kind = predict_pack(image_path)

    print("入力画像:", image_path)
    print("AI判定:", kind, "型", flush=True)

    if kind not in WORK_ANGLES:
        print("対象外：ロボット動作禁止", flush=True)
        return

    angles = WORK_ANGLES[kind]
    print(f"作業指示：{kind}型、模擬作業{len(angles)}回")

    rclpy.init()
    controller = CraneController()

    try:
        print("初期姿勢へ移動", flush=True)
        controller.move(VERTICAL)

        for i, angle in enumerate(angles, 1):
            print(
                f"模擬作業 {i}/{len(angles)}："
                f"作業姿勢へ移動",
                flush=True
            )

            target = [
                angle,
                HOME[1],
                HOME[2],
                HOME[3],
            ]
            controller.move(target)

            print("作業姿勢から退避", flush=True)
            controller.move(VERTICAL)

        print("初期姿勢へ復帰", flush=True)
        controller.move(HOME)

        print("================================")
        print(f"{kind}型：模擬作業シーケンス完了")
        print("================================")

    finally:
        controller.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
