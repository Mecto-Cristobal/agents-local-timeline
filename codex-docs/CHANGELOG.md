# Changelog

## 1.0.0 - 2026-02-14
- MVPを日本向け納品版として整理
- `FastAPI on_event` から `lifespan` へ移行
- `/api/agents/system/progress` の受け付け項目を拡張（運用投稿フォーマットに追従）
- `pages.py` の重複コンテキスト構築を整理
- サービス層の保存処理を `app/services/persistence.py` に共通化
- `editor.js` の構文破損とシーン読込処理を修正
- `start_agents.bat` の既定ホストを `127.0.0.1` へ変更
- テスト基盤を `StaticPool` へ統一し、`pytest` 安定実行を確認
