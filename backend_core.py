"""
智能穿搭推荐系统 - 后端核心逻辑
=================================
包含:
1. 数据加载与清洗（并行加载优化）
2. 时尚术语智能翻译
3. 天气推荐引擎
4. 衣物推荐引擎
5. 风格提取与匹配
"""

import pandas as pd
import numpy as np
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional, Tuple
from collections import Counter
import re


# ======================= 1. 智能翻译模块 =======================

class FashionTranslator:
    """时尚术语中英文翻译"""
    
    def __init__(self):
        # 短语级翻译（优先匹配）
        self.phrase_cn = {
            "autumn/winter": "秋冬", "fall/winter": "秋冬", "spring/summer": "春夏",
            "fleece-lined": "加绒", "fur-lined": "加毛", "shearling-lined": "加毛绒",
            "faux fur": "仿皮草", "faux leather": "仿皮", "diamond-quilted": "菱格绗缝",
            "stone-washed": "石洗", "stone washed": "石洗", "distressed washed": "做旧水洗",
            "high-waisted": "高腰", "wide-leg": "阔腿", "straight-leg": "直筒",
            "slim-fit": "修身", "loose-fit": "宽松", "regular fit": "常规版型",
            "mid-top": "中帮", "high-top": "高帮", "low-top": "低帮",
            "ankle-length": "及踝", "knee-length": "及膝", "pointed-toe": "尖头",
            "round-toe": "圆头", "square-toe": "方头", "half-zip": "半拉链",
            "double-layer": "双层", "multi-layer": "多层", "laid-back": "休闲随性",
            "spaghetti strap": "细肩带", "v-neck": "V领", "turtleneck": "高领",
            "crew-neck": "圆领", "mock-neck": "半高领", "long-sleeve": "长袖",
            "short-sleeve": "短袖", "three-quarter": "七分",
            "color-block": "撞色", "color block": "撞色", "two-tone": "双色",
            "light-colored": "浅色系", "dark-colored": "深色系", "light-blue": "浅蓝",
            "navy blue": "藏蓝", "army green": "军绿", "olive green": "橄榄绿",
            "off-white": "米白", "all-white": "全白", "all-black": "全黑",
            "ribbed knit": "罗纹针织", "cable-knit": "绞花针织", "chunky knit": "粗针织",
            "fine-knit": "细针织", "soft-knit": "柔软针织", "jacquard knit": "提花针织",
            "leopard print": "豹纹", "floral print": "碎花", "animal print": "动物纹",
            "geometric print": "几何印花", "letter print": "字母印花",
            "heart print": "心形印花", "star print": "星星印花",
            "houndstooth": "千鸟格", "polka dot": "波点",
            "baseball cap": "棒球帽", "knit scarf": "针织围巾", "knit beanie": "针织帽",
            "ankle boots": "及踝靴", "combat boots": "工装靴", "chelsea boots": "切尔西靴",
            "platform sneakers": "厚底运动鞋", "platform shoes": "厚底鞋",
            "platform slides": "厚底凉拖", "ballet flats": "芭蕾平底鞋",
            "casual sneakers": "休闲运动鞋", "running shoes": "跑鞋",
            "german army trainers": "德式军训练鞋", "outdoor sandals": "户外凉鞋",
            "t-shirt": "T恤", "polo shirt": "Polo衫", "dress shirt": "衬衫",
            "button-down shirt": "纽扣衬衫", "long-sleeve shirt": "长袖衬衫",
            "short-sleeve shirt": "短袖衬衫", "hooded sweatshirt": "带帽卫衣",
            "knit sweater": "针织毛衣", "knit cardigan": "针织开衫", "knit vest": "针织马甲",
            "knit tank top": "针织背心", "tank top": "背心", "button-down": "纽扣",
            "shirt dress": "衬衫裙", "sweater dress": "毛衣连衣裙",
            "denim jacket": "牛仔外套", "leather jacket": "皮夹克",
            "trench coat": "风衣", "wool coat": "羊毛大衣", "maxi coat": "长大衣",
            "down jacket": "羽绒服", "puffer jacket": "羽绒服", "padded jacket": "棉服",
            "bomber jacket": "飞行员夹克", "varsity jacket": "棒球服",
            "cargo trousers": "工装长裤", "cargo pants": "工装裤",
            "skinny trousers": "修身长裤", "wide-leg trousers": "阔腿裤",
            "straight-leg jeans": "直筒牛仔裤", "distressed jeans": "破洞牛仔裤",
            "mini skirt": "迷你裙", "midi skirt": "中长裙", "pleated skirt": "百褶裙",
            "pencil skirt": "铅笔裙", "a-line skirt": "A字裙",
            "arc-shaped handbag": "弧形手提包", "shoulder bag": "单肩包",
            "tote bag": "托特包", "crossbody bag": "斜挎包",
            "american vintage": "美式复古", "french style": "法式风",
            "street wear": "街头风", "streetwear": "街头风",
        }
        
        # 单词级翻译
        self.word_cn = {
            # 颜色
            "black": "黑色", "white": "白色", "brown": "棕色", "gray": "灰色", "grey": "灰色",
            "blue": "蓝色", "beige": "米色", "red": "红色", "navy": "藏青", "tan": "棕褐色",
            "pink": "粉色", "burgundy": "酒红", "khaki": "卡其色", "green": "绿色",
            "yellow": "黄色", "orange": "橙色", "purple": "紫色", "teal": "青色",
            "camel": "驼色", "maroon": "栗色", "ivory": "象牙白", "cream": "奶油色",
            "taupe": "灰褐色", "olive": "橄榄色", "mint": "薄荷绿", "coral": "珊瑚色",
            "wheat": "小麦色", "mustard": "芥末黄", "wine": "酒红", "light": "浅",
            "dark": "深", "pale": "淡", "bright": "亮", "soft": "柔和", "neutral": "中性",
            
            # 品类
            "jacket": "外套", "coat": "大衣", "shirt": "衬衫", "top": "上衣",
            "sweater": "毛衣", "sweatshirt": "卫衣", "trousers": "长裤", "pants": "长裤",
            "jeans": "牛仔裤", "shorts": "短裤", "skirt": "半身裙", "dress": "连衣裙",
            "cardigan": "开衫", "vest": "马甲", "hoodie": "卫衣", "blazer": "西装外套",
            "blouse": "上衣", "tunic": "束腰外衣", "tank": "背心", "tee": "T恤",
            "jumpsuit": "连体裤", "onepiece": "连体衣", "anorak": "防寒大衣",
            "parka": "派克大衣", "overcoat": "大衣",
            "shoes": "鞋", "boots": "靴子", "sneakers": "运动鞋", "trainers": "运动鞋",
            "loafers": "乐福鞋", "flats": "平底鞋", "heels": "高跟鞋", "heel": "高跟鞋",
            "sandals": "凉鞋", "slides": "凉拖", "clogs": "木底鞋", "derby": "德比",
            "chelsea": "切尔西", "bag": "包包", "handbag": "手提包", "backpack": "双肩包",
            "cap": "帽子", "hat": "帽子", "beanie": "针织帽", "beret": "贝雷帽",
            "scarf": "围巾", "tie": "领带", "gloves": "手套", "socks": "袜子",
            "accessory": "配饰", "accessories": "配饰", "tote": "托特", "shoulder": "单肩",
            "crossbody": "斜挎", "outerwear": "外套",
            
            # 材质
            "knit": "针织", "denim": "牛仔", "leather": "皮", "suede": "麂皮",
            "corduroy": "灯芯绒", "wool": "羊毛", "cashmere": "羊绒", "fleece": "抓绒",
            "fur": "毛皮", "faux": "仿", "velvet": "丝绒", "satin": "缎面",
            "silk": "丝绸", "lace": "蕾丝", "canvas": "帆布", "tweed": "粗花呢",
            "linen": "亚麻", "cotton": "棉", "plush": "毛绒", "nylon": "尼龙",
            "polyester": "涤纶", "jacquard": "提花", "shearling": "毛绒",
            
            # 风格
            "casual": "休闲", "minimalist": "简约", "minimal": "极简", "vintage": "复古",
            "retro": "复古", "trendy": "潮流", "elegant": "优雅", "preppy": "学院",
            "sweet": "甜美", "cool": "酷感", "commuter": "通勤", "outdoor": "户外",
            "athletic": "运动", "sporty": "运动", "formal": "正装", "business": "商务",
            "street": "街头", "artistic": "艺术", "artsy": "艺术", "chic": "时髦",
            "fashion": "时尚", "stylish": "时尚", "basic": "基础款", "versatile": "百搭",
            "classic": "经典", "modern": "现代", "french": "法式", "korean": "韩系",
            "japanese": "日系", "chinese": "中式", "guochao": "国潮", "american": "美式",
            "british": "英式", "italian": "意式", "german": "德式", "refined": "精致",
            "luxury": "奢华", "handmade": "手工", "utilitarian": "工装", "utility": "工装",
            "military": "军旅", "army": "军旅", "workwear": "工装", "gentle": "温柔",
            "fresh": "清新", "cute": "可爱", "girlish": "少女", "youth": "青春",
            "mature": "成熟", "simple": "简约", "comfortable": "舒适",
            
            # 版型
            "fit": "版型", "slim": "修身", "loose": "宽松", "wide": "宽", "narrow": "窄",
            "high": "高", "low": "低", "long": "长", "short": "短", "mid": "中",
            "cropped": "短款", "oversized": "宽松oversize", "oversize": "宽松oversize",
            "regular": "常规", "skinny": "紧身", "curved": "弧形", "relaxed": "宽松",
            
            # 细节
            "neck": "领", "collar": "领", "collared": "带领", "hooded": "带帽",
            "hood": "帽", "sleeve": "袖", "sleeves": "袖", "sleeveless": "无袖",
            "strap": "肩带", "striped": "条纹", "plaid": "格纹", "check": "格纹",
            "pattern": "图案", "print": "印花", "printed": "印花", "solid": "纯色",
            "colorblock": "撞色", "block": "撞色", "color": "色", "colour": "色",
            "embroidered": "刺绣", "embroidery": "刺绣", "patchwork": "拼贴",
            "patch": "贴布", "patches": "贴布", "zipped": "拉链", "zip": "拉链",
            "zipper": "拉链", "buttoned": "纽扣", "button": "纽扣", "laced": "系带",
            "buckled": "搭扣", "belted": "系带", "tied": "系带", "pleated": "百褶",
            "ruched": "抽褶", "fringe": "流苏", "ruffle": "荷叶边", "asymmetric": "不对称",
            "layered": "层叠", "double": "双", "single": "单", "half": "半",
            "detail": "细节", "details": "细节", "contrast": "撞色", "trim": "镶边",
            "charm": "挂饰", "decorative": "装饰", "embellished": "装饰",
            
            # 季节
            "autumn": "秋", "fall": "秋", "winter": "冬", "spring": "春", "summer": "夏",
            
            # 其他
            "basic": "基础款", "premium": "高级", "versatile": "百搭", "trendy": "潮流",
            "comfortable": "舒适", "warm": "保暖", "thick": "厚", "thin": "薄",
            "padded": "夹棉", "lined": "里衬", "quilted": "绗缝", "washed": "水洗",
            "distressed": "做旧", "vintage": "复古", "retro": "复古",
            "textured": "纹理", "cutout": "镂空", "cut-out": "镂空",
            "multi-pocket": "多口袋", "multi-pocket": "多口袋",
            "metal": "金属", "logo": "logo", "hardware": "配件",
        }
    
    def translate(self, text: str, lang: str = 'cn', text_type: str = 'general') -> str:
        """翻译入口"""
        if lang != 'cn' or not text:
            return text
        
        result = text
        
        # 1. 按长度排序的短语匹配
        sorted_phrases = sorted(self.phrase_cn.keys(), key=len, reverse=True)
        
        placeholders = {}
        counter = [0]
        
        def mark_translated(match):
            idx = counter[0]
            counter[0] += 1
            original_phrase = match.group(0)
            for p in sorted_phrases:
                if p.lower() == original_phrase.lower():
                    placeholders[f"__PH{idx}__"] = self.phrase_cn[p]
                    return f"__PH{idx}__"
            return original_phrase
        
        for phrase in sorted_phrases:
            pattern = r'(?<![a-zA-Z])' + re.escape(phrase) + r'(?![a-zA-Z])'
            result = re.sub(pattern, mark_translated, result, flags=re.IGNORECASE)
        
        # 2. 单词级翻译
        words = re.split(r'(\s+|/|,|\.|\(|\)|\'|")', result)
        translated_parts = []
        
        for w in words:
            w_lower = w.lower().strip()
            if w.startswith("__PH") and w.endswith("__"):
                translated_parts.append(w)
                continue
            if w.strip() in ['/', ',', '.', '(', ')', '"', "'"] or w.isspace() or w == '':
                translated_parts.append(w)
                continue
            if '-' in w_lower and len(w_lower) > 3:
                parts = w_lower.split('-')
                all_translated = True
                translated_subparts = []
                for p in parts:
                    if p in self.word_cn:
                        translated_subparts.append(self.word_cn[p])
                    else:
                        all_translated = False
                        break
                if all_translated:
                    translated_parts.append(''.join(translated_subparts))
                    continue
            if w_lower in self.word_cn:
                cn = self.word_cn[w_lower]
                if cn:
                    translated_parts.append(cn)
            else:
                translated_parts.append(w)
        
        result = ''.join(translated_parts)
        
        # 3. 替换占位符
        for ph, value in placeholders.items():
            result = result.replace(ph, value)
        
        # 4. 清理
        result = re.sub(r'([\u4e00-\u9fff])\s+(?=[\u4e00-\u9fff])', r'\1', result)
        result = re.sub(r'\s+', ' ', result).strip()
        
        return result


