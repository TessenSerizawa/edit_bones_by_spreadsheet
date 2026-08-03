ボーンの名前と表示・非表示をCSVファイルに記載した情報によって変換するアドオンです。<br/>
MikuMikuDanceやMayaのHumanIKのボーン名はBlenderの左右対称命名規則に当てはまらず、ミラー編集ができません。<br/>
そのような時、このアドオンでボーン名を一時的に左右対称な名前に変換し、作業後に元の名前に戻すという使い方を想定しています。<br/>

|Version|DL|Blender|
|---|---|---|
|0.1|https://github.com/Uiler/edit_bones_by_spreadsheet/releases/tag/v0.1|2.7.9|
|0.2|https://github.com/Uiler/edit_bones_by_spreadsheet/releases/tag/v0.2|2.81|
|0.3 (unofficial fork)|-|4.5 LTS|

## 0.3 (Blender 4.5向け非公式修正版) での変更点

- `bl_info`のBlenderバージョン要件を `4.5.0` に更新
- CSV読み込みをUTF-8(BOM有無問わず) / cp932 自動判定に変更(従来はcp932固定だったため、Windows以外やUTF-8で保存したCSVを読むと文字化け・例外になっていた)
- CSV書き出しを `utf-8-sig` に変更(BOM付きUTF-8。日本語版Excelでもそのまま開ける)
- Blender 4.0でボーンレイヤー(`bone.layers`)がボーンコレクションに置き換わったことに伴い、`common.py`内の未使用だった可視判定関数を新API対応に修正(呼び出されると例外になる状態だったのを修正)
- アドオン無効化時に `Scene.uil_edit_bones_by_spreadsheet_propgrp` を削除するよう`unregister()`を修正(再読み込み時の残留プロパティ対策)
- 正規表現リテラルを raw 文字列化し、新しいPythonでの `SyntaxWarning` を解消
- `blender_manifest.toml` を追加し、Blender 4.2以降の「拡張機能(Extension)」形式でもインストール可能に(従来通り「レガシーアドオンのインストール」でも動作します)

### インストール方法(Blender 4.5)
ZIPファイルごとBlenderの `編集 > プリファレンス > 拡張機能 (Get Extensions)` 右上のドロップダウンから「ディスクからインストール (Install from Disk)」でZIPを選択してください。

<br/>
[チュートリアル動画]https://youtu.be/61QXbOFOzBE
