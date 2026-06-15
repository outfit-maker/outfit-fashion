"""
智能穿搭推荐系统 - 性能优化模块
包含缓存机制和预计算功能
"""
import os
import pickle
import hashlib

class CacheManager:
    """缓存管理器"""
    
    def __init__(self, data_dir: str):
        self.cache_dir = os.path.join(data_dir, '.cache')
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def _get_cache_key(self, key: str) -> str:
        """生成缓存文件名"""
        return hashlib.md5(key.encode()).hexdigest() + '.pkl'
    
    def get(self, key: str):
        """获取缓存数据"""
        cache_path = os.path.join(self.cache_dir, self._get_cache_key(key))
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'rb') as f:
                    return pickle.load(f)
            except Exception:
                return None
        return None
    
    def set(self, key: str, value):
        """设置缓存数据"""
        cache_path = os.path.join(self.cache_dir, self._get_cache_key(key))
        try:
            with open(cache_path, 'wb') as f:
                pickle.dump(value, f)
            return True
        except Exception:
            return False
    
    def clear(self):
        """清除所有缓存"""
        for file in os.listdir(self.cache_dir):
            os.remove(os.path.join(self.cache_dir, file))

def optimize_recommendation_system(data_dir: str, label_df, translator, style_extractor):
    """
    预计算优化：预先处理所有衣物数据，缓存翻译结果和风格信息
    """
    cache = CacheManager(data_dir)
    
    # 尝试从缓存加载预处理数据
    cache_key = f"optimized_items_{len(label_df)}_{label_df['itemID'].max() if not label_df.empty else '0'}"
    optimized_items = cache.get(cache_key)
    
    if optimized_items is not None:
        print("✓ 使用缓存的预处理数据")
        return optimized_items
    
    print("正在预计算衣物数据...")
    optimized_items = {}
    
    for _, row in label_df.iterrows():
        item_id = str(row['itemID']).strip()
        gender = str(row.get('gender', '')).strip()
        composite_key = f"{item_id}_{gender}" if gender else item_id
        
        # 预计算翻译结果
        title = str(row['title'])
        title_cn = translator.translate(title, 'cn', 'title')
        
        # 预计算风格信息
        style = str(row.get('style', ''))
        style_cn = style_extractor.get_style_for_display(style, 'cn')
        
        info = {
            'itemID': item_id,
            'category': str(row['category']),
            'title': title,
            'title_cn': title_cn,
            'style': style,
            'style_cn': style_cn,
            'season': int(row.get('season', 1)),
            'thick': int(row.get('thick', 1)),
            'gender': gender,
        }
        optimized_items[composite_key] = info
    
    # 保存到缓存
    cache.set(cache_key, optimized_items)
    print(f"✓ 预计算完成，缓存了 {len(optimized_items)} 条衣物数据")
    
    return optimized_items

def build_category_index(optimized_items):
    """构建按类别和性别索引的快速查找结构"""
    items_by_category_gender = {}
    
    for key, info in optimized_items.items():
        cat = info['category']
        gender = info['gender']
        
        if cat not in items_by_category_gender:
            items_by_category_gender[cat] = {}
        if gender not in items_by_category_gender[cat]:
            items_by_category_gender[cat][gender] = []
        
        items_by_category_gender[cat][gender].append(info)
    
    return items_by_category_gender