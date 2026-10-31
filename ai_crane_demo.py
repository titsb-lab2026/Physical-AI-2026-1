from pathlib import Path
import sys

import joblib
import rclpy
from PIL import Image
from rclpy.action import ActionClient
from rclpy.node import Node
from control_msgs.action import FollowJointTrajectory
from trajectory_msgs.msg import JointTrajectoryPoint
from action_msgs.msg import GoalStatus

from train_lib_pack_ai import preprocess


BASE = Path(__file__).resolve().parent
MODEL_FILE = BASE / "ai_models/lib_pack_rf.joblib"

JOINT_NAMES = [
    "crane_plus_joint1",
    "crane_plus_joint2",
    "crane_plus_joint3",
    "crane_plus_joint4",
]

# 動作確認済みの角度を使用
TARGETS = {
    "A": [0.0, 0.0, 0.0, 0.0],
    "B": [0.1, 0.0, 0.0, 0.0],
}


def predict_pack(image_path):
    saved = joblib.load(MODEL_FILE)
    model = saved["model"]

    with Image.open(image_path) as img:
        features = preprocess(img).reshape(1, -1)

    prediction = int(model.predict(features)[0])
    return saved["label_names"][prediction]


class CraneController(Node):
    def __init__(self):
        super().__init__("lib_pack_ai_crane_demo")
        self.client = ActionClient(
            self,
            FollowJointTrajectory,
            "/crane_plus_arm_controller/follow_joint_trajectory",
        )

    def move(self, positions):
        print("CRANE+のコントローラに接続中...", flush=True)

        if not self.client.wait_for_server(timeout_sec=15.0):
            raise RuntimeError("アームのActionサーバが見つかりません")

        goal = FollowJointTrajectory.Goal()
        goal.trajectory.joint_names = JOINT_NAMES

        point = JointTrajectoryPoint()
        point.positions = positions
        point.time_from_start.sec = 4

        goal.trajectory.points = [point]

        future = self.client.send_goal_async(goal)
        rclpy.spin_until_future_complete(self, future, timeout_sec=15.0)

        if not future.done():
            raise RuntimeError("動作指令の受付がタイムアウトしました")

        handle = future.result()

        if not handle.accepted:
            raise RuntimeError("アームが動作指令を拒否しました")

        print("動作指令が受け付けられました", flush=True)

        result_future = handle.get_result_async()
        rclpy.spin_until_future_complete(
            self, result_future, timeout_sec=60.0
        )

        if not result_future.done():
            raise RuntimeError("動作完了の確認がタイムアウトしました")

        response = result_future.result()

        if response.status != GoalStatus.STATUS_SUCCEEDED:
            raise RuntimeError("アームの動作が正常終了しませんでした")

        if response.result.error_code != 0:
            raise RuntimeError(
                f"軌道制御エラー: {response.result.error_code}"
            )

        print("CRANE+の動作成功", flush=True)


def main():
    if len(sys.argv) != 2:
        print("使用方法: python3 ai_crane_demo.py 画像ファイル")
        sys.exit(1)

    image_path = Path(sys.argv[1])

    if not image_path.is_file():
        print("画像ファイルが見つかりません:", image_path)
        sys.exit(1)

    print("================================")
    print("Physical AI 模擬LiB解体デモ")
    print("================================")
    print("入力画像:", image_path)

    kind = predict_pack(image_path)
    print("AI判定:", kind, "型")

    if kind not in TARGETS:
        print("対象外パック：アームの動作を禁止")
        return

    print(kind, "型用の模擬作業位置を選択")
    print("関節目標角度:", TARGETS[kind])

    rclpy.init()
    controller = CraneController()

    try:
        controller.move(TARGETS[kind])
    finally:
        controller.destroy_node()
        rclpy.shutdown()

    print("デモ終了")


if __name__ == "__main__":
    main()
