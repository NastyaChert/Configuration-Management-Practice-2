"""Модуль получения прямых зависимостей пакетов."""

import json
import re
import urllib.error
import urllib.request

HTTP_TIMEOUT = 10
VERSION_CLEAN_PATTERN = r"[\[\]\(\),\s]"


def fetch_json(url: str) -> dict:
    """Загружает и декодирует JSON по указанному URL."""
    req = urllib.request.Request(url, headers={"User-Agent": "DepViz/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Ошибка сети при обращении к {url}: {exc}") from exc


def get_registration_base_url(index_url: str) -> str:
    """Извлекает базовый URL сервиса регистраций из индекса NuGet v3."""
    data = fetch_json(index_url)
    for resource in data.get("resources", []):
        res_type = resource.get("@type", "")
        if res_type.startswith("RegistrationsBaseUrl"):
            return resource["@id"].rstrip("/")
    raise RuntimeError("В индексе репозитория не найден RegistrationsBaseUrl.")


def normalize_version(version_range: str) -> str:
    """Извлекает конкретную версию из диапазона версий NuGet."""
    cleaned = re.sub(VERSION_CLEAN_PATTERN, " ", version_range).strip()
    if not cleaned:
        return ""
    return cleaned.split()[0]


def get_nuget_dependencies(
    index_url: str, package: str, version: str
) -> list[tuple[str, str]]:
    """Получает список прямых зависимостей (имя, версия) для пакета NuGet."""
    base_url = get_registration_base_url(index_url)
    pkg_lower = package.lower()
    ver_lower = version.lower()
    leaf_url = f"{base_url}/{pkg_lower}/{ver_lower}.json"
    leaf_data = fetch_json(leaf_url)

    catalog_entry = leaf_data.get("catalogEntry", leaf_data)
    if isinstance(catalog_entry, str):
        catalog_entry = fetch_json(catalog_entry)

    deps: dict[str, str] = {}
    for group in catalog_entry.get("dependencyGroups", []):
        for dep in group.get("dependencies", []):
            dep_id = dep.get("id")
            dep_ver = normalize_version(dep.get("range", ""))
            if dep_id and dep_id not in deps:
                deps[dep_id] = dep_ver
    return list(deps.items())


def load_test_repo(file_path: str) -> dict[str, list[str]]:
    """Загружает граф тестового репозитория из текстового файла."""
    graph: dict[str, list[str]] = {}
    with open(file_path, encoding="utf-8") as file:
        for raw_line in file:
            line = raw_line.strip()
            if not line or ":" not in line:
                continue
            node, targets_str = line.split(":", maxsplit=1)
            targets = [t.strip() for t in targets_str.split() if t.strip()]
            graph[node.strip()] = targets
    return graph