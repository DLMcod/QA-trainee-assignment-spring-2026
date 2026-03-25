# QA Trainee Assignment — Spring 2026

Автоматизированные API-тесты для микросервиса объявлений Avito.

## Структура проекта

```
├── conftest.py              # Фикстуры pytest (создание/удаление объявлений)
├── tests/
│   ├── test\_create\_item.py  # POST /api/1/item
│   ├── test\_get\_item.py     # GET /api/1/item/:id
│   ├── test\_get\_seller\_items.py  # GET /api/1/:sellerID/item
│   ├── test\_statistics.py   # GET /api/1/statistic/:id
│   └── test\_e2e.py          # E2E сценарии
├── TESTCASES.md             # Описание тест-кейсов
├── BUGS.md                  # Баг-репорты (скриншот + API)
├── requirements.txt         # Зависимости Python
├── pytest.ini               # Конфигурация pytest
├── ruff.toml                # Конфигурация линтера
└── allure-results/          # Результаты Allure (генерируются при запуске)
```

## Требования

* Python 3.10+
* pip

## Установка и запуск

```bash
# 1. Клонировать репозиторий
git clone <repo-url>
cd avito-qa-assignment

# 2. Создать виртуальное окружение и установить зависимости
python3 -m venv venv
source venv/bin/activate   # Linux/macOS
# venv\\Scripts\\activate    # Windows
pip install -r requirements.txt

# 3. Запустить все тесты
pytest

# 4. Запустить с подробным выводом
pytest -v

# 5. Запустить конкретный файл
pytest tests/test\_create\_item.py -v

# 6. Запустить только позитивные тесты
pytest -k "Positive" -v
```

## Allure-отчёт

```bash
# Запуск тестов с генерацией Allure
pytest --alluredir=allure-results

# Просмотр отчёта (требуется allure CLI)
allure serve allure-results
```

## Линтер

```bash
# Проверка
ruff check .

# Автоисправление
ruff check --fix .
```

## Результаты

* **51 тест** (44 pass / 7 fail)
* **7 failing тестов** — все документируют найденные баги (BUG-1..BUG-8)
* **8 багов API**  — описаны в BUGS.md

## Стек

* **Python 3** + **pytest** — фреймворк тестирования
* **requests** — HTTP-клиент
* **allure-pytest** — Allure-отчёты (шаги, описания, вложения)
* **ruff** — линтер

