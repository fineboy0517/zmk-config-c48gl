# C48GL / SuperMini nRF52840用ZMK

[![Build C48GL UF2](https://github.com/fineboy0517/zmk-config-c48gl/actions/workflows/build.yml/badge.svg)](https://github.com/fineboy0517/zmk-config-c48gl/actions/workflows/build.yml)

公開リポジトリ: [fineboy0517/zmk-config-c48gl](https://github.com/fineboy0517/zmk-config-c48gl)

GL516ケース用C48GLを、nice!nano v2互換のSuperMini nRF52840で使うための単体48キー設定です。USB HID・Bluetooth LEに対応し、通常版とZMK Studio有効版を用意しました。

**両方のUF2をローカルでビルド済みです。実機には書き込んでいません。** [GitHub Actionsでも両UF2の生成・検査に成功しました](https://github.com/fineboy0517/zmk-config-c48gl/actions/runs/41897929720)。対象PCB・SuperMiniでのUSB/BLE動作、電源と導通は未検証です。ピン配線は公開QMKとPCBで照合しましたが、手元のSuperMiniの互換性は実物で確認してください。

- [配線調査・ピン対応・標準ドライバの検討](docs/research.md)
- [ビルド検証結果](docs/build-validation.md)
- 設定本体: `boards/shields/c48gl/`、`config/c48gl.keymap`、`config/c48gl.conf`
- 生成済みUF2: `firmware/c48gl-nice_nano_v2.uf2`、`firmware/c48gl-nice_nano_v2-studio.uf2`

## 特殊マトリクスへの対応

C48GLは4本の行線と6本の列線で48キーを読む双方向マトリクスです。左側と右側でダイオード方向が逆で、QMKは独自の`matrix.c`でGPIOの入出力を切り替えています。

ZMKでは標準の`zmk,kscan-gpio-charlieplex`と10×10→48キーのmatrix-transformで表現しました。独自ドライバは追加していません。左右の切り替え、全48キーの接続は公開PCBと照合済みです。配線・変換の根拠は[調査記録](docs/research.md)を参照してください。

専用割り込み線がないためポーリングを使います。キーでの復帰経路が未確認の深いスリープは無効です。待機消費電流・電池寿命・左右混在の多キー同時押しは実機で検証する必要があります。

## GitHub Actionsでビルド

[成功したビルドとUF2ダウンロード](https://github.com/fineboy0517/zmk-config-c48gl/actions/runs/41897929720)のArtifactsから`firmware`を取得できます。中に通常版とStudio版の2つのUF2が入っています。このリポジトリは配置済みなので、キーマップを変更する場合は`config/c48gl.keymap`を編集してpushしてください。

1. このフォルダの内容を自分のGitHubリポジトリへ追加します。`.github/`、`boards/`、`config/`、`zephyr/`、`research/`、`scripts/`、`build.yaml`を含めてください。`.build/`はビルド用作業領域なので追加しません。
2. pushすると`Build C48GL UF2`が起動します。Actionsの画面から`Run workflow`でも起動できます。
3. `validate`、通常版・Studio版のビルド、`verify-uf2`が成功したことを確認します。
4. Actionsの実行結果のArtifactsから`firmware`をダウンロードしてZIPを展開します。

| UF2 | 用途 |
| --- | --- |
| `c48gl-nice_nano_v2.uf2` | USB HID + BLE HID |
| `c48gl-nice_nano_v2-studio.uf2` | 上記 + Studio、USB CDC通信 |

シールド名は`c48gl`、ボード名は**`nice_nano_v2`**です。ZMK v0.3.0のコミットと依存ソースのSHAを`config/west.yml`に固定しています。この版に現行main用の`nice_nano//zmk`という名前を混在させないでください。

Actionsは同じ固定コミットのZMK公式再利用ワークフローを呼び出します。公式ワークフローのビルドコンテナは`zmkfirmware/zmk-build-arm:stable`なので、ツール環境まで不変に固定したものではありません。エラー時はActionsのログと`docs/build-validation.md`のローカル検証環境を比較してください。

## 初期キーマップと日本語入力

ローマ字入力用QWERTYです。**OSのハードウェアキーボード配列は日本語/JISを前提**とし、記号もJISのHID位置に合わせています。US配列として認識させると記号が一致しません。ファームウェアそのものはIMEではなく、変換キーなどをOSへ送ります。

次は論理上の4段×12キー表示です。実際には左右に傾きと段差があり、親指キーもずれています。

```text
Tab   Q    W    E     R       T      | Y      U       I      O     P     Bksp
Esc   A    S    D     F       G      | H      J       K      L     ;     Enter
Shift Z    X    C     V       B      | N      M       ,      .     ↑     /
Ctrl  GUI  Alt  LOWER 無変換  Space  | Space  変換    RAISE  ←     ↓     →
```

| 操作 | 内容 |
| --- | --- |
| `LOWER`を押しながら | 最上段がEsc・1〜0・Delete。@、角括弧、コロン、矢印・Home/End・PageUp/Downなど |
| `RAISE`を押しながら | F1〜F12、JIS用記号。括弧、引用符、波括弧、アンダースコア、バックスラッシュなど |
| `LOWER + RAISE`を押しながら | 接続・Studio操作用のADJUSTレイヤー |
| 無変換・変換 | `INT_MUHENKAN`・`INT_HENKAN`。WindowsではIME設定で「無変換=IMEオフ」「変換=IMEオン」にすると便利です |
| `LOWER + 無変換 / 変換` | `LANG2 / LANG1`。macOSなどの英数・かな切り替え用。OS側の入力ソース設定に依存します |
| `RAISE + 無変換 / 変換` | かなキー / 全角半角LANGキー。OSでの解釈は要確認 |

JISの¥キーと「ろ」位置のキーはLOWERにあります。表示が¥かバックスラッシュになるかはOS・アプリ・フォントに依存します。

ADJUSTでのキー位置は、通常配列のキー名を目印にすると次のとおりです。

| 通常時の位置 | ADJUST時の動作 |
| --- | --- |
| Q / W / E / R / T | BLEプロファイル1 / 2 / 3 / 4 / 5を選択（内部番号0〜4） |
| A | USBを優先出力に選択 |
| S | Bluetoothを優先出力に選択 |
| Backspace | 選択中プロファイルのペアリング情報を削除 |
| 左Space（最下段左ブロックの右端） | Studioのロック解除。通常版では何もしません |
| 左Shift | Caps Lock |

Bluetoothで使うときはプロファイルを選び、PC/スマートフォンのBluetooth画面で`C48GL`をペアリングします。USB接続中でもBLEを優先させたい場合はADJUSTのS、USBへ戻す場合はAを使います。入力は選択された接続先へ送られ、USBとBLEへ同時送信する設定ではありません。

ペアリングし直す場合は、対象プロファイルを選択してからADJUST+Backspaceを操作し、OS側の古い登録も削除します。他のプロファイルは消去しません。

キーマップ編集は`config/c48gl.keymap`、JIS記号定義は`config/c48gl-jis.h`です。変更後は再ビルドしてください。

## ZMK Studio

Studio有効版は48キーの`physical-layout`と`keys`、USB通信用`studio-rpc-usb-uart`、`CONFIG_ZMK_STUDIO=y`を含みます。選択は`zmk,physical-layout`で行い、旧式のchosen `zmk,matrix-transform`は指定していません。

1. 対象実機を確認してからStudio版UF2を書き込みます。
2. USBデータケーブルで接続し、[ZMK Studio](https://zmk.studio/)を開きます。対応ブラウザまたはStudioアプリの接続方法は[公式案内](https://zmk.dev/docs/features/studio)に従ってください。
3. C48GLを選び、LOWER+RAISE+左Spaceでロックを解除します。
4. 配列を変更し、Studio側で保存します。

既存の4レイヤーのキー割り当てを変更できます。StudioでGPIO配線やスキャナ方式を修正することはできません。Studio版はビルド確認済みで、実際のStudioクライアントとの接続・保存は未検証です。ロック機能は有効なままです。

Studioの保存内容は不揮発メモリに残り、UF2を更新しても新しい`.keymap`より保存内容が優先される場合があります。初期配列に戻すときはStudio側のリセット手順を確認してください。設定全消去はBLEペアリングも失わせ得るため、この構成では自動実行しません。

## ローカルビルド

[ZMK v0.3.0](https://github.com/zmkfirmware/zmk/tree/v0.3.0)に対応したZephyr環境とARM用Zephyr SDKが必要です。今回の検証ではmacOS arm64、Zephyr SDK 0.16.8を使いました。以下は別の開発フォルダを使う例です。

```sh
# Python仮想環境を作成し、以降は有効にした状態で実行
python3 -m venv "$HOME/zmk-c48gl-venv"
. "$HOME/zmk-c48gl-venv/bin/activate"

# このリポジトリの場所。別の場所へ置いた場合は変更
export C48GL_CONFIG=/Users/motomura/Documents/C48GL
pip install -r "$C48GL_CONFIG/requirements-build.txt"

mkdir -p "$HOME/zmk-c48gl-work"
cd "$HOME/zmk-c48gl-work"
git clone --depth 1 --branch v0.3.0 https://github.com/zmkfirmware/zmk.git zmk
cd zmk
west init -l app
west update
pip install -r zephyr/scripts/requirements-base.txt
# 古いnanopbがpkg_resourcesを要求するため依存を揃える
pip install -r "$C48GL_CONFIG/requirements-build.txt"

# ARMツールチェーンを展開したSDKの実際の場所に変更
export ZEPHYR_TOOLCHAIN_VARIANT=zephyr
export ZEPHYR_SDK_INSTALL_DIR="$HOME/zephyr-sdk-0.16.8"

python "$C48GL_CONFIG/scripts/verify_config.py"
west build -s app -d ../build-standard -b nice_nano_v2 -- \
  -DSHIELD=c48gl \
  -DZMK_CONFIG="$C48GL_CONFIG/config" \
  -DZMK_EXTRA_MODULES="$C48GL_CONFIG"

west build -s app -d ../build-studio -b nice_nano_v2 \
  -S studio-rpc-usb-uart -- \
  -DSHIELD=c48gl \
  -DZMK_CONFIG="$C48GL_CONFIG/config" \
  -DZMK_EXTRA_MODULES="$C48GL_CONFIG" \
  -DCONFIG_ZMK_STUDIO=y

python "$C48GL_CONFIG/scripts/verify_uf2.py" \
  ../build-standard/zephyr/zmk.uf2 ../build-studio/zephyr/zmk.uf2
```

出力はそれぞれ`build-standard/zephyr/zmk.uf2`、`build-studio/zephyr/zmk.uf2`です。ボード・snippet・重要な構成を変えた場合は`west build -p always ...`でクリーンビルドしてください。

上のローカル例はZMK付属manifestから依存を取得します。Actionsと同じ依存SHAまで揃えるには、[検証記録](docs/build-validation.md)の固定manifestを使う手順を利用してください。macOSでは`/tmp`と`/private/tmp`の別名が混在するとStudioのprotobuf生成先がずれる場合があります。ホーム配下など、別名を含まない開発パスを推奨します。

## 書き込み方法（今回は実行していません）

**ビルド成功と実物の配線・互換性を確認してから**行います。元のPro Micro/ATmega32u4向けQMK HEXとは形式も対象MCUも異なります。

1. 手元のPCBで表の10信号線、GND/VCC、RESET、ソケットの向きを導通確認します。SuperMiniの実際のピン配置とブートローダーを確認します。電池を使う場合は極性・充電仕様も先に確認します。
2. USBデータケーブルで接続し、SuperMiniのRESETとGNDを素早く2回短絡するか、対応するリセットスイッチを2回押してUF2ブートローダーへ入ります。ボードによって操作・ドライブ名は異なります。
3. 現れたUF2ドライブの`INFO_UF2.TXT`を読み、nRF52840用でnice!nano v2互換のアプリ配置を扱えるブートローダーであることを確認します。不明なら書き込みを止めます。
4. 成功したビルドの通常版かStudio版の**どちらか1つ**のUF2を、そのドライブにコピーします。通常はドライブが消えてキーボードが再起動します。
5. 最初はUSBで48キーを1個ずつ確認し、左右混在の同時押し・LOWER/RAISEを確認してからBLEとStudioを試します。

UF2ドライブが出ない場合に、別機種のブートローダーやQMK HEXを代わりに書かないでください。このプロジェクトには自動flash処理、ブートローダー更新、設定全消去は含めていません。

## ライセンス

追加設定・スクリプトはGPL-2.0-or-laterで提供します。保存したQMKソースは各ファイルの著作権・ライセンス表記に従います。公開ハードウェア資料とVIA JSONは出典を保持した参照資料で、再配布・改変時はそれぞれの公開元の条件を確認してください。ZMK本体と生成ファームウェアに含まれる依存コードのライセンスは各上流に従います。