# ======================= 2. 风格提取模块 =======================

class StyleExtractor:
    """从 style 字段中提取纯风格标签"""
    
    # 纯风格关键词 -> 中文显示
    STYLE_KEYWORDS = {
        # 英文风格词
        "casual": "休闲",
        "minimalist": "简约",
        "minimal": "简约",
        "vintage": "复古",
        "retro": "复古",
        "trendy": "潮流",
        "fashion": "时尚",
        "stylish": "时尚",
        "elegant": "优雅",
        "preppy": "学院",
        "sweet": "甜美",
        "cool": "酷感",
        "commuter": "通勤",
        "business": "商务",
        "outdoor": "户外",
        "sporty": "运动",
        "athletic": "运动",
        "formal": "正装",
        "street": "街头",
        "streetwear": "街头",
        "artistic": "艺术",
        "chic": "时髦",
        "classic": "经典",
        "modern": "现代",
        "youth": "青春",
        "mature": "成熟",
        "simple": "简约",
        "comfortable": "舒适",
        "versatile": "百搭",
        "basic": "基础",
        "gentle": "温柔",
        "fresh": "清新",
        "cute": "可爱",
        
        # 国家/地区风格
        "american": "美式",
        "british": "英伦",
        "english": "英式",
        "french": "法式",
        "italian": "意式",
        "german": "德式",
        "korean": "韩系",
        "japanese": "日系",
        "chinese": "中式",
        "guochao": "国潮",
        "nordic": "北欧",
        
        # 材质/特殊风格
        "denim": "牛仔",
        "leather": "皮革",
        "knit": "针织",
        "wool": "羊毛",
        "workwear": "工装",
        "utility": "工装",
        "military": "军旅",
        "army": "军旅",
    }
    
    # 预定义的纯风格列表（用于UI选择）
    PURE_STYLES_CN = [
        "不限",
        "休闲", "简约", "复古", "潮流", "时尚",
        "优雅", "学院", "甜美", "酷感", "通勤",
        "商务", "户外", "运动", "正装", "街头",
        "艺术", "经典", "青春", "成熟", "温柔",
        "清新", "可爱", "时髦", "百搭", "舒适",
        "美式", "英伦", "法式", "意式", "德式",
        "韩系", "日系", "中式", "国潮", "北欧",
        "牛仔", "皮革", "针织", "工装", "军旅",
    ]
    
    # 预定义的纯风格列表（英文显示）
    PURE_STYLES_EN = [
        "Any",
        "Casual", "Minimalist", "Vintage", "Trendy", "Fashion",
        "Elegant", "Preppy", "Sweet", "Cool", "Commuter",
        "Business", "Outdoor", "Sporty", "Formal", "Street",
        "Artistic", "Classic", "Youth", "Mature", "Gentle",
        "Fresh", "Cute", "Chic", "Versatile", "Comfortable",
        "American", "British", "French", "Italian", "German",
        "Korean", "Japanese", "Chinese", "Guochao", "Nordic",
        "Denim", "Leather", "Knit", "Utility", "Military",
    ]
    
    @classmethod
    def extract_style(cls, style_text: str) -> List[str]:
        """从 style 文本中提取风格关键词"""
        if not style_text or not isinstance(style_text, str):
            return []
        
        text_lower = style_text.lower()
        styles = []
        
        for keyword, cn_name in cls.STYLE_KEYWORDS.items():
            if keyword in text_lower:
                if cn_name not in styles:
                    styles.append(cn_name)
        
        return styles
    
    @classmethod
    def get_style_for_display(cls, style_text: str, lang: str = 'cn') -> str:
        """将 style 字段转为纯风格显示"""
        styles = cls.extract_style(style_text)
        if not styles:
            return "其他" if lang == 'cn' else "Others"
        return "、".join(styles) if lang == 'cn' else "/".join(styles)
    
    @classmethod
    def match_style_tag(cls, style_text: str, style_tag: str) -> bool:
        """检查 style_text 是否包含指定风格标签"""
        if not style_text or not style_tag:
            return True
        if style_tag in ["不限", "Any", "any", ""]:
            return True
        
        styles = cls.extract_style(style_text)
        # 同时检查中英文
        tag_lower = style_tag.lower()
        text_lower = str(style_text).lower()
        
        # 检查中文匹配
        if style_tag in styles:
            return True
        # 检查英文匹配
        for en_word, cn_word in cls.STYLE_KEYWORDS.items():
            if en_word in tag_lower or cn_word == style_tag:
                if en_word in text_lower:
                    return True
        return False


