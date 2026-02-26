# get-wandb-data

Weights & Biases の複数の run からログデータを取得し、`pandas.DataFrame` として返すライブラリです。
スカラー値だけでなく、画像・動画・音声などのメディアファイルのダウンロードにも対応しています。

## インストール

```bash
pip install git+https://github.com/oakwood-fujiken/get-wandb-data.git
```

ローカルで開発する場合:

```bash
git clone https://github.com/oakwood-fujiken/get-wandb-data.git
cd get-wandb-data
pip install -e .
```

## 事前準備

W&B の API キーが必要です。未設定の場合は以下のいずれかで設定してください。

```bash
# 方法1: wandb login コマンド
wandb login

# 方法2: 環境変数
export WANDB_API_KEY="your-api-key"
```

## 使い方

### スカラー値の取得

```python
from get_wandb_data import get_wandb_data

df = get_wandb_data(
    run_ids=["run_id_1", "run_id_2", "run_id_3"],
    keys=["loss", "accuracy"],
    entity="your-entity",   # W&B のユーザー名またはチーム名
    project="your-project", # W&B のプロジェクト名
)

print(df)
```

#### 出力例

| run_id | run_name   | tags             | _step | loss | accuracy |
| ------ | ---------- | ---------------- | ----- | ---- | -------- |
| abc123 | cool-run-1 | [v1, baseline]   | 0     | 0.95 | 0.10     |
| abc123 | cool-run-1 | [v1, baseline]   | 1     | 0.80 | 0.35     |
| def456 | cool-run-2 | [v2, experiment] | 0     | 0.90 | 0.12     |
| def456 | cool-run-2 | [v2, experiment] | 1     | 0.70 | 0.45     |

### メディアファイル（画像・動画・音声など）の取得

`wandb.Image`, `wandb.Video`, `wandb.Audio` などでログされたデータを取得するには、`download_media=True` を指定します。

```python
df = get_wandb_data(
    run_ids=["run_id_1", "run_id_2"],
    keys=["loss", "generated_image", "sample_audio"],
    entity="your-entity",
    project="your-project",
    download_media=True,           # メディアファイルをダウンロード
    media_dir="./my_media_files",  # 保存先ディレクトリ（省略時: ./wandb_media）
)

print(df)
```

#### 出力例

| run_id | run_name   | tags       | _step | loss | generated_image                                       | sample_audio                                      |
| ------ | ---------- | ---------- | ----- | ---- | ----------------------------------------------------- | ------------------------------------------------- |
| abc123 | cool-run-1 | [v1]       | 0     | 0.95 | my_media_files/abc123/media/images/generated_0.png    | my_media_files/abc123/media/audio/sample_0.wav    |
| abc123 | cool-run-1 | [v1]       | 1     | 0.80 | my_media_files/abc123/media/images/generated_1.png    | my_media_files/abc123/media/audio/sample_1.wav    |

メディアカラムのセルは、ファイルのローカルパス（文字列）に置き換えられます。
スカラー値のカラムは通常通り数値のまま返されます。

#### 対応メディアタイプ

| W&B のログ方法   | 対応 |
| ---------------- | ---- |
| `wandb.Image`    | Yes  |
| `wandb.Video`    | Yes  |
| `wandb.Audio`    | Yes  |
| `wandb.Html`     | Yes  |
| `wandb.Table`    | Yes  |
| `wandb.Object3D` | Yes  |

#### ダウンロード先のディレクトリ構造

```
media_dir/
├── <run_id_1>/
│   └── media/
│       ├── images/
│       │   ├── generated_0.png
│       │   └── generated_1.png
│       └── audio/
│           ├── sample_0.wav
│           └── sample_1.wav
└── <run_id_2>/
    └── media/
        └── ...
```

### 返却される DataFrame のカラム

| カラム名   | 説明                                                         |
| ---------- | ------------------------------------------------------------ |
| `run_id`   | run の ID                                                    |
| `run_name` | run の表示名                                                 |
| `tags`     | run に付与されたタグのリスト                                 |
| `_step`    | ログのステップ番号                                           |
| (各 key)   | スカラー値、または `download_media=True` 時のローカルファイルパス |

### パラメータ

| パラメータ       | 型              | 必須 | デフォルト     | 説明                                                                    |
| ---------------- | --------------- | ---- | -------------- | ----------------------------------------------------------------------- |
| `run_ids`        | `Sequence[str]` | Yes  | —              | 取得対象の run ID のリスト                                              |
| `keys`           | `Sequence[str]` | Yes  | —              | 取得したいログデータの名前のリスト (例: `["loss", "accuracy"]`)         |
| `entity`         | `str \| None`   | No   | `None`         | W&B の entity 名。省略時は環境のデフォルト値を使用                      |
| `project`        | `str \| None`   | No   | `None`         | W&B のプロジェクト名。省略時は環境のデフォルト値を使用                  |
| `download_media` | `bool`          | No   | `False`        | `True` にするとメディアファイルをダウンロードしローカルパスに置き換える |
| `media_dir`      | `str \| Path`   | No   | `"wandb_media"` | メディアファイルの保存先ディレクトリ                                    |

## ライセンス

MIT
