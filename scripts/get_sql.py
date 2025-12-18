# scripts/extract_db_schema.py
from pathlib import Path
import sqlite3

# Путь к твоей базе данных (как в database.py)
DB_PATH = Path(__file__).parent.parent / "app" / "database" / "repair_requests.db"

def get_exact_schema():
    """Получает точную схему из базы данных repair_requests.db"""
    
    if not DB_PATH.exists():
        print(f"❌ База данных не найдена: {DB_PATH}")
        print("💡 Запусти сначала: python -m scripts.import_data")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("=" * 70)
    print("РЕАЛЬНАЯ СХЕМА БАЗЫ ДАННЫХ — Учёт заявок на ремонт")
    print("=" * 70)
    
    # Получаем все пользовательские таблицы
    cursor.execute("""
        SELECT name, sql 
        FROM sqlite_master 
        WHERE type='table' 
        AND name NOT LIKE 'sqlite_%'
        ORDER BY name
    """)
    
    tables = cursor.fetchall()
    
    all_sql = []
    
    for table_name, table_sql in tables:
        print(f"\nТАБЛИЦА: {table_name}")
        print("-" * 50)
        
        if table_sql:
            print(table_sql)
            all_sql.append(table_sql)
            
            # Структура колонок
            print(f"\nСТРУКТУРА {table_name}:")
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            for col in columns:
                col_id, col_name, col_type, not_null, default, pk = col
                flags = []
                if pk: flags.append("PRIMARY KEY")
                if not_null: flags.append("NOT NULL")
                if default is not None: flags.append(f"DEFAULT {default}")
                
                flags_str = " ".join(flags)
                print(f"  - {col_name}: {col_type} {flags_str}")
            
            # Внешние ключи
            cursor.execute(f"PRAGMA foreign_key_list({table_name})")
            fks = cursor.fetchall()
            
            if fks:
                print(f"\nВНЕШНИЕ КЛЮЧИ {table_name}:")
                for fk in fks:
                    if len(fk) >= 5:
                        _, _, table_to, col_from, col_to = fk[:5]
                        print(f"  - {col_from} → {table_to}.{col_to}")
        else:
            print("  (нет SQL-определения)")
        
        print("-" * 50)
    
    conn.close()
    
    # Сохраняем SQL-файл рядом с repair_requests.db
    sql_file_path = DB_PATH.parent / "db_schema.sql"
    with open(sql_file_path, "w", encoding="utf-8") as f:
        f.write("\n\n".join(all_sql))
    
    print(f"\n✅ Полный SQL-скрипт сохранён в:")
    print(f"   {sql_file_path}")
    print(f"\n📁 Расположение базы: {DB_PATH}")


if __name__ == "__main__":
    get_exact_schema()