# ======================= 3. 数据加载模块 =======================

class DataLoader:
    """加载与管理衣物数据"""
    
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.translator = FashionTranslator()
        self.style_extractor = StyleExtractor()
        self.label_df = None
        self.look_df = None
        self.weather_df = None
        self.ratings_df = None
        self._load_all()
    
    def _load_all(self):
        try:
            # 优先尝试 xlsx（项目数据格式）
            male_label_path = os.path.join(self.data_dir, 'male', 'label_male.xlsx')
            female_label_path = os.path.join(self.data_dir, 'female', 'label_female.xlsx')
            child_label_path = os.path.join(self.data_dir, 'child', 'label_child.xlsx')
            
            if os.path.exists(male_label_path):
                # 使用多线程并行加载数据
                start_time = time.time()
                
                def load_gender_data(gender, path):
                    if os.path.exists(path):
                        df = pd.read_excel(path)
                        df['gender'] = gender
                        return df
                    return None
                
                # 并行加载三个性别数据
                with ThreadPoolExecutor(max_workers=3) as executor:
                    futures = {
                        executor.submit(load_gender_data, '男', male_label_path): 'male',
                        executor.submit(load_gender_data, '女', female_label_path): 'female',
                        executor.submit(load_gender_data, '童', child_label_path): 'child'
                    }
                    
                    dfs = []
                    for future in as_completed(futures):
                        result = future.result()
                        if result is not None:
                            dfs.append(result)
                
                self.label_df = pd.concat(dfs, ignore_index=True)
                print(f"✓ 数据加载完成（并行加载耗时: {time.time() - start_time:.2f}s）")
                
                # 清洗label数据
                self.label_df = self.label_df.dropna(subset=['itemID', 'category', 'title'])
                self.label_df = self.label_df[self.label_df['itemID'].astype(str).str.strip() != '']
                self.label_df = self.label_df[self.label_df['category'].astype(str).str.strip() != '']
                for col in ['itemID', 'category', 'title', 'style']:
                    if col in self.label_df.columns:
                        self.label_df[col] = self.label_df[col].astype(str).str.strip()
                
                # 加载 look 数据
                male_look_path = os.path.join(self.data_dir, 'male', 'look_male.xlsx')
                if os.path.exists(male_look_path):
                    male_look = pd.read_excel(male_look_path)
                    female_look = pd.read_excel(os.path.join(self.data_dir, 'female', 'look_female.xlsx'))
                    child_look = pd.read_excel(os.path.join(self.data_dir, 'child', 'look_child.xlsx'))
                    self.look_df = pd.concat([male_look, female_look, child_look], ignore_index=True)
                
                # 加载天气数据
                weather_path = os.path.join(self.data_dir, 'weather_data.xlsx')
                if os.path.exists(weather_path):
                    self.weather_df = pd.read_excel(weather_path)
                
                # 尝试 ratings
                ratings_path = os.path.join(self.data_dir, 'ratings.csv')
                if os.path.exists(ratings_path):
                    self.ratings_df = pd.read_csv(ratings_path)
                else:
                    self.ratings_df = pd.DataFrame(columns=[
                        'timestamp', 'recommendation_type', 'rating', 'feedback', 'items'
                    ])
            else:
                # 回退到 csv 格式
                if os.path.exists(os.path.join(self.data_dir, 'label_df.csv')):
                    self.label_df = pd.read_csv(os.path.join(self.data_dir, 'label_df.csv'))
                if os.path.exists(os.path.join(self.data_dir, 'look_df.csv')):
                    self.look_df = pd.read_csv(os.path.join(self.data_dir, 'look_df.csv'))
                if os.path.exists(os.path.join(self.data_dir, 'weather_df.csv')):
                    self.weather_df = pd.read_csv(os.path.join(self.data_dir, 'weather_df.csv'))
                
                ratings_path = os.path.join(self.data_dir, 'ratings.csv')
                if os.path.exists(ratings_path):
                    self.ratings_df = pd.read_csv(ratings_path)
                else:
                    self.ratings_df = pd.DataFrame(columns=[
                        'timestamp', 'recommendation_type', 'rating', 'feedback', 'items'
                    ])
        except Exception as e:
            print(f"加载数据时出错: {e}")
            import traceback
            traceback.print_exc()
    
    def get_items_by_gender(self, gender: str) -> pd.DataFrame:
        """按性别筛选衣物"""
        if self.label_df is None:
            return pd.DataFrame()
        # 数据集中 gender 为中文：男/女/童
        df = self.label_df[self.label_df['gender'] == gender].copy()
        return df.reset_index(drop=True)
    
    def search_items(self, query: str, gender: str, lang: str = 'cn') -> List[Dict]:
        """根据用户输入关键词搜索衣物（模糊匹配 title 和 style）"""
        df = self.get_items_by_gender(gender)
        if df.empty or not query:
            return []
        
        query = str(query).strip().lower()
        if not query:
            return []
        
        results = []
        seen_ids = set()
        
        for _, row in df.iterrows():
            item_id = str(row.get('itemID', ''))
            if item_id in seen_ids:
                continue
            
            title = str(row.get('title', ''))
            style = str(row.get('style', ''))
            
            # 中英文混合搜索
            text_to_search = (title + " " + style).lower()
            
            # 尝试翻译后搜索
            translated_title = self.translator.translate(title, 'cn', 'title')
            translated_style = self.style_extractor.get_style_for_display(style, 'cn')
            
            # 检查是否匹配
            match = False
            if query in text_to_search:
                match = True
            elif query in translated_title.lower() or query in translated_style.lower():
                match = True
            else:
                # 分词匹配
                query_parts = [q for q in query.split() if q]
                if query_parts:
                    title_lower = title.lower()
                    style_lower = style.lower()
                    match_all = True
                    for qp in query_parts:
                        if qp not in title_lower and qp not in style_lower:
                            # 尝试中文关键词匹配
                            found_in_cn = False
                            for kw, cn in self.style_extractor.STYLE_KEYWORDS.items():
                                if qp == cn.lower() or qp in cn:
                                    if kw in style_lower:
                                        found_in_cn = True
                                        break
                            if not found_in_cn:
                                match_all = False
                                break
                    match = match_all
            
            if match:
                title_cn = translated_title if lang == 'cn' else title
                style_cn = translated_style if lang == 'cn' else style
                results.append({
                    'itemID': item_id,
                    'title': title_cn,
                    'title_en': title,
                    'style': style_cn,
                    'style_en': style,
                    'category': str(row.get('category', '')),
                    'season': int(row.get('season', 1)),
                    'thick': int(row.get('thick', 1)),
                    'gender': str(row.get('gender', gender)),
                })
                seen_ids.add(item_id)
                if len(results) >= 20:
                    break
        
        return results
    
    def get_item_by_id(self, item_id: str, lang: str = 'cn', gender: str = None) -> Optional[Dict]:
        """根据 itemID 获取衣物信息（可选按性别筛选）"""
        if self.label_df is None:
            return None
        rows = self.label_df[self.label_df['itemID'].astype(str) == str(item_id)]
        if rows.empty:
            return None
        if gender is not None:
            gender_rows = rows[rows['gender'] == gender]
            if not gender_rows.empty:
                rows = gender_rows
        row = rows.iloc[0]
        title = str(row.get('title', ''))
        style = str(row.get('style', ''))
        return {
            'itemID': str(row.get('itemID', '')),
            'title': self.translator.translate(title, lang, 'title') if lang == 'cn' else title,
            'title_en': title,
            'style': self.style_extractor.get_style_for_display(style, lang) if lang == 'cn' else style,
            'style_en': style,
            'category': str(row.get('category', '')),
            'season': int(row.get('season', 1)),
            'thick': int(row.get('thick', 1)),
            'gender': str(row.get('gender', '')),
        }


