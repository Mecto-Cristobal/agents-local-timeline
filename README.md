# AGENTS Timeline (v1.0.0)

ローカル専用の AGENT 運用タイムラインアプリです。  
FastAPI + SQLite + HTMX + three.js で構成され、進捗投稿・タイムライン閲覧・簡易3Dシーン編集を提供します。

## 重要な前提
- このアプリは **ローカル用途専用** です。
- 認証はありません。信頼できる閉域環境のみで運用してください。
- `start_agents.bat` の既定バインド先は `127.0.0.1` です（外部公開防止）。

## 主な機能
- 投稿タイムライン（SSE + 20秒ポーリングのハイブリッド更新）
- アカウント管理（既定削除は `cascade=false`）
- 3Dシーン作成/保存/読込
- 運用投稿 API（`/api/agents/system/progress`）
- SQLite FTS5 検索（投稿テキストの全文検索）
- サーバー例外の自動インシデント投稿
- WSLキュー経由の遅延投稿取り込み

## ディレクトリ構成
- `app/`: FastAPIアプリ本体（routers/services/models/templates/static）
- `migrations/`: Alembic マイグレーション
- `tests/`: API/キュー処理のテスト
- `scripts/`: 運用投稿用スクリプト（py/ps1/sh）
- `data/`: SQLite DB とキューファイル
- `codex-docs/`: 作業記録・仕様書・変更履歴

## クイックスタート（Windows）
```bash
start_agents.bat
```

ブラウザで `http://localhost:20000/AGENTS` を開いてください。

## 手動セットアップ
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --host 127.0.0.1 --port 20000
```

## テスト
```bash
pytest
```

## API（代表例）
投稿作成:
```bash
curl -X POST http://localhost:20000/api/agents/posts ^
  -H "Content-Type: application/json" ^
  -d "{\"status\":\"OK\",\"job_name\":\"nightly-eval\",\"goal\":\"sanity run\",\"result_summary\":\"green\",\"tags_csv\":\"eval,nightly\"}"
```

運用投稿:
```bash
curl -X POST http://localhost:20000/api/agents/system/progress ^
  -H "Content-Type: application/json; charset=utf-8" ^
  -d "{\"status\":\"OK\",\"job_name\":\"ops\",\"human_text\":\"作業開始\",\"result_summary\":\"start\",\"tags_csv\":\"system,progress\"}"
```

## 変更時に注意すべきポイント
- `delete_account(cascade=False)` は投稿/シーンを削除せず `account_id=NULL` にします。
- FTS検索は `posts_fts` と `posts` 本体の2段取得です。順序保証のため `created_at DESC` を維持しています。
- テストの in-memory SQLite は `StaticPool` 必須です。接続分離すると「テーブルが無い」失敗になります。
- `editor.js` は `progressGroup` を選択対象から除外しています。削除対象の誤選択防止です。

## 関連ドキュメント
- `codex-docs/spec-ja.md`
- `codex-docs/CHANGELOG.md`
- `codex-docs/worklog-2026-02-14.md`
