# ビルド検証記録

検証日: 2026-11-05（日本時間）。生成物は`firmware/`に保存しています。実機への書き込みは行っていません。

## 検証した構成

| 項目 | 値 |
| --- | --- |
| ホスト | macOS arm64 |
| ZMK | v0.3.0 / `edf5c0814fd3ea202e43aad2d68fd32e882a518c` |
| Zephyr | 3.5.0 / `dacab4875df72109b96cc8977547a0dc04875bcd` |
| SDK | Zephyr SDK 0.16.8、macOS aarch64、arm-zephyr-eabi |
| Python | 3.9.6 |
| West / CMake / Ninja | 1.5.0 / 3.31.10 / 1.13.2 |
| ボード / シールド | `nice_nano_v2` / `c48gl` |
| Studio追加指定 | `-S studio-rpc-usb-uart`、`-DCONFIG_ZMK_STUDIO=y` |

ビルドに使用した39プロジェクトのHEADと`config/west.yml`の固定SHAが全て一致することを確認しました。`firmware/west-frozen.yml`はネイティブ検証環境のactive-only manifestの記録です。CI用`config/west.yml`はZMK本体も含めて固定してあり、移動するブランチのimportを含みません。

Pythonパッケージの実際の一覧は`firmware/python-requirements-verified.txt`です。この一覧にはローカル環境構築時に導入されたビルド不要のパッケージも含まれるため、導入手順には`requirements-build.txt`とZephyrの`requirements-base.txt`を使ってください。

## 結果

| 構成 | 結果 | FLASH使用 | RAM使用 | UF2サイズ |
| --- | --- | ---: | ---: | ---: |
| 通常版 | コンパイル・リンク・UF2生成成功 | 178,816 B / 792 KiB | 41,264 B / 256 KiB | 357,888 B |
| Studio有効版 | コンパイル・リンク・UF2生成成功 | 205,120 B / 792 KiB | 58,806 B / 256 KiB | 410,624 B |

通常版SHA-256:

```text
c9c45e80767f27c9be680ab643fd7964fe7cb13ddaa23d683bc14caaf15381ba
```

Studio有効版SHA-256:

```text
cfbf9c11b6e84b9fff3d33f5cea546949e8a0d129578675c21118bc26d03a005
```

各構成の最終ビルドログ、Kconfig結果、生成Devicetreeは`firmware/standard/`と`firmware/studio/`に保存しました。Zephyrのビルド情報などの差により、別環境で再ビルドしたUF2のハッシュやサイズは変わる場合があります。

## 完了した検査

- `scripts/verify_config.py`: 原本ハッシュ、QMK→コネクタ10本、PCBの48スイッチ・ダイオード、transform、Studio形状、4×48 bindingsが一致。
- 両ビルドの生成`edt.pickle`を解析し、実際のnRF GPIOがR0〜R3=P0.17/P0.20/P0.22/P0.24、C0〜C5=P0.31/P0.29/P0.02/P1.15/P1.13/P1.11に解決され、すべてACTIVE_LOWになることを確認。
- chosenのkscanがCharlieplex、physical-layoutが48キー、transformが48交点であることを確認。旧式のchosen matrix-transformなし。
- 両構成でUSB・BLE・Charlieplexスキャナが有効。Studio構成でStudio・ロック・USB CDCが有効。
- `scripts/verify_uf2.py`: 全ブロックのマジック、連番、nRF52840 family ID `0xADA52840`、アドレス重複なし、開始アドレス`0x26000`、全書き込みが`0x26000`〜`0xEBFFF`のアプリ領域内であることを確認。
- 固定manifestを別の一時ワークスペースで`west init -l config`・`west manifest --validate`して成功。
- Workflow、build matrix、module YAMLの構文を確認。

ネイティブ環境にはDTC実行ファイルがなく、ZephyrのPython Devicetree処理と上記の生成結果照合で検証しています。上流ボード定義の`NRF_STORE_REBOOT_TYPE_GPREGRET`非推奨警告、Studioのnanopbによる`pkg_resources`非推奨警告は残ります。コンパイル・リンクエラーはありません。

## Actionsと同じ固定ソースでローカルビルドする方法

READMEのSDK・venv準備後、元の設定とは別の空の作業フォルダへconfigをコピーします。シールドの`zephyr/module.yml`と依存Zephyrのディレクトリが衝突するため、元の設定フォルダ内で`west init`しないでください。

```sh
export C48GL_CONFIG=/Users/motomura/Documents/C48GL
mkdir -p "$HOME/zmk-c48gl-frozen-work"
cp -R "$C48GL_CONFIG/config" "$HOME/zmk-c48gl-frozen-work/config"
cd "$HOME/zmk-c48gl-frozen-work"
west init -l config
west update
pip install -r zephyr/scripts/requirements-base.txt
pip install -r "$C48GL_CONFIG/requirements-build.txt"

west build -s zmk/app -d build-standard -b nice_nano_v2 -- \
  -DSHIELD=c48gl -DZMK_CONFIG="$C48GL_CONFIG/config" \
  -DZMK_EXTRA_MODULES="$C48GL_CONFIG"

west build -s zmk/app -d build-studio -b nice_nano_v2 \
  -S studio-rpc-usb-uart -- \
  -DSHIELD=c48gl -DZMK_CONFIG="$C48GL_CONFIG/config" \
  -DZMK_EXTRA_MODULES="$C48GL_CONFIG" -DCONFIG_ZMK_STUDIO=y
```

Studioの古いnanopbは`pkg_resources`を要求するためSetuptools 80.9.0を固定しています。macOSの`/tmp`と`/private/tmp`を混在させるとprotobufの相対パスが一致しない場合があるため、ソースはホーム配下など同一表記の実パスに置いてください。上流ソースへの修正は行っていません。

## GitHub Actionsでの検証

[公開リポジトリ](https://github.com/fineboy0517/zmk-config-c48gl)へ配置し、[Actions実行 #1](https://github.com/fineboy0517/zmk-config-c48gl/actions/runs/41897929720)が成功しました（2026-11-05 日本時間）。対象コミットは`f1a78fae095d84c668dd464c4e9929c73f579409`です。

`validate`、通常版ビルド、Studio版ビルド、成果物の統合、`verify-uf2`の全ジョブが成功しました。両UF2は上記ローカル版とサイズ・SHA-256が一致しています。

成果物は実行ページのArtifactsにある`firmware`（artifact ID: `13356078376`）です。ZIPには`c48gl-nice_nano_v2.uf2`と`c48gl-nice_nano_v2-studio.uf2`が入ります。ZIPのSHA-256は`0353edfd1e7b252559bbd6a0526bb86a384dc2a22c95e66b027887b40d159ef2`です。

GitHub上の44ファイルのGit blob hashも、初回配置時のローカルファイルと全て一致することを確認しました。その後の文書・検証記録のみの更新には`[skip ci]`を付け、ビルド済み設定に変更を加えていません。

## 実機で未実施の検証

実物でのピン互換性、起動、48キー入力、同時押し、USB HID通信、BLEペアリング、Studio通信・保存、電源・バッテリー・無線性能は未検証です。ビルド成功はこれらの動作確認を意味しません。確認項目とピン対応は`docs/research.md`、将来の書き込み手順はREADMEを参照してください。