# ======================= 4. 天气推荐引擎 =======================

class WeatherRecommender:
    """基于天气的穿搭推荐"""
    
    CN_CATEGORY = {
        'inner_top': '内搭', 'mid_layer_top': '中层上衣', 'outerwear': '外套',
        'bottom': '下装', 'shoes': '鞋履', 'accessory': '配饰',
        'bag': '包包', 'onepiece': '连体衣'
    }
    
    CN_WEATHER = {
        'sunny': '晴天', 'cloudy': '多云', 'windy': '大风', 'rainy': '雨天',
        'thunderstorm': '雷暴', 'snowy': '雪天', 'foggy': '雾天', 'hazy': '霾天'
    }
    
    CN_SEASON = {0: '夏季', 1: '春秋', 2: '冬季'}
    CN_THICK = {0: '薄款', 1: '中等厚度', 2: '厚款'}
    
    CN_TIPS = {
        'heat': '建议多喝水，避免长时间户外活动',
        'cold': '建议添加保暖衣物，注意手脚保暖',
        'uv': '紫外线较强，建议涂抹防晒霜，佩戴遮阳帽',
        'rain': '建议携带雨具，避免衣物被淋湿',
        'wind': '风较大时，建议穿着防风外套',
        'humid': '空气较潮湿，注意衣物防潮',
        'hot_color': '气温较高，建议穿着浅色系衣物',
        'cold_layer': '气温较低，建议叠穿保暖',
        'nice': '今日天气宜人，适合轻装出行'
    }
    
    CN_REASONS = {
        'outerwear': {0: '轻薄透气', 1: '轻薄适中', 2: '保暖防寒'},
        'inner_top': {0: '透气吸汗', 1: '舒适贴身', 2: '保暖舒适'},
        'mid_layer_top': {0: '防晒薄款', 1: '适中厚度', 2: '加绒保暖'},
        'bottom': {0: '轻薄透气', 1: '舒适休闲', 2: '加绒保暖'},
        'shoes': {0: '透气舒适', 1: '日常休闲', 2: '保暖防滑'},
        'accessory': {0: '遮阳防晒', 1: '搭配点缀', 2: '保暖防寒'}
    }
    
    def __init__(self, label_df: pd.DataFrame, look_df: pd.DataFrame = None, weather_df: pd.DataFrame = None):
        self.label_df = label_df
        self.look_df = look_df
        self.weather_df = weather_df
        self.translator = FashionTranslator()
        self.style_extractor = StyleExtractor()
        self.item_info = {}
        self.items_by_category_gender = {}  # 优化：按类别+性别索引
        self._build_index()
    
    def _build_index(self):
        """构建衣物索引（使用预计算优化）"""
        if self.label_df is None:
            return
        
        # 尝试使用性能优化模块
        try:
            from performance_optimizer import optimize_recommendation_system, build_category_index
            self.item_info = optimize_recommendation_system(os.path.dirname(os.path.abspath(__file__)), 
                                                           self.label_df, self.translator, self.style_extractor)
            self.items_by_category_gender = build_category_index(self.item_info)
            print("✓ 使用性能优化模块")
            return
        except ImportError:
            pass
        
        # 回退到原始实现
        for _, row in self.label_df.iterrows():
            item_id = str(row['itemID']).strip()
            gender = str(row.get('gender', '')).strip()
            composite_key = f"{item_id}_{gender}" if gender else item_id
            
            # 预计算翻译和风格
            title = str(row['title'])
            title_cn = self.translator.translate(title, 'cn', 'title')
            style = str(row.get('style', ''))
            style_cn = self.style_extractor.get_style_for_display(style, 'cn')
            
            info = {
                'itemID': item_id,
                'category': str(row['category']),
                'title': title,
                'title_cn': title_cn,  # 预计算
                'style': style,
                'style_cn': style_cn,  # 预计算
                'season': int(row.get('season', 1)),
                'thick': int(row.get('thick', 1)),
                'gender': gender,
            }
            self.item_info[composite_key] = info
            
            # 构建类别+性别索引
            cat = info['category']
            g = info['gender']
            if cat not in self.items_by_category_gender:
                self.items_by_category_gender[cat] = {}
            if g not in self.items_by_category_gender[cat]:
                self.items_by_category_gender[cat][g] = []
            self.items_by_category_gender[cat][g].append(info)
    
    def recommend(self, temperature: float, humidity: float = 60,
                 uv_index: int = 5, weather_condition: str = 'cloudy',
                 gender: str = '女', style_tag: Optional[str] = None,
                 lang: str = 'cn') -> Dict:
        """核心推荐函数"""
        
        # 1. 天气分析
        needs = []
        if temperature >= 30:
            needs.append('heat_protection')
        elif temperature <= 5:
            needs.append('warm_protection')
        if humidity >= 80:
            needs.append('humidity_control')
        if uv_index >= 6:
            needs.append('uv_protection')
        if weather_condition in ['rainy', 'rain', 'thunderstorm']:
            needs.append('rain_protection')
        if weather_condition == 'windy' or (temperature <= 15 and weather_condition == 'cloudy'):
            needs.append('wind_protection')
        if weather_condition == 'snowy':
            needs.append('snow_protection')
        
        # 2. 确定目标季节厚度
        target_season = 0 if temperature >= 25 else (2 if temperature <= 10 else 1)
        target_thick = 0 if temperature >= 28 else (2 if temperature <= 8 else 1)
        if weather_condition == 'windy':
            target_thick = 2
        
        # 3. 选择穿搭（使用预计算的索引）
        outfit = {}
        if target_season == 0:
            priority_categories = ['inner_top', 'bottom', 'shoes', 'accessory']
        elif target_season == 2:
            priority_categories = ['outerwear', 'mid_layer_top', 'inner_top', 'bottom', 'shoes', 'accessory']
        else:
            priority_categories = ['mid_layer_top', 'inner_top', 'bottom', 'shoes', 'accessory']
        
        if 'rain_protection' in needs and 'outerwear' not in priority_categories:
            priority_categories.insert(0, 'outerwear')
        
        for cat in priority_categories:
            # 使用预计算的类别+性别索引，直接获取符合条件的衣物
            if cat not in self.items_by_category_gender:
                continue
            if gender not in self.items_by_category_gender[cat]:
                continue
            
            candidates = self.items_by_category_gender[cat][gender]
            
            # 按风格筛选
            if style_tag and style_tag not in ['不限', 'Any', 'any', '']:
                filtered = [c for c in candidates
                           if self.style_extractor.match_style_tag(c.get('style', ''), style_tag)]
                if filtered:
                    candidates = filtered
            
            # 按季节/厚度排序
            candidates_sorted = sorted(candidates,
                                     key=lambda x: (
                                         abs(int(x.get('season', 1)) - target_season),
                                         abs(int(x.get('thick', 1)) - target_thick)
                                     ))
            
            if candidates_sorted:
                best = candidates_sorted[0]
                cat_cn = self.CN_CATEGORY.get(cat, cat) if lang == 'cn' else cat.replace('_', ' ').title()
                
                # 使用预计算的翻译结果
                if lang == 'cn':
                    title = best.get('title_cn', best['title'])
                    style = best.get('style_cn', best.get('style', ''))
                else:
                    title = best['title']
                    style = best.get('style', '')
                
                # 选择理由
                reason_map = self.CN_REASONS if lang == 'cn' else {
                    'outerwear': {0: 'Light & Breathable', 1: 'Light & Moderate', 2: 'Warm & Windproof'},
                    'inner_top': {0: 'Breathable', 1: 'Comfortable', 2: 'Warm & Comfortable'},
                    'mid_layer_top': {0: 'UV Protection', 1: 'Moderate', 2: 'Fleece Lined'},
                    'bottom': {0: 'Light & Breathable', 1: 'Casual', 2: 'Fleece Lined'},
                    'shoes': {0: 'Breathable', 1: 'Daily', 2: 'Warm & Anti-slip'},
                    'accessory': {0: 'Sun Protection', 1: 'Accessory', 2: 'Warmth'},
                }
                base_reason = reason_map.get(cat, {}).get(target_season, '')
                if lang == 'cn':
                    if 'uv_protection' in needs and cat in ['accessory', 'outerwear']:
                        base_reason += '，防晒功能'
                    if 'rain_protection' in needs and cat == 'outerwear':
                        base_reason += '，防雨功能'
                    if 'wind_protection' in needs and cat in ['outerwear', 'shoes']:
                        base_reason += '，防风设计'
                
                outfit[cat_cn] = {
                    'itemID': best['itemID'],
                    'title': title,
                    'title_en': best['title'],
                    'category': cat_cn,
                    'category_en': cat,
                    'style': style,
                    'style_en': best.get('style', ''),
                    'reason': base_reason,
                    'season': best.get('season', 1),
                    'thick': best.get('thick', 1),
                }
        
        # 4. 生成小贴士
        tips = []
        if lang == 'cn':
            tips_map = self.CN_TIPS
            needs_cn_map = {
                'heat_protection': ('防暑', tips_map['heat']),
                'warm_protection': ('保暖', tips_map['cold']),
                'uv_protection': ('防晒', tips_map['uv']),
                'rain_protection': ('防雨', tips_map['rain']),
                'wind_protection': ('防风', tips_map['wind']),
                'snow_protection': ('防雪', tips_map['cold']),
                'humidity_control': ('除湿', tips_map['humid']),
            }
            for need in needs:
                if need in needs_cn_map:
                    tips.append(needs_cn_map[need][1])
            if temperature >= 25:
                tips.append(tips_map['hot_color'])
            elif temperature <= 10:
                tips.append(tips_map['cold_layer'])
            if not tips:
                tips.append(tips_map['nice'])
        else:
            en_tips = {
                'heat': 'Drink more water, avoid long outdoor activities',
                'cold': 'Add warm clothing, keep hands and feet warm',
                'uv': 'UV is strong, apply sunscreen and wear a sun hat',
                'rain': 'Bring rain gear to avoid getting wet',
                'wind': 'It\'s windy, wear windproof outerwear',
                'humid': 'Air is humid, keep clothing dry',
                'hot_color': 'Temperature is high, wear light-colored clothing',
                'cold_layer': 'Temperature is low, layer up for warmth',
                'nice': 'Weather is nice today, suitable for light clothing'
            }
            need_keys_map = {
                'heat_protection': 'heat', 'warm_protection': 'cold',
                'uv_protection': 'uv', 'rain_protection': 'rain',
                'wind_protection': 'wind', 'snow_protection': 'cold',
                'humidity_control': 'humid',
            }
            for need in needs:
                if need in need_keys_map:
                    tips.append(en_tips[need_keys_map[need]])
            if temperature >= 25:
                tips.append(en_tips['hot_color'])
            elif temperature <= 10:
                tips.append(en_tips['cold_layer'])
            if not tips:
                tips.append(en_tips['nice'])
        
        season_display = self.CN_SEASON.get(target_season, '春秋') if lang == 'cn' else \
            ['Summer', 'Spring/Autumn', 'Winter'][target_season]
        thick_display = self.CN_THICK.get(target_thick, '中等厚度') if lang == 'cn' else \
            ['Thin', 'Medium', 'Thick'][target_thick]
        
        return {
            'weather_analysis': {
                'temperature': temperature,
                'humidity': humidity,
                'uv_index': uv_index,
                'weather_condition': weather_condition,
                'needs': needs,
            },
            'target_season': season_display,
            'target_thick': thick_display,
            'outfit': outfit,
            'tips': tips,
            'lang': lang,
        }


