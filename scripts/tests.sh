#!/bin/sh
LOG_DIR="./logs"

mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/django_tests_$(date +%Y-%m-%d_%H-%M-%S).log"

docker compose exec djangoapp python manage.py test # -v 2 >> "$LOG_FILE" 2>&1
echo "✅ Testes salvos em $LOG_FILE"

find "$LOG_DIR" -name "django_tests_*.log" -mtime +7 -delete