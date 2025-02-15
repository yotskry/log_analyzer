# Log Analyzer

Приложение для анализа логов и генерации html отчета на основе входных данных в виде лога nginx.

## Функциональность

- Чтение лога nginx, лог может быть в формате gz или plain text.
- Генерация отчета на основе статистики запросов.
- Поддержка внешнего конфигурационного файла через параметр --config. Формат конфигурационного файла:
  ```json
  {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log",
    "APP_LOGS": "./app_logs"
  }
  ```

## Запуск приложения

### Через Make

Для запуска приложения с использованием `Makefile` выполните следующие шаги:

1. Установите все зависимости:

    ```bash
    make install
    ```

2. Для запуска линтовки, тестов и приложения, используйте команды:

    - **Линтинг**:
      ```bash
      make lint
      ```

    - **Тестирование (с покрытием)**:
      ```bash
      make test
      ```
    
    - **Линтинг и тестирование**:
      ```bash
      make сheck
      ```

    - **Запуск приложения**:
      ```bash
      make run [OPTIONS="--config config/custom_config.json"]
      ```
    
    - **Очистка артефактов**:
      ```bash
      make clean
      ```

### Через Docker

1. Сборка Docker образа:

    Собрерите образ:

    ```bash
    docker build -t log_analyzer .
    ```

2. Запуск контейнера:

    После того как образ был собран, запустите контейнер:

    ```bash
    docker run --rm -v ./logs:/app/logs -v ./reports:/app/reports -v ./app_logs:/app/app_logs log_analyzer
    ```

    - **`logs:/app/logs`** — директория с логами nginx.
    - **`reports:/app/reports`** — директория для отчетов.
    - **`app_logs:/app/app_logs`** — директория с логами приложения.

Контейнер будет автоматически анализировать логи и генерировать отчет, который можно найти в указанной директории `reports`.