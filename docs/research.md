# C48GLの配線調査とZMK標準機能への対応

調査日: 2026-11-05。実物の基板・SuperMiniに対する導通測定や動作試験は行っていません。

## 一次資料

QMK本家のGL516ディレクトリにはC48GLがなく、設計者フォークの`remap`ブランチから見つけました。

| 資料 | 固定した版・根拠 |
| --- | --- |
| [C48GL QMK](https://github.com/Salicylic-acid3/qmk_firmware/tree/384396b78dd62fa25955c58d77f3cd93040ca933/keyboards/gl516/c48gl) | `384396b78dd62fa25955c58d77f3cd93040ca933` |
| [config.h](https://github.com/Salicylic-acid3/qmk_firmware/blob/384396b78dd62fa25955c58d77f3cd93040ca933/keyboards/gl516/c48gl/config.h) | 8行6列の論理マトリクス、4行線・6列線の実配線 |
| [matrix.c](https://github.com/Salicylic-acid3/qmk_firmware/blob/384396b78dd62fa25955c58d77f3cd93040ca933/keyboards/gl516/c48gl/matrix.c) | 行をLOWにして列を読む24キー、列をLOWにして行を読む24キー |
| [info.json](https://github.com/Salicylic-acid3/qmk_firmware/blob/384396b78dd62fa25955c58d77f3cd93040ca933/keyboards/gl516/c48gl/info.json) | LAYOUTの48要素とその順序 |
| [rules.mk](https://github.com/Salicylic-acid3/qmk_firmware/blob/384396b78dd62fa25955c58d77f3cd93040ca933/keyboards/gl516/c48gl/rules.mk) | `CUSTOM_MATRIX = lite`、独自`matrix.c`を追加 |
| [公開PCB・回路図](https://github.com/Salicylic-acid3/GL516_Example/tree/a3e8a0b21a2889e085a683e8f666ea4ae58bedab/Keyboard/C48GL/2_Assemble) | `a3e8a0b21a2889e085a683e8f666ea4ae58bedab`。全48キーのパッド接続と位置を照合 |
| [設計者のVIA JSON](https://github.com/Salicylic-acid3/via-json/blob/444d72bd2f50546e2c5d42bb36a3074ed3bb0794/c48gl.json) | 左右24キー、角度付きの配置を補助確認 |
| [ZMK v0.3.0 Charlieplex仕様](https://github.com/zmkfirmware/zmk/blob/edf5c0814fd3ea202e43aad2d68fd32e882a518c/docs/docs/config/kscan.md#charlieplex-driver) | 駆動GPIOがRCのrow、入力GPIOがcolumn。割り込み線なしのポーリングに対応 |
| [ZMK標準ドライバ実装](https://github.com/zmkfirmware/zmk/blob/edf5c0814fd3ea202e43aad2d68fd32e882a518c/app/module/drivers/kscan/kscan_gpio_charlieplex.c) | `kscan_charlieplex_read()`は1本ずつ出力、他のGPIOを入力にする。ACTIVE_LOWではプルアップ |
| [nice!nanoのコネクタ定義](https://github.com/zmkfirmware/zmk/blob/edf5c0814fd3ea202e43aad2d68fd32e882a518c/app/boards/arm/nice_nano/arduino_pro_micro_pins.dtsi) | Pro Microコネクタ番号とnRF52840のGPIOの対応 |

取得した資料とSHA-256は`research/sources.json`、QMKとハードウェアの原本は`research/`に保存しています。公開PCBのU1フットプリント名は`Micon_BMP_GL`ですが、キーの10信号線はQMKのPro Micro配線と一致します。実物の基板版・ソケット実装は未確認です。

**同梱の古い`C48GL.net`は採用しません。** これは12列・全ダイオード同方向の別の配線を含んでいます。現行`.kicad_pcb`と`.sch`、QMK独自スキャナを優先しました。資料の矛盾を確認できるよう原本は残しています。

## ピン対応

QMKの`D1`などはATmega32u4のポート名です。ArduinoのD1やnRFのP0.01と同一ではありません。

| 信号 | QMK AVRピン | PCB U1パッド | Pro Micro番号 | nice!nano v2 GPIO | Charlieplex番号 |
| --- | --- | ---: | ---: | --- | ---: |
| R0 | D1 | 5 | 2 | P0.17 | 0 |
| R1 | D0 | 6 | 3 | P0.20 | 1 |
| R2 | D4 | 7 | 4 | P0.22 | 2 |
| R3 | C6 | 8 | 5 | P0.24 | 3 |
| C0 | F4 / A3 | 20 | 21 | P0.31 | 4 |
| C1 | F5 / A2 | 19 | 20 | P0.29 | 5 |
| C2 | F6 / A1 | 18 | 19 | P0.02 | 6 |
| C3 | F7 / A0 | 17 | 18 | P1.15 | 7 |
| C4 | B1 | 16 | 15 | P1.13 | 8 |
| C5 | B3 | 15 | 14 | P1.11 | 9 |

ここまでは公開ソースと標準コネクタ定義で確認しました。**手元のSuperMiniがこのnice!nano v2配列・電源構成・ブートローダーを満たすかは未確認**です。未確認のピンを仮のGPIOで埋めた箇所はありません。シールドは`&pro_micro`を使い、コネクタ変換を固定版ZMKへ委ねています。

## ダイオードと特殊マトリクス

- 左24キー: `C[c] → スイッチ → ダイオード → R[r]`。カソードは行線。物理信号線基準でCOL2ROW。
- 右24キー: `R[r] → ダイオード → スイッチ → C[c]`。カソードはスイッチ経由で列線。物理信号線基準でROW2COL。
- QMKの`MATRIX_ROWS=8`のうち、0〜3は左、4〜7は右を示す論理行。実物に8本の行線があるわけではありません。

GPIOを共有し入出力を反転する双方向方式です。単一の通常の`zmk,kscan-gpio-matrix`に`diode-direction`を1つ指定するだけでは表現できません。matrix-transformもGPIOの入出力方向そのものは切り替えません。共有線を2つの通常スキャナに割り当てる構成も、走査の排他制御を保証しないため採用しません。

一方、標準の`zmk,kscan-gpio-charlieplex`は全GPIOを順次駆動し、他を読むため、この配線を含む上位集合を走査できます。**独自Cドライバは不要**です。10×10のうち48交点だけを変換に登録し、自己交点・未使用交点はキーマップに割り当てません。

| QMK座標 | ZMKスキャナ座標 | 電気的動作 |
| --- | --- | --- |
| `(r,c)`、r=0〜3 | `RC(r,4+c)` | R[r]をLOW、C[c]を入力として読む |
| `(4+r,c)`、r=0〜3 | `RC(4+c,r)` | C[c]をLOW、R[r]を入力として読む |

GPIOはすべてACTIVE_LOW。標準ドライバの入力設定で内部プルアップが入ります。スキャン待ち5µs、押下・解放デバウンス5ms、無押下時5ms周期を初期値にしています。これらは実測していないソフトウェア調整値です。

専用`interrupt-gpios`は公開配線にないので指定しません。`wakeup-source`も指定せず、`CONFIG_ZMK_SLEEP=n`としています。無線HIDは利用できますが、電池寿命は未計測で、割り込み式キーボードと同等の低消費電力は保証できません。

## 配列と物理配置

QMKのLAYOUT順は各段につき左6・右6で、次の4段です。

```text
(0,0)..(0,5)    (4,0)..(4,5)
(1,0)..(1,5)    (5,0)..(5,5)
(2,0)..(2,5)    (6,0)..(6,5)
(3,0)..(3,5)    (7,0)..(7,5)
```

左SW番号は`1+4*c+r`、右は`25+4*c+r`です。QMKのinfo.jsonのx/yは簡略化された格子です。Studioの形状にはPCBの各SWの中心座標と角度を採用し、19.05mmを1uに換算しました。ホットスワップ配線のため180°反転したフットプリントは、表示するキー軸を±90°内へ正規化しています。

`scripts/verify_config.py`は原本ハッシュ、10本のピン対応、48個すべてのスイッチとダイオードの接続、生成済みtransform/物理配置、4レイヤー×48 bindingsを照合します。これはソース間の整合性確認で、実機試験の代わりではありません。

## 実機で残る検証

対象PCBとSuperMiniの版、ソケットの向き・導通、USB/BLE入力、リセットからの復帰、Studioとの通信、電流・電池計測は未検証です。GL516ケース内のアンテナ位置とBLE到達距離も未検証です。

双方向マトリクスでは複数押下時の間接的な導通経路にも注意が必要です。例えば左`(0,0)`・右`(5,0)`・左`(1,1)`を押すと、回路上はC1→R1→C0→R0の経路ができます。ダイオードの順方向電圧とGPIO入力閾値によっては左`(0,1)`の誤検出に繋がり得ます。標準ドライバでの配線表現とコンパイルは検証できますが、任意の多キー同時押しやNKROの保証はできません。初回試験では左右混在の3キー押下、Shift/Ctrlと文字、LOWER+RAISEを含めて確認してください。

バッテリー端子・充電電流・電源スイッチ・LED/外部電源制御はSuperMini製品ごとの差があり、未確認です。RGB・OLED・追加GPIOの設定は作成していません。nice!nanoの外部電源制御は無効化してあります。
