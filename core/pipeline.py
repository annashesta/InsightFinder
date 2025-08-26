# pipeline.py

from core.data_loader import load_data
from core.utils import make_target_binary, find_binary_target
from core.orchestrator import run_simple_orchestration
from report.generate_report import save_report
import os


def analyze_dataset(data_path: str, target_column: str | None = None, filename: str | None = None):
    """
    Запускает полный пайплайн анализа данных.

    Args:
        data_path: Путь к CSV-файлу.
        target_column: Название целевой переменной. Если None, будет найдена автоматически.
        filename: Имя файла для отчета. Если None, будет взято из data_path.

    Returns:
        Кортеж (путь_к_отчету, история, текст_отчета) или None в случае ошибки.
    """
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Файл не найден: {data_path}")

    print(f"📂 Загружаем данные из {data_path}...")
    df = load_data(data_path)

    # Если имя файла не передано, используем базовое имя пути
    if filename is None:
        filename = os.path.basename(data_path)
        print(f"📄 Имя файла для отчета: '{filename}'")

    if target_column is None:
        print("🔍 Автоопределение бинарной целевой переменной...")
        target_column = find_binary_target(df)
        print(f"✅ Найдена целевая переменная: '{target_column}'")
    else:
        if target_column not in df.columns:
            raise ValueError(f"Столбец '{target_column}' не найден.")
        print(f"🎯 Используем целевую переменную: '{target_column}'")

    try:
        df = make_target_binary(df, target_column)
        print(f"✅ Целевая переменная '{target_column}' преобразована в 0/1.")
    except Exception as e:
        print(f"❌ Ошибка обработки целевой переменной: {e}")
        return

    print("🚀 Запускаем мультиагентный анализ...")
    history, final_report = run_simple_orchestration(
        df=df,
        target_column=target_column,
        filename=filename
    )

    # Инициализируем report_path, чтобы он был доступен в случае ошибки сохранения
    report_path = None
    try:
        report_path = save_report(final_report)
        print(f"\n✅ Отчёт сохранён: {report_path}")
    except Exception as e:
        print(f"❌ Ошибка сохранения отчёта: {e}")
        # Не возвращаем здесь, продолжаем выполнение, чтобы вернуть историю и отчет

    # Возвращаем report_path (может быть None), историю и текст отчета
    return report_path, history, final_report
