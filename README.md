# get-wandb-data

Weights & Biases の複数の run からログデータを取得し、`pandas.DataFrame` として返すライブラリです。

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

### 出力例

| run_id   | run_name   | tags             | _step | loss  | accuracy |
| -------- | ---------- | ---------------- | ----- | ----- | -------- |
| abc123   | cool-run-1 | [v1, baseline]   | 0     | 0.95  | 0.10     |
| abc123   | cool-run-1 | [v1, baseline]   | 1     | 0.80  | 0.35     |
| def456   | cool-run-2 | [v2, experiment] | 0     | 0.90  | 0.12     |
| def456   | cool-run-2 | [v2, experiment] | 1     | 0.70  | 0.45     |

### 返却される DataFrame のカラム

| カラム名   | 説明                             |
| ---------- | -------------------------------- |
| `run_id`   | run の ID                        |
| `run_name` | run の表示名                     |
| `tags`     | run に付与されたタグのリスト     |
| `_step`    | ログのステップ番号               |
| (各 key)   | `keys` で指定したメトリクスの値  |

### パラメータ

| パラメータ | 型              | 必須 | 説明                                                                 |
| ---------- | --------------- | ---- | -------------------------------------------------------------------- |
| `run_ids`  | `Sequence[str]` | Yes  | 取得対象の run ID のリスト                                           |
| `keys`     | `Sequence[str]` | Yes  | 取得したいログデータの名前のリスト (例: `["loss", "accuracy"]`)      |
| `entity`   | `str \| None`   | No   | W&B の entity 名。省略時は環境のデフォルト値を使用                   |
| `project`  | `str \| None`   | No   | W&B のプロジェクト名。省略時は環境のデフォルト値を使用               |

## ライセンス

MIT
