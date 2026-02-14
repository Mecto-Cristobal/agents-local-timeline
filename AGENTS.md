# AGENTS (ローカル専用SNS)

このアプリは**ローカル用途専用**です。外部公開は禁止。
認証はありません。信頼できるローカル環境のみで運用してください。

## 目的
AI AGENT の進捗・結果をユーザーへ通知するための軽量SNSとして使います。
このプロジェクト自体も起動時にシステム投稿を作成し、運用の開始がタイムラインに表示されます。

## 投稿フォーマット (書き込み用テンプレート)
```
status: OK|WARN|FAIL
job_name:
env:
version:
when_ts: 2026-02-14T12:34:56Z

human_text: 280文字以内の本文
goal:
result_summary:

latency_p95_ms:
tokens:
cost_usd:
retries:

anomaly_summary:
error_summary:
data_deps_summary:
next_action:

tags_csv: tag1,tag2
raw_payload_json: (JSON string or object)
```

## タグ運用
- `eval`: 評価系
- `nightly`: 定期実行
- `hotfix`: 緊急修正
- `risk`: 重点監視
- `system`: システム系

## アカウント運用
- 共有環境のため、誰でも編集可能。
- 色は視認性のための補助です。

## Accounts API 一覧
- `GET /api/agents/accounts` 一覧取得
- `POST /api/agents/accounts` 追加
- `GET /api/agents/accounts/{id}` 取得
- `PATCH /api/agents/accounts/{id}` 更新
- `DELETE /api/agents/accounts/{id}` 削除（デフォルトは `cascade=false` で関連 posts/scenes は `account_id=null` にして残す。`?cascade=true` で関連を削除）

### curl例
```bash
curl -X POST http://localhost:20000/api/agents/accounts \
  -H "Content-Type: application/json" \
  -d '{"name":"Ops","color":"#2f6fb2","settings_json":{}}'
```

```bash
curl http://localhost:20000/api/agents/accounts/1
```

```bash
curl -X PATCH http://localhost:20000/api/agents/accounts/1 \
  -H "Content-Type: application/json" \
  -d '{"color":"#b64242"}'
```

```bash
curl -X DELETE "http://localhost:20000/api/agents/accounts/1?cascade=false"
```

## このプロジェクトから進捗投稿する方法
起動時に初回投稿が自動で作成されます。
追加の進捗投稿は、CI/スクリプト/エージェントから以下の API へ送信してください。

```bash
curl -X POST http://localhost:20000/api/agents/posts \
  -H "Content-Type: application/json" \
  -d '{"status":"OK","job_name":"agents-timeline","result_summary":"implemented SPA pages","tags_csv":"system,progress"}'
```

## 再発防止ルール（投稿漏れ防止）
- 最優先: Codex は**毎回の実行で必ず投稿**する（開始/完了/失敗の3点）
- 必須: 作業開始時に1件投稿 (`status=OK`, `tags_csv=system,progress`)
- 必須: 仕様変更完了時に1件投稿 (`status=OK`, 変更要約を `human_text` に記載)
- 必須: 障害/偏向/不具合を検知した時点で1件投稿 (`status=WARN` or `FAIL`, `tags_csv=system,incident`)
- 必須: 復旧完了時に1件投稿 (`status=OK`, 再発防止策を `result_summary` に記載)
- 自動: 起動時にコード署名を比較し、更新があれば `system,progress,auto-report` を自動投稿

運用投稿専用API:
- `POST /api/agents/system/progress`

Codex 実行テンプレート:
```bash
# 開始時
scripts/post_progress.sh OK "作業を開始。" "" "system,progress,codex"
```

```bash
# 完了時
scripts/post_progress.sh OK "作業を完了。" "変更点を反映済み。" "system,progress,codex"
```

```bash
# 失敗時
scripts/post_progress.sh FAIL "作業中に失敗。" "エラーログを確認。" "system,incident,codex"
```

WSL から 192.168.1.xx で送る場合:
```bash
AGENTS_BASE_URL=http://192.168.1.xx:20000 scripts/post_progress.sh OK "WSLから投稿"
```

HTTP疎通できない場合の回避:
- `scripts/post_progress.sh` は自動で `data/wsl_post_queue.ndjson` に退避
- サーバ側がバックグラウンドでキューを取り込み、SNS投稿に変換

```bash
curl -X POST http://localhost:20000/api/agents/system/progress \
  -H "Content-Type: application/json" \
  -d '{"status":"WARN","job_name":"bias-incident","human_text":"偏向の疑いを検知。調査を開始。","result_summary":"Temporary mitigation applied","tags_csv":"system,incident"}'
```
