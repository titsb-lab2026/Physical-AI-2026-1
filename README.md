# Physical AIによる異種LiBパックの認識と模擬解体ロボット制御

## 1. 目的

形状や構造が異なるリチウムイオン電池（LiB）パックを
画像AIで分類し、その結果に応じてロボットアームの
模擬作業シーケンスを切り替える仕組みを検証する。

実物のLiBは使用せず、合成画像とGazeboシミュレーションを使用する。

## 2. システム構成

- ROS 2 Humble
- Gazebo Sim
- CRANE+ ロボットアーム
- Python
- Random Forest（scikit-learn）
- FollowJointTrajectory（ROS 2 Action）

処理の流れ：

合成PNG画像
→ 画像前処理
→ Random Forestによる型式分類
→ 型式別の作業シーケンス選択
→ ROS 2によるアーム制御

## 3. AIによる型式分類

- A型：模擬締結部4か所
- B型：模擬締結部3か所
- C型：学習済みの対象外クラス

生成した合成画像でRandom Forestを学習した。
同じ画像生成方式によるテストデータ240枚で、
240枚すべてを正しく分類した。

これは合成データ上の結果であり、
実物LiBパックでの認識性能を保証するものではない。

## 4. ロボット動作

- A型：4回の模擬作業動作
- B型：3回の模擬作業動作
- C型：動作指令を送らず終了

あらかじめ設定した関節角度による模擬動作であり、
実際のねじ位置への接近やねじの取り外しではない。

## 5. 主なファイル

- generate_lib_packs.py：学習用合成画像の生成
- train_lib_pack_ai.py：Random Forestの学習・評価
- ai_crane_demo.py：画像分類とROS 2制御
- run_lib_sequence.py：型式別の模擬作業シーケンス
- create_sim_packs.py：Gazebo用模擬モデルの生成
- sim_pack_A.sdf：A型の模擬モデル
- sim_pack_B.sdf：B型の模擬モデル
- images/：画像
- ai_models/：学習済みモデル

## 6. 実行方法

ROS 2、CRANE+関連パッケージ、Python依存ライブラリを
導入した環境で実行する。

### Gazebo起動

ros2 launch crane_plus_gazebo crane_plus_with_table.launch.py

### 模擬パックをGazeboへ追加

ros2 run ros_gz_sim create -world default -file sim_pack_A.sdf -name lib_pack_A -x 0.34 -y 0.14 -z 1.015

ros2 run ros_gz_sim create -world default -file sim_pack_B.sdf -name lib_pack_B -x 0.34 -y -0.14 -z 1.015

### AI分類と模擬動作

python3 run_lib_sequence.py images/pack_A.png

python3 run_lib_sequence.py images/pack_B.png

python3 run_lib_sequence.py images/pack_C.png

## 7. AI分類の確認

画像の内容は変えず、ファイル名のAとBを入れ替える試験を実施した。

- A型画像をpack_B_test.pngとして入力 → A型と判定
- B型画像をpack_A_test.pngとして入力 → B型と判定

ファイル名ではなく画像内容に基づく分類であることを確認した。

## 8. 制約・今後の課題

- AIへの入力は事前作成したPNG画像
- Gazeboカメラからのリアルタイム認識は未実装
- 模擬パックの位置推定は未実装
- 締結部へのアーム先端位置合わせは未実装
- 実際のねじ取り外し機構は未実装
- 実物LiBでの認識・動作評価は未実施
- C型は学習済みクラスであり、一般的な未知物体検出ではない
