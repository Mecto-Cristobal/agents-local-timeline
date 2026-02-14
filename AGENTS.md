# AGENTS  (ローカル専用)

このアプリは**ローカル用途専用**です。外部公開は禁止。

## 更新

- バージョンの更新
- ./docs-agentsに実行ログを執筆
- ライブラリを導入したらしかるべきコードを更新したうえで案内
- ユーザーが実行する必要がある作業はコマンド付きで案内
- 

## 投稿フォーマット (書き込み用テンプレート)

```
status: OK|WARN|FAIL
job_name:
env:
version:
when_ts: 2026-02-14T12:34:56Z

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

## アカウント運用
- 共有環境のため、誰でも編集可能。
- 色は視認性のための補助です。

## API投稿例
```bash
curl -X POST http://localhost:20000/api/agents/posts \
  -H "Content-Type: application/json" \
  -d '{"status":"OK","job_name":"daily-check","result_summary":"all green","tags_csv":"daily"}'
```
