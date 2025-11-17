# ESP32-Wi-Fi-firmware-update
# 用途・目的
これらのファイルは，ESP32のファームウェアアップデートをWiFiを使用してプル方式で行うMicropythonのプログラムである．ESP32にboot.pyとota.pyを実装する．処理の流れとして，ESP32が起動したときにHTTPを使用してサーバーのOTAディレクトリにあるファームウェアをダウンロードする．受信したデータは未使用のパーテーションに直接書き込みを行う．ダウンロードが終了した後に，次回起動時に使用するパーテーションを今回書き込んだパーテーションに設定して再起動を行う．

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
/
├─ boot.py
└─ ota.py
```
◯サーバー
- OS：ubuntu-24.04/LTS
- 実行環境：Python 3.12.3

ファイル構成
```
/home/c0a2201673/
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
c0a2201673@c0a22016-sotuken:~$ python3 -m http.server 8000
```
- ファイルを `OTA/` に配置するか，`FW_URL` を実ファイルに合わせて変更（80/443 以外のポートは URL に明記）．

# 実行結果
## ESP32
以下の画像は、ESP32 の実行時ログ出力である。reset machine の出力を境に、上部がアップデート適用前、下部が適用後の状態を示している。
ログ中の [BOOT] running= に続く値は、現在使用しているパーティションのラベル名を示し、fw= に続く値は、現在動作しているファームウェアのバージョンを表している。
適用前のログでは、[BOOT] running= ota_0 fw= v1.26.0 on 2025-08-09 となっており、ota_0 パーティションを使用し、v1.26.0 on 2025-08-09 のファームウェアが動作していることが確認できる。
一方、適用後のログでは、[BOOT] running= ota_1 fw= v1.26.1 on 2025-09-11 と表示され、適用後は ota_1 パーティションを使用し、v1.26.1 on 2025-09-11 のファームウェアが正常に起動していることが確認できる。
また、最後には Ctrl + C によりプログラムを終了しており，その後の出力で MicroPython v1.26.1 on 2025-09-11; Generic ESP32 module with OTA with ESP32 の表示から、アップデート後の Micropython ファームウェアがシステム上で正しく動作していることが明確である。

<img width="694" height="737" alt="image" src="https://github.com/user-attachments/assets/bdfd69a4-2df1-4f5a-8948-cd4cb34b150f" />


## サーバー
次の画像はサーバーでコマンドを実行してESP32を動作させた際の出力結果の画像である．出力を見るとESP32がHTTPを使用してOTAディレクトリにあるESP32_GENERIC-OTA-20250911-v1.26.1.app-binをGETしている事が分かる．

<img width="1029" height="93" alt="image" src="https://github.com/user-attachments/assets/0e253e8e-a645-4dbe-8d30-1f4d6d80860a" />