# ======================= 5. 衣物推荐引擎 =======================

class ClothingBasedRecommender:
    """基于已有衣物的穿搭推荐"""
    
    CN_CATEGORY = {
        'inner_top': '内搭', 'mid_layer_top': '中层上衣', 'outerwear': '外套',
        'bottom': '下装', 'shoes': '鞋履', 'accessory': '配饰',
        'bag': '包包', 'onepiece': '连体衣'
    }
    
    def __init__(self, label_df: pd.DataFrame, look_df: pd.DataFrame = None):
        self.label_df = label_df
        self.look_df = look_df
        self.translator = FashionTranslator()
        self.style_extractor = StyleExtractor()
        self.item_info = {}
        self.items_by_category = {}
        self._build_index()
    
    def _build_index(self):
        if self.label_df is None:
            return
        for _, row in self.label_df.iterrows():
            item_id = str(row['itemID']).strip()
            gender = str(row.get('gender', '')).strip()
            composite_key = f"{item_id}_{gender}" if gender else item_id
            
            self.item_info[composite_key] = {
                'itemID': item_id,
                'category': str(row['category']),
                'title': str(row['title']),
                'style': str(row.get('style', '')),
                'season': int(row.get('season', 1)),
                'thick': int(row.get('thick', 1)),
                'gender': gender,
            }
            cat = str(row['category'])
            if cat not in self.items_by_category:
                self.items_by_category[cat] = []
            self.items_by_category[cat].append(self.item_info[composite_key])
    
    def recommend(self, owned_item_ids: List[str], gender: str,
                  style_tag: Optional[str] = None, lang: str = 'cn') -> Dict:
        """基于已有衣物推荐完整穿搭"""
        
        owned_items_detail = []
        owned_categories = set()
        season_sum = 0
        thick_sum = 0
        
        cat_map = self.CN_CATEGORY if lang == 'cn' else {
            'inner_top': 'Inner Top', 'mid_layer_top': 'Mid-layer Top',
            'outerwear': 'Outerwear', 'bottom': 'Bottom', 'shoes': 'Shoes',
            'accessory': 'Accessory', 'bag': 'Bag', 'onepiece': 'One-piece'
        }
        
        # 分析已有衣物
        for item_id in owned_item_ids:
            composite_key = f"{item_id}_{gender}"
            if composite_key in self.item_info:
                info = self.item_info[composite_key]
                owned_categories.add(info['category'])
                title = info['title']
                style = info['style']
                if lang == 'cn':
                    title = self.translator.translate(title, 'cn', 'title')
                    style = self.style_extractor.get_style_for_display(style, 'cn')
                
                owned_items_detail.append({
                    'itemID': info['itemID'],
                    'title': title,
                    'title_en': info['title'],
                    'category': info['category'],
                    'category_cn': cat_map.get(info['category'], info['category']),
                    'style': style,
                    'style_en': info['style'],
                    'season': info.get('season', 1),
                    'thick': info.get('thick', 1),
                })
                season_sum += int(info.get('season', 1))
                thick_sum += int(info.get('thick', 1))
        
        count = len(owned_items_detail) if owned_items_detail else 1
        avg_season = round(season_sum / count)
        avg_thick = round(thick_sum / count)
        
        # 确定缺失品类
        essential = ['inner_top', 'bottom', 'shoes']
        optional = ['outerwear', 'mid_layer_top', 'accessory']
        missing = []
        for cat in essential:
            if cat not in owned_categories:
                missing.append(cat)
        for cat in optional:
            if cat not in owned_categories:
                missing.append(cat)
        
        # 为缺失品类推荐
        suggestions = {}
        gender_items = {}
        for cat, items in self.items_by_category.items():
            gender_items[cat] = [i for i in items if i.get('gender') == gender]
        
        for cat in missing:
            if cat not in gender_items or not gender_items[cat]:
                continue
            
            candidates = gender_items[cat]
            
            # 风格筛选
            if style_tag and style_tag not in ['不限', 'Any', 'any', '']:
                filtered = [c for c in candidates
                           if self.style_extractor.match_style_tag(c.get('style', ''), style_tag)]
                if filtered:
                    candidates = filtered
            
            # 按匹配度排序
            candidates_sorted = sorted(candidates,
                                     key=lambda x: (
                                         abs(int(x.get('season', 1)) - avg_season),
                                         abs(int(x.get('thick', 1)) - avg_thick)
                                     ))
            
            items_list = []
            for c in candidates_sorted[:5]:
                title = c['title']
                style = c.get('style', '')
                if lang == 'cn':
                    title = self.translator.translate(title, 'cn', 'title')
                    style = self.style_extractor.get_style_for_display(style, 'cn')
                
                match_reason = (f"与您的整体风格相匹配" if lang == 'cn'
                              else f"Matches your overall style")
                
                items_list.append({
                    'itemID': c['itemID'],
                    'title': title,
                    'title_en': c['title'],
                    'style': style,
                    'style_en': c.get('style', ''),
                    'category': cat,
                    'category_cn': cat_map.get(cat, cat),
                    'match_reason': match_reason,
                })
            
            suggestions[cat] = items_list
        
        # 构建完整穿搭
        outfit_owned = []
        for item in owned_items_detail:
            outfit_owned.append({
                'title': item['title'],
                'title_en': item['title_en'],
                'category': item['category'],
                'category_cn': item['category_cn'],
                'style': item['style'],
                'style_en': item['style_en'],
                'source': '已有' if lang == 'cn' else 'Owned',
            })
        
        outfit_recommended = []
        for cat, items in suggestions.items():
            if items:
                best = items[0]
                outfit_recommended.append({
                    'title': best['title'],
                    'title_en': best['title_en'],
                    'category': best['category'],
                    'category_cn': best['category_cn'],
                    'style': best['style'],
                    'style_en': best['style_en'],
                    'source': '推荐' if lang == 'cn' else 'Recommended',
                })
        
        # 缺失品类中文显示
        missing_cn = [cat_map.get(cat, cat) for cat in missing]
        
        # 穿搭提示
        tips = []
        if lang == 'cn':
            if len(owned_items_detail) == 0:
                tips.append('您还没有添加任何衣物，请先搜索并添加您的衣物')
            elif len(owned_items_detail) < 2:
                tips.append('您的衣物种类较少，建议补充更多基础品类')
            if 'outerwear' in missing:
                tips.append('建议添加一件外套，应对天气变化')
            if 'shoes' in missing:
                tips.append('建议添加一双合适的鞋子')
            if 'accessory' in missing:
                tips.append('配饰可以提升整体穿搭效果')
            if not tips:
                tips.append('您的衣物搭配已经比较完整')
        else:
            if len(owned_items_detail) == 0:
                tips.append('You haven\'t added any clothing yet')
            elif len(owned_items_detail) < 2:
                tips.append('You have fewer clothing categories, consider adding more')
            if 'outerwear' in missing:
                tips.append('Consider adding a jacket for weather changes')
            if 'shoes' in missing:
                tips.append('Consider adding a pair of suitable shoes')
            if 'accessory' in missing:
                tips.append('Accessories can enhance your outfit')
            if not tips:
                tips.append('Your outfit is already complete')
        
        return {
            'analysis': {
                'items': owned_items_detail,
                'categories': list(owned_categories),
                'avg_season': avg_season,
                'avg_thick': avg_thick,
                'category_count': len(owned_items_detail),
            },
            'missing_categories': missing,
            'missing_categories_cn': missing_cn,
            'suggestions': suggestions,
            'complete_outfit': {
                'owned': outfit_owned,
                'recommended': outfit_recommended,
            },
            'outfit_tips': tips,
            'lang': lang,
        }


