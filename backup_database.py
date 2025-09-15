#!/usr/bin/env python3
"""
Database backup and restore utility for King's Choice database.
This script helps backup your VPS database and restore it to your workspace.
"""

import sqlite3
import os
import sys
import subprocess
from datetime import datetime

def backup_database(db_path, backup_path):
    """Create a backup of the SQLite database"""
    try:
        # Connect to the source database
        conn = sqlite3.connect(db_path)
        
        # Create backup using SQLite's backup API
        backup_conn = sqlite3.connect(backup_path)
        conn.backup(backup_conn)
        
        # Close connections
        backup_conn.close()
        conn.close()
        
        print(f"✅ Database backup created successfully: {backup_path}")
        return True
    except Exception as e:
        print(f"❌ Error creating backup: {e}")
        return False

def create_sql_dump(db_path, dump_path):
    """Create a SQL dump of the database"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        with open(dump_path, 'w', encoding='utf-8') as f:
            f.write("PRAGMA foreign_keys=OFF;\n")
            f.write("BEGIN TRANSACTION;\n")
            
            for table in tables:
                table_name = table[0]
                
                # Get table schema
                cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table_name}';")
                schema = cursor.fetchone()
                if schema and schema[0]:
                    f.write(f"{schema[0]};\n")
                
                # Get table data
                cursor.execute(f"SELECT * FROM {table_name};")
                rows = cursor.fetchall()
                
                if rows:
                    # Get column names
                    cursor.execute(f"PRAGMA table_info({table_name});")
                    columns = [col[1] for col in cursor.fetchall()]
                    
                    for row in rows:
                        values = []
                        for value in row:
                            if value is None:
                                values.append('NULL')
                            elif isinstance(value, str):
                                # Escape single quotes
                                escaped_value = value.replace("'", "''")
                                values.append(f"'{escaped_value}'")
                            else:
                                values.append(str(value))
                        
                        f.write(f"INSERT INTO {table_name} VALUES({','.join(values)});\n")
            
            f.write("COMMIT;\n")
        
        conn.close()
        print(f"✅ SQL dump created successfully: {dump_path}")
        return True
    except Exception as e:
        print(f"❌ Error creating SQL dump: {e}")
        return False

def restore_database(db_path, dump_path):
    """Restore database from SQL dump"""
    try:
        # Remove existing database if it exists
        if os.path.exists(db_path):
            os.remove(db_path)
        
        # Create new database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Read and execute SQL dump
        with open(dump_path, 'r', encoding='utf-8') as f:
            sql_dump = f.read()
            cursor.executescript(sql_dump)
        
        conn.commit()
        conn.close()
        
        print(f"✅ Database restored successfully: {db_path}")
        return True
    except Exception as e:
        print(f"❌ Error restoring database: {e}")
        return False

def verify_database(db_path):
    """Verify database integrity and show basic stats"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get table names and row counts
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print("\n📊 Database Statistics:")
        print("-" * 40)
        
        total_rows = 0
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
            count = cursor.fetchone()[0]
            total_rows += count
            print(f"{table_name:20} : {count:>6} rows")
        
        print("-" * 40)
        print(f"{'Total':20} : {total_rows:>6} rows")
        
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Error verifying database: {e}")
        return False

def main():
    """Main function with command line interface"""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 backup_database.py backup <source_db> [backup_name]")
        print("  python3 backup_database.py restore <dump_file> <target_db>")
        print("  python3 backup_database.py verify <db_path>")
        print("\nExamples:")
        print("  # Backup VPS database")
        print("  python3 backup_database.py backup /path/to/kings_choice.db")
        print("  # Restore to workspace")
        print("  python3 backup_database.py restore backup_2024-01-15.sql kings_choice.db")
        print("  # Verify database")
        print("  python3 backup_database.py verify kings_choice.db")
        return
    
    command = sys.argv[1]
    
    if command == "backup":
        if len(sys.argv) < 3:
            print("❌ Error: Source database path required")
            return
        
        source_db = sys.argv[2]
        if not os.path.exists(source_db):
            print(f"❌ Error: Source database not found: {source_db}")
            return
        
        # Generate backup filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = sys.argv[3] if len(sys.argv) > 3 else f"kings_choice_backup_{timestamp}"
        
        # Create both binary backup and SQL dump
        binary_backup = f"{backup_name}.db"
        sql_dump = f"{backup_name}.sql"
        
        print(f"🔄 Creating backup from: {source_db}")
        print(f"📦 Binary backup: {binary_backup}")
        print(f"📄 SQL dump: {sql_dump}")
        
        success1 = backup_database(source_db, binary_backup)
        success2 = create_sql_dump(source_db, sql_dump)
        
        if success1 and success2:
            print(f"\n✅ Backup completed successfully!")
            print(f"📁 Files created:")
            print(f"   - {binary_backup}")
            print(f"   - {sql_dump}")
        else:
            print(f"\n❌ Backup failed!")
    
    elif command == "restore":
        if len(sys.argv) < 4:
            print("❌ Error: Dump file and target database path required")
            return
        
        dump_file = sys.argv[2]
        target_db = sys.argv[3]
        
        if not os.path.exists(dump_file):
            print(f"❌ Error: Dump file not found: {dump_file}")
            return
        
        print(f"🔄 Restoring database from: {dump_file}")
        print(f"🎯 Target database: {target_db}")
        
        if restore_database(target_db, dump_file):
            verify_database(target_db)
    
    elif command == "verify":
        if len(sys.argv) < 3:
            print("❌ Error: Database path required")
            return
        
        db_path = sys.argv[2]
        if not os.path.exists(db_path):
            print(f"❌ Error: Database not found: {db_path}")
            return
        
        verify_database(db_path)
    
    else:
        print(f"❌ Unknown command: {command}")

if __name__ == "__main__":
    main()