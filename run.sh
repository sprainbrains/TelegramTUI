#!/bin/bash

set -e

if [[ "$(basename "$0")" == "tg" ]]; then
    # Быстрый запуск через команду 'tg'
    SCRIPT_DIR="$(cd "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")" && pwd)"
    cd "$SCRIPT_DIR"
    if [ ! -f "main.py" ]; then
        echo "❌ main.py не найден в $SCRIPT_DIR"
        exit 1
    fi

    if [ ! -d ".venv" ]; then
        echo "❌ Виртуальное окружение (.venv) не найдено. Запустите сначала ./run.sh для настройки."
        exit 1
    fi

    source .venv/bin/activate
    exec python main.py
fi

echo "🔍 Проверка наличия Python..."

if command -v python3 &> /dev/null; then
    PYTHON=python3
elif command -v python &> /dev/null; then
    PYTHON=python
else
    echo "❌ Python не найден. Установите Python 3."
    exit 1
fi

echo "✅ Найден Python: $($PYTHON --version)"

VENV_DIR=".venv"
if [ ! -d "$VENV_DIR" ]; then
    echo "📦 Создание виртуального окружения..."
    "$PYTHON" -m venv "$VENV_DIR"
else
    echo "📁 Виртуальное окружение уже существует."
fi

source "$VENV_DIR/bin/activate"
pip install --upgrade pip > /dev/null 2>&1

if [ -f "requirements.txt" ]; then
    echo "📥 Установка зависимостей из requirements.txt..."
    pip install -r requirements.txt
else
    echo "⚠️ Файл requirements.txt не найден — пропуск установки зависимостей."
fi

if [ ! -f "main.py" ]; then
    echo "❌ Ошибка: файл main.py не найден в текущей директории."
    exit 1
fi


echo
echo "Хотите создать команду 'tg' для быстрого запуска из любого места? [y/N]: "
read -r REPLY

if [[ "$REPLY" =~ ^[Yy]([Ee][Ss])?$ ]]; then
    SCRIPT_ABS_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/$(basename "${BASH_SOURCE[0]}")"

    # Выбираем директорию
    if [ -w "/usr/local/bin" ]; then
        BIN_DIR="/usr/local/bin"
    else
        BIN_DIR="$HOME/.local/bin"
    fi

    # Если ~/.local/bin не существует — создаём с подтверждением
    if [ "$BIN_DIR" = "$HOME/.local/bin" ] && [ ! -d "$BIN_DIR" ]; then
        echo
        echo "Директория $BIN_DIR не найдена."
        echo "Создать её и добавить в PATH? [y/N]: "
        read -r CONFIRM
        if [[ "$CONFIRM" =~ ^[Yy]([Ee][Ss])?$ ]]; then
            mkdir -p "$BIN_DIR"
            echo "✅ Директория создана: $BIN_DIR"

            # Определяем файл конфигурации
            if [ -n "$ZSH_VERSION" ]; then
                RC_FILE="$HOME/.zshrc"
            elif [ -f "$HOME/.bashrc" ]; then
                RC_FILE="$HOME/.bashrc"
            elif [ -f "$HOME/.profile" ]; then
                RC_FILE="$HOME/.profile"
            else
                RC_FILE="$HOME/.bashrc"
                touch "$RC_FILE"
            fi

            # Добавляем в PATH, если ещё не добавлено
            if ! grep -q "$HOME/.local/bin" "$RC_FILE" 2>/dev/null; then
                echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$RC_FILE"
                echo "✅ Добавлено в PATH: $RC_FILE"
                export PATH="$HOME/.local/bin:$PATH"
            else
                echo "ℹ️  $HOME/.local/bin уже в PATH."
            fi
        else
            echo "❌ Отмена: невозможно создать команду без директории в PATH."
            exit 1
        fi
    fi

    # Создаём symlink
    LINK_PATH="$BIN_DIR/tg"
    rm -f "$LINK_PATH" 2>/dev/null || true
    ln -s "$SCRIPT_ABS_PATH" "$LINK_PATH"
    echo
    echo "✅ Команда 'tg' успешно установлена!"
    echo "Теперь вы можете запускать приложение из любой директории:"
    echo "Если команда 'tg' не распознаётся, перезапустите терминал или выполните 'source $RC_FILE'."
else
    echo "⏭️ Создание команды 'tg' пропущено."
fi

echo "✅ Работа завершена."

echo "🚀 Запуск приложения..."
python main.py