# ======================= 6. 评分管理模块 =======================

class RatingManager:
    """管理用户对推荐结果的评分"""
    
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.ratings_path = os.path.join(data_dir, 'ratings.csv')
        self.ratings_df = self._load_ratings()
    
    def _load_ratings(self) -> pd.DataFrame:
        if os.path.exists(self.ratings_path):
            try:
                df = pd.read_csv(self.ratings_path)
                # 确保 rating 列是数值类型
                if 'rating' in df.columns:
                    df['rating'] = pd.to_numeric(df['rating'], errors='coerce').fillna(0).astype(int)
                return df
            except Exception:
                pass
        return pd.DataFrame(columns=['timestamp', 'recommendation_type', 'rating', 'feedback', 'items'])
    
    def add_rating(self, recommendation_type: str, rating: int,
                   feedback: str = "", items: Optional[List[str]] = None) -> bool:
        """添加一条评分记录
        
        Args:
            recommendation_type: 'weather' 或 'clothing'
            rating: 0-5 的整数评分
            feedback: 用户文字反馈
            items: 推荐的衣物ID列表
        """
        try:
            rating = int(rating)
            rating = max(0, min(5, rating))  # 限制在0-5之间
            
            from datetime import datetime
            new_row = {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'recommendation_type': recommendation_type,
                'rating': rating,
                'feedback': str(feedback) if feedback else '',
                'items': ','.join(items) if items else '',
            }
            
            new_df = pd.DataFrame([new_row])
            self.ratings_df = pd.concat([self.ratings_df, new_df], ignore_index=True)
            
            # 保存到文件
            try:
                self.ratings_df.to_csv(self.ratings_path, index=False, encoding='utf-8-sig')
            except Exception as e:
                print(f"保存评分文件时出错: {e}")
            
            return True
        except Exception as e:
            print(f"添加评分时出错: {e}")
            return False
    
    def get_statistics(self) -> Dict:
        """获取评分统计"""
        if self.ratings_df.empty:
            return {'count': 0, 'avg_rating': 0, 'distribution': {}}
        
        # 确保 rating 列是数值类型
        ratings = pd.to_numeric(self.ratings_df['rating'], errors='coerce').fillna(0)
        
        count = len(self.ratings_df)
        avg_rating = round(ratings.mean(), 2)
        
        distribution = {}
        for i in range(6):
            distribution[str(i)] = int((ratings == i).sum())
        
        # 按类型分组统计
        by_type = {}
        try:
            by_type = self.ratings_df.groupby('recommendation_type')['rating'].apply(
                lambda x: round(pd.to_numeric(x, errors='coerce').fillna(0).mean(), 2)
            ).to_dict()
        except Exception:
            by_type = {}
        
        return {
            'count': int(count),
            'avg_rating': float(avg_rating),
            'distribution': distribution,
            'by_type': by_type,
        }


