"""Сервис экспорта проекта в JSON и Markdown."""

from datetime import datetime, timezone


def _isoformat(value):
    """Преобразует datetime в ISO-8601 строку или None."""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).isoformat()
    return str(value)


def _linked_prompts(project):
    """Уникальные промпты, привязанные к сценам проекта (порядок сцен)."""
    seen = set()
    prompts = []
    for scene in sorted(project.scenes, key=lambda s: s.order or 0):
        prompt = scene.prompt
        if prompt is None or prompt.id in seen:
            continue
        seen.add(prompt.id)
        prompts.append(prompt)
    return prompts


def _prompt_payload(prompt) -> dict:
    """Сериализует промпт и его версии для JSON-экспорта."""
    versions = []
    for version in sorted(prompt.versions, key=lambda v: v.version_number or 0):
        versions.append(
            {
                "version_number": version.version_number,
                "prompt_text": version.prompt_text,
                "negative_prompt": version.negative_prompt,
                "camera": version.camera_params,
                "lighting": version.lighting,
                "style": version.visual_style,
                "aspect_ratio": version.frame_format,
                "notes": version.notes,
                "change_note": version.change_note,
                "created_at": _isoformat(version.created_at),
                "average_rating": version.average_rating,
            }
        )
    return {
        "id": prompt.id,
        "title": prompt.name,
        "purpose": prompt.purpose,
        "ai_service": prompt.service,
        "tags": ([t.strip() for t in prompt.tags.split(",") if t.strip()] if prompt.tags else []),
        "versions": versions,
    }


def _append_prompt_markdown(lines, prompt) -> None:
    """Добавляет блок промпта в Markdown-документ."""
    lines.append(f"### {prompt.name}")
    lines.append("")
    if prompt.purpose:
        lines.append(f"**Назначение:** {prompt.purpose}")
    if prompt.service:
        lines.append(f"**Сервис:** {prompt.service}")
    if prompt.tags:
        tags = ", ".join(t.strip() for t in prompt.tags.split(",") if t.strip())
        lines.append(f"**Теги:** {tags}")
    lines.append("")

    versions = sorted(prompt.versions, key=lambda v: v.version_number or 0)
    for version in versions:
        lines.append(f"#### Версия {version.version_number or '—'}")
        lines.append("")
        lines.append(f"{version.prompt_text}")
        lines.append("")
        if version.negative_prompt:
            lines.append(f"**Negative prompt:** {version.negative_prompt}")
            lines.append("")
        if version.camera_params:
            lines.append(f"**Камера:** {version.camera_params}")
        if version.lighting:
            lines.append(f"**Освещение:** {version.lighting}")
        if version.visual_style:
            lines.append(f"**Стиль:** {version.visual_style}")
        if version.frame_format:
            lines.append(f"**Кадр:** {version.frame_format}")
        if version.notes:
            lines.append(f"**Заметки:** {version.notes}")
        if version.change_note:
            lines.append(f"**Причина изменения:** {version.change_note}")
        lines.append(f"**Создана:** {_isoformat(version.created_at) or '—'}")
        avg = version.average_rating
        if avg is not None:
            lines.append(f"**Средняя оценка:** {avg:.1f}/5")
        lines.append("")
        lines.append("---")
        lines.append("")


def export_project_json(project) -> dict:
    """Возвращает структурированный dict проекта для json.dumps.

    В ``prompts`` попадают только промпты, привязанные хотя бы к одной сцене.
    """
    scenes = []
    for scene in sorted(project.scenes, key=lambda s: s.order or 0):
        scenes.append(
            {
                "order": scene.order,
                "title": scene.title,
                "description": scene.description,
                "duration_seconds": scene.duration_seconds,
                "status": scene.status,
                "prompt_id": scene.prompt_id,
            }
        )

    prompts = [_prompt_payload(prompt) for prompt in _linked_prompts(project)]

    return {
        "project": {
            "id": project.id,
            "title": project.title,
            "description": project.description,
            "visual_style": project.visual_style,
            "content_format": project.content_format,
            "created_at": _isoformat(project.created_at),
            "updated_at": _isoformat(project.updated_at),
        },
        "scenes": scenes,
        "prompts": prompts,
    }


def export_project_markdown(project) -> str:
    """Возвращает читаемый Markdown-документ проекта."""
    lines = []

    lines.append(f"# {project.title}")
    lines.append("")

    if project.description:
        lines.append("## Описание")
        lines.append("")
        lines.append(project.description)
        lines.append("")

    lines.append("## Сведения о проекте")
    lines.append("")
    lines.append(f"- **Визуальный стиль:** {project.visual_style or '—'}")
    lines.append(f"- **Формат контента:** {project.content_format or '—'}")
    lines.append(f"- **Создан:** {_isoformat(project.created_at) or '—'}")
    lines.append(f"- **Обновлён:** {_isoformat(project.updated_at) or '—'}")
    lines.append("")

    lines.append("## Сцены")
    lines.append("")
    if project.scenes:
        for scene in sorted(project.scenes, key=lambda s: s.order or 0):
            lines.append(f"### Сцена {scene.order or '—'}: {scene.title}")
            lines.append("")
            if scene.description:
                lines.append(scene.description)
                lines.append("")
            lines.append(f"- **Длительность:** {scene.duration_seconds or '—'} сек.")
            lines.append(f"- **Статус:** {scene.status}")
            prompt_name = scene.prompt.name if scene.prompt else "—"
            lines.append(f"- **Промпт:** {prompt_name}")
            lines.append("")
    else:
        lines.append("Сцен нет.")
        lines.append("")

    lines.append("## Связанные промпты")
    lines.append("")
    prompt_list = _linked_prompts(project)
    if prompt_list:
        for prompt in prompt_list:
            _append_prompt_markdown(lines, prompt)
    else:
        lines.append("Промптов нет.")
        lines.append("")

    return "\n".join(lines)
