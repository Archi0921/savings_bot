# savings_bot

## Описание проекта
Многие люди в попытке отложить деньги на важные цели не знают или не понимают, как правильно спланировать свои накопления. Наш Telegram-бот решает эту проблему и предоставляет пользователям помощь в планировании и накоплении денежных средств. Бот регулярно напоминает о необходимости пополнить "копилку" и предоставляет отчёты о достижении цели.
Основные технологии: SQLAlchemy, Aiogram, APScheduler, SQLite.

### Основные возможности
- **Постановка финансовых целей**: Пользователь может поставить перед собой цель, введя сумму цели, свою заработную плату и процент от зарплаты, который готов ежемесячно откладывать;
- **Автоматический расчёт графика платежей**: На основании введённых данных бот рассчитывает предполагаемый график платежей, чтобы помочь пользователю достичь своей цели в оптимальные сроки;
- **Напоминания**: Бот напоминает пользователю в оптимальные даты о необходимости отложить деньги, чтобы не забывать о своих финансовых целях;
- **Отчёты и прогресс**: Пользователь может в любой момент запросить текущий статус своих накоплений и увидеть прогресс по каждой цели.

### Планы на будущее

В будущих версиях бота мы планируем добавить:
- Возможность корректировки графика платежей;
- Настройку частоты и времени напоминаний;
- Инфографику о достижениях и награды для повышения мотивации пользователей.

## Установка и запуск
### Установка зависимостей

Установите необходимые зависимости, выполнив:

```
pip install -r requirements.txt
```

### Установка TOKEN
В директории вашего проекта создайте файл .env с содержанием:
```
TOKEN=<токен вашего Telegram-бота>
```

### Запуск бота
Запустите бота, выполнив:
```
python main.py
```