# ======================= 7. 便捷入口函数 =======================

def create_system(data_dir: str) -> Dict:
    """创建完整的推荐系统实例"""
    loader = DataLoader(data_dir)
    translator = FashionTranslator()
    style_extractor = StyleExtractor()
    
    # 导入数据库管理器（使用try-except处理导入）
    db_manager = None
    try:
        # 确保src目录在sys.path中
        if 'src' not in sys.path and os.path.join(data_dir, 'src') not in sys.path:
            sys.path.insert(0, os.path.join(data_dir, 'src'))
        
        from database_manager import DatabaseManager
        db_manager = DatabaseManager(data_dir)
        db_manager.migrate_from_csv()  # 从CSV迁移数据到数据库
    except (ImportError, ModuleNotFoundError) as e:
        # 如果导入失败，使用内存中的评分管理器
        print(f"数据库管理器导入失败，使用默认评分管理器: {e}")
        db_manager = RatingManager(data_dir)
    
    weather_rec = WeatherRecommender(loader.label_df, loader.look_df, loader.weather_df)
    clothing_rec = ClothingBasedRecommender(loader.label_df, loader.look_df)
    
    return {
        'loader': loader,
        'translator': translator,
        'style_extractor': style_extractor,
        'weather_rec': weather_rec,
        'clothing_rec': clothing_rec,
        'rating_manager': db_manager,  # 使用数据库管理器
        'label_df': loader.label_df,
        'look_df': loader.look_df,
        'weather_df': loader.weather_df,
        'ratings_df': loader.ratings_df,
        'data_dir': data_dir,
        'db_manager': db_manager,  # 添加数据库管理器引用
    }


