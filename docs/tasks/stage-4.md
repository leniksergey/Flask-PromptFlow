# Этап 4 — Экспорт и аналитика

> Прочитай `AGENTS.md` полностью и предыдущие `stage-*.md`. Проверь, что модели Project/Scene/Prompt/PromptVersion/PromptRating готовы.

## Цель этапа
Реализовать экспорт проекта в Markdown и JSON, а также dashboard с базовыми показателями.

## Задачи

### 1. Сервис экспорта
- `app/services/export_service.py`:
  - `export_project_json(project) -> dict` — структурированный dict, готовый к `json.dumps(..., ensure_ascii=False, indent=2)`;
  - `export_project_markdown(project) -> str` — читаемый документ.
- Содержимое JSON (задокументируй в README):
```json
{
  "project": {
    "id": 1,
    "title": "...",
    "description": "...",
    "visual_style": "...",
    "content_format": "...",
    "created_at": "ISO-8601",
    "updated_at": "ISO-8601"
  },
  "scenes": [
    {
      "order": 1,
      "title": "...",
      "description": "...",
      "duration_seconds": 10,
      "status": "planned"
    }
  ],
  "prompts": [
    {
      "title": "...",
      "purpose": "...",
      "ai_service": "...",
      "tags": ["..."],
      "versions": [
        {
          "version_number": 1,
          "prompt_text": "...",
          "negative_prompt": "...",
          "camera": "...",
          "lighting": "...",
          "style": "...",
          "aspect_ratio": "...",
          "notes": "...",
          "change_note": "...",
          "created_at": "ISO-8601",
          "average_rating": 4.5
        }
      ]
    }
  ]
}
