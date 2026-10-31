from pathlib import Path
import random

import joblib
import numpy as np
from PIL import Image
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

from generate_lib_packs import make_pack

LABELS = {"A": 0, "B": 1, "C": 2}
LABEL_NAMES = {0: "A", 1: "B", 2: "C"}
IMG_SIZE = (80, 60)   # 横, 縦


def augment_image(img, seed):
    r = random.Random(seed)

    # 小さな回転
    angle = r.uniform(-8.0, 8.0)
    img = img.rotate(angle, fillcolor=(230, 234, 238))

    # 明るさゆらぎ
    arr = np.array(img).astype(np.int16)
    shift = r.randint(-10, 10)
    arr = np.clip(arr + shift, 0, 255).astype(np.uint8)

    # 微小ノイズ
    noise = np.random.default_rng(seed).integers(-6, 7, size=arr.shape, endpoint=False)
    arr = np.clip(arr.astype(np.int16) + noise, 0, 255).astype(np.uint8)

    return Image.fromarray(arr)


def preprocess(img):
    img = img.convert("L")              # グレースケール
    img = img.resize(IMG_SIZE)          # 小さくして特徴量化
    arr = np.array(img, dtype=np.float32) / 255.0
    return arr.flatten()


def build_dataset(n_per_class, base_seed):
    X = []
    y = []

    for kind, label in LABELS.items():
        for i in range(n_per_class):
            seed = base_seed + label * 10000 + i
            img = make_pack(kind, seed=seed)
            img = augment_image(img, seed=seed + 999)
            feat = preprocess(img)

            X.append(feat)
            y.append(label)

    return np.array(X), np.array(y)


def main():
    Path("ai_models").mkdir(exist_ok=True)

    print("学習データを作成します")
    X_train, y_train = build_dataset(n_per_class=300, base_seed=1000)
    X_test, y_test = build_dataset(n_per_class=80, base_seed=50000)

    print(f"学習データ数: {len(X_train)}")
    print(f"評価データ数: {len(X_test)}")

    model = RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        max_depth=None,
        n_jobs=-1
    )

    print("AI学習を開始します")
    model.fit(X_train, y_train)
    print("AI学習が完了しました")

    y_pred = model.predict(X_test)

    acc = accuracy_score(y_test, y_pred)
    print(f"評価データ正解率: {acc:.3f}")
    print("混同行列:")
    print(confusion_matrix(y_test, y_pred))
    print("分類レポート:")
    print(classification_report(y_test, y_pred, target_names=["A", "B", "C"]))

    model_path = "ai_models/lib_pack_rf.joblib"
    joblib.dump(
        {
            "model": model,
            "img_size": IMG_SIZE,
            "label_names": LABEL_NAMES
        },
        model_path
    )
    print(f"モデル保存先: {model_path}")

    # 代表画像で推論確認
    for kind in ("A", "B", "C"):
        img = Image.open(f"images/pack_{kind}.png")
        feat = preprocess(img).reshape(1, -1)
        pred = model.predict(feat)[0]
        print(f"pack_{kind}.png -> AI判定: {LABEL_NAMES[pred]}")


if __name__ == "__main__":
    main()