def get_pure_style_options(lang: str = 'cn') -> List[str]:
    """获取纯风格选项列表（用于UI）"""
    if lang == 'cn':
        return StyleExtractor.PURE_STYLES_CN
    return StyleExtractor.PURE_STYLES_EN


# ======================= 快速测试 =======================

if __name__ == "__main__":
    _CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
    _DATA_DIR = os.path.join(os.path.dirname(_CURRENT_DIR), 'data')
    if not os.path.exists(_DATA_DIR):
        _DATA_DIR = 'data'
    
    print("=== 测试智能穿搭推荐系统 ===")
    print(f"数据目录: {_DATA_DIR}")
    
    system = create_system(_DATA_DIR)
    
    print(f"\n加载衣物数量: {len(system['label_df'])}")
    
    # 测试天气推荐
    print("\n=== 天气推荐测试 ===")
    result = system['weather_rec'].recommend(
        temperature=15, humidity=60, uv_index=5,
        weather_condition='cloudy', gender='女',
        style_tag='简约', lang='cn'
    )
    print(f"目标季节: {result['target_season']}")
    print(f"目标厚度: {result['target_thick']}")
    print(f"推荐衣物:")
    for cat, item in result['outfit'].items():
        print(f"  [{cat}] {item['title']} - {item['style']} - {item['reason']}")
    print(f"小贴士: {result['tips']}")
    
    # 测试衣物搜索
    print("\n=== 衣物搜索测试 ===")
    results = system['loader'].search_items('卫衣', '女', 'cn')
    print(f"搜索'卫衣' 得到 {len(results)} 件:")
    for r in results[:5]:
        print(f"  {r['itemID']}: {r['title']} - {r['style']}")
    
    # 测试评分
    print("\n=== 评分测试 ===")
    success = system['rating_manager'].add_rating(
        recommendation_type='weather', rating=4,
        feedback='推荐不错，风格很合适', items=['p1', 'p2']
    )
    print(f"添加评分: {'成功' if success else '失败'}")
    stats = system['rating_manager'].get_statistics()
    print(f"评分统计: {stats}")
    
    print("\n=== 所有测试完成 ===")
