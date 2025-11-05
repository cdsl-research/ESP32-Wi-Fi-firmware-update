# ESP32-Wi-Fi-firmware-update
# 用途・目的
これらのファイルは，ESP32のファームウェアアップデートをWiFiを使用して行うMicropythonのプログラムである．ESP32にboot.pyとota.pyを実装する．処理の流れとして，ESP32が起動したときにHTTPを使用してサーバーのOTAディレクトリにあるファームウェアをダウンロードする．受信したデータは未使用のパーテーションに直接書き込みを行う．ダウンロードが終了した後に，次回起動時に使用するパーテーションを今回書き込んだパーテーションに設定して再起動を行う．

# 環境
ESP32とHTTPサーバーを使用する．ESP32にはOTAサポート版のファームウェアを入れておく．サーバーにはOTAディレクトリを作成し，その中にアップデートに使用するファームウェアファイルを設置する．このファームウェアはOTAサポート版の識別子が.app-binのものである必要がある．

実行例で使用したESP32とサーバーの環境は以下の通りである．

◯ESP32
- ファームウェア(アップデート前)：v1.26.0 (2025-08-09)
- ファームウェア(アップデート後)：v1.26.1 (2025-09-11)
- 使用したPythonモジュール
  - time
  - network
  - urequests
  - uhashlib
  - esp32
  - machine
  - esp
  - uos 

ファイル構成
```
root/
    ├─ boot.py
    └─ ota.py
```
◯サーバー
- OS：ubuntu-24.04/LTS
- 実行環境：Python 3.12.3

ファイル構成
```
user/
    └─ OTA/ 
        └─ ESP32_GENERIC-OTA-20250911-v1.26.1.app-bin ⇒ ファームウェア
```
# プログラムとコマンド
## boot.py
- `Partition.mark_app_valid_cancel_rollback()` で起動中イメージを有効化
- 実行パーティション名や FW バージョン，MAC を表示

## ota.py
- `WIFI_SSID` / `WIFI_PASS` と `FW_URL` を任意の値に設定．
- HTTP からチャンク単位でダウンロードし，`esp32.Partition.get_next_update()` で得た未使用パーテーションにブロック整列で書き込み．
- 末尾をパディングして確定，次回起動パーティションを指定して再起動．

## HTTPサーバーの起動コマンド
- 任意の静的 HTTP サーバで配信可能．既定例はポート 8000
- 簡易サーバ例（`OTA/` ディレクトリを含むカレントで）
```
python3 -m http.server 8000
```
- ファイルを `OTA/` に配置するか，`FW_URL` を実ファイルに合わせて変更（80/443 以外のポートは URL に明記）．

# 実行結果
## ESP32
次の画像は，ESP32のコンソールに出力された実行結果の画像である．`reset machine`の出力を堺に上部がアップデートの適用前，下部がアップデートの適用後である．適用前では`ota_0`のパーテーションを使用しており，ファームウェアは`v1.26.0 on 2025-08-09`を使用していることがわかる．適用後では適用後では`ota_1`のパーテーションに変わっており，ファームウェアも`v1.26.1 on 2025-09-11`に変わっていることがわかる．これにより，ファームウェアアップデートが正常に行えたことがわかる．

<img width="471" height="718" alt="image" src="https://github.com/user-attachments/assets/08279f4a-371f-4bea-aaf4-b4b8cd9c61da" />

## サーバー
次の画像はサーバーでコマンドを実行してESP32を動作させた際の出力結果の画像である．出力を見るとESP32がHTTPを使用してOTAディレクトリにあるESP32_GENERIC-OTA-20250911-v1.26.1.app-binをGETしている事が分かる．

<img width="1029" height="93" alt="image" src="https://github.com/user-attachments/assets/0e253e8e-a645-4dbe-8d30-1f4d6d80860a" />


