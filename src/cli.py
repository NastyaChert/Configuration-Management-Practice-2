"""Модуль разбора и валидации аргументов командной строки."""

import argparse
import os
import re
from dataclasses import dataclass

MIN_DEPTH = 0
VERSION_PATTERN = r"^[0-9A-Za-z.\-+]+$"


@dataclass
class AppConfig:
    """Конфигурация приложения."""

    package: str
    repo: str
    test_mode: bool
    version: str
    ascii_tree: bool
    max_depth: int
    load_order: bool


def parse_args(argv: list[str] | None = None) -> AppConfig:
    """Разбирает и проверяет аргументы командной строки."""
    parser = argparse.ArgumentParser(
        description="Визуализатор графа зависимостей NuGet."
    )
    parser.add_argument("-p", "--package", required=True, help="Имя пакета")
    parser.add_argument("-r", "--repo", required=True, help="URL или путь")
    parser.add_argument("-t", "--test-mode", action="store_true")
    parser.add_argument("-v", "--version", default="", help="Версия пакета")
    parser.add_argument("-a", "--ascii", action="store_true")
    parser.add_argument("-d", "--max-depth", type=int, default=3)
    parser.add_argument("-l", "--load-order", action="store_true")

    args = parser.parse_args(argv)
    validate_args(args)
    return AppConfig(
        package=args.package.strip(),
        repo=args.repo.strip(),
        test_mode=args.test_mode,
        version=args.version.strip(),
        ascii_tree=args.ascii,
        max_depth=args.max_depth,
        load_order=args.load_order,
    )


def validate_args(args: argparse.Namespace) -> None:
    """Проверяет корректность переданных пользователем параметров."""
    if not args.package or not args.package.strip():
        raise ValueError("Имя пакета не может быть пустым.")
    if args.max_depth < MIN_DEPTH:
        raise ValueError("Максимальная глубина не может быть отрицательной.")
    if args.test_mode and not os.path.isfile(args.repo):
        raise FileNotFoundError(f"Тестовый файл не найден: {args.repo}")
    if not args.test_mode:
        if not args.repo.startswith(("http://", "https://")):
            raise ValueError("URL репозитория должен начинаться с http/https.")
        if not args.version or not re.match(VERSION_PATTERN, args.version):
            raise ValueError("Некорректный или пустой формат версии пакета.")