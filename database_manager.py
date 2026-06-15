"""
智能穿搭推荐系统 - 数据库接入模块
将评分数据从CSV迁移到SQLite数据库
"""
import sqlite3
import pandas as pd
import os
from datetime import datetime
from typing import Dict, List, Optional

class DatabaseManager:
    """数据库管理器 - 使用SQLite存储评分数据"""
    
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.db_path = os.path.join(data_dir, 'ratings.db')
        self._init_database()
    
    def _init_database(self):
        """初始化数据库表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建评分表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ratings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                recommendation_type TEXT NOT NULL,
                rating INTEGER NOT NULL CHECK(rating BETWEEN 0 AND 5),
                feedback TEXT,
                items TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建索引以提高查询性能
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_ratings_type ON ratings(recommendation_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_ratings_rating ON ratings(rating)')
        
        conn.commit()
        conn.close()
    
    def migrate_from_csv(self, csv_path: str = None):
        """从CSV文件迁移数据到数据库"""
        if csv_path is None:
            csv_path = os.path.join(self.data_dir, 'ratings.csv')
        
        if not os.path.exists(csv_path):
            print("CSV文件不存在，跳过迁移")
            return
        
        try:
            df = pd.read_csv(csv_path)
            if df.empty:
                print("CSV文件为空，跳过迁移")
                return
            
            conn = sqlite3.connect(self.db_path)
            
            # 检查是否已有数据
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM ratings')
            count = cursor.fetchone()[0]
            if count > 0:
                print(f"数据库已有 {count} 条记录，跳过迁移")
                conn.close()
                return
            
            # 转换rating列为整数
            df['rating'] = pd.to_numeric(df['rating'], errors='coerce').fillna(0).astype(int)
            
            # 写入数据库
            df.to_sql('ratings', conn, if_exists='append', index=False)
            
            conn.commit()
            conn.close()
            print(f"成功迁移 {len(df)} 条评分记录到数据库")
        except Exception as e:
            print(f"迁移数据时出错: {e}")
    
    def add_rating(self, recommendation_type: str, rating: int, 
                   feedback: str = "", items: Optional[List[str]] = None) -> bool:
        """添加一条评分记录"""
        try:
            rating = max(0, min(5, int(rating)))
            items_str = ','.join(items) if items else ''
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO ratings (timestamp, recommendation_type, rating, feedback, items)
                VALUES (?, ?, ?, ?, ?)
            ''', (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), recommendation_type, rating, feedback, items_str))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"添加评分时出错: {e}")
            return False
    
    def get_statistics(self) -> Dict:
        """获取评分统计"""
        conn = sqlite3.connect(self.db_path)
        
        # 总评分数量
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM ratings')
        count = cursor.fetchone()[0]
        
        if count == 0:
            conn.close()
            return {'count': 0, 'avg_rating': 0.0, 'distribution': {}, 'by_type': {}}
        
        # 平均评分
        cursor.execute('SELECT AVG(rating) FROM ratings')
        avg_rating = round(float(cursor.fetchone()[0]), 2)
        
        # 评分分布
        distribution = {}
        for i in range(6):
            cursor.execute('SELECT COUNT(*) FROM ratings WHERE rating = ?', (i,))
            distribution[str(i)] = cursor.fetchone()[0]
        
        # 按类型统计
        by_type = {}
        cursor.execute('SELECT recommendation_type, AVG(rating) FROM ratings GROUP BY recommendation_type')
        for row in cursor.fetchall():
            by_type[row[0]] = round(float(row[1]), 2)
        
        conn.close()
        
        return {
            'count': count,
            'avg_rating': avg_rating,
            'distribution': distribution,
            'by_type': by_type,
        }
    
    def get_all_ratings(self) -> pd.DataFrame:
        """获取所有评分记录"""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql('SELECT * FROM ratings ORDER BY created_at DESC', conn)
        conn.close()
        return df
    
    def get_ratings_by_type(self, recommendation_type: str) -> pd.DataFrame:
        """按类型获取评分记录"""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql('SELECT * FROM ratings WHERE recommendation_type = ? ORDER BY created_at DESC', 
                         conn, params=(recommendation_type,))
        conn.close()
        return df

# ======================= 迁移脚本 =======================
def migrate_to_database(data_dir: str):
    """执行数据迁移"""
    print("=== 开始迁移评分数据到SQLite数据库 ===")
    
    db_manager = DatabaseManager(data_dir)
    db_manager.migrate_from_csv()
    
    # 测试数据库功能
    stats = db_manager.get_statistics()
    print(f"数据库统计信息:")
    print(f"  总评分数量: {stats['count']}")
    print(f"  平均评分: {stats['avg_rating']}")
    print(f"  评分分布: {stats['distribution']}")
    print(f"  按类型统计: {stats['by_type']}")
    
    print("=== 数据迁移完成 ===")

if __name__ == "__main__":
    import sys
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = current_dir  # 数据目录就是当前目录
    
    migrate_to_database(data_dir)