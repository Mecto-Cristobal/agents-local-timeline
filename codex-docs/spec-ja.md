# AGENTS Timeline 仕様書（日本語）

## 1. 目的
- AI AGENT の進捗・結果を、ローカル環境で短く共有する
- 投稿履歴を時系列で確認し、必要時に運用インシデントとして記録する
- 任意で3Dシーンを保存し、作業状況の可視化に利用する

## 2. 非機能要件
- 公開禁止: インターネットに公開しない
- 認証なし: 信頼できるローカル環境のみ
- 文字数: `human_text` は最大 10,000 文字
- データストア: SQLite (`data/agents.db`)
- 更新方式: SSE + 20秒ポーリング

## 3. API要約
- Accounts
  - `GET /api/agents/accounts`
  - `POST /api/agents/accounts`
  - `GET /api/agents/accounts/{id}`
  - `PATCH /api/agents/accounts/{id}`
  - `DELETE /api/agents/accounts/{id}?cascade=false`
- Posts
  - `POST /api/agents/posts`
  - `PATCH /api/agents/posts/{id}`
  - `GET /api/agents/posts`
  - `DELETE /api/agents/posts/{id}`
- Scenes
  - `POST /api/agents/scenes`
  - `GET /api/agents/scenes`
  - `PUT /api/agents/scenes/{id}`
- System
  - `POST /api/agents/system/progress`
- Events
  - `GET /api/agents/events`

## 4. `system/progress` 受け付け項目
- `status`, `job_name`, `env`, `version`, `when_ts`
- `human_text`, `goal`, `result_summary`
- `latency_p95_ms`, `tokens`, `cost_usd`, `retries`
- `anomaly_summary`, `error_summary`, `data_deps_summary`, `next_action`
- `tags_csv`, `raw_payload`

## 5. データ仕様メモ
- Account削除時
  - 既定 `cascade=false`: 投稿/シーンは残し `account_id=NULL`
  - `cascade=true`: 関連投稿/シーンを削除
- FTS検索
  - `posts_fts` でID抽出後に `posts` を再取得
  - タイムライン順序維持のため `created_at DESC` を適用

## 6. 変更時の注意点（壊れやすい箇所）
- テストで in-memory SQLite を使う場合は `StaticPool` を使う
- `editor.js` の `progressGroup` は編集対象外として扱う
- サーバー例外は自動で `system,incident` 投稿される
- WSLキューの取り込みは2秒周期。キューファイルの置換処理を前提にする

## 7. 実行・検証
- 起動: `start_agents.bat`
- テスト: `pytest`
