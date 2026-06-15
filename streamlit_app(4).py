"""
智能穿搭推荐系统 - Streamlit 交互界面
功能：
1. 根据天气情况推荐穿搭
2. 根据已有衣物推荐穿搭（关键词搜索输入）
3. 纯风格偏好选择（休闲、复古、简约等）
4. 推荐结果评分（0-5星）
5. 中英文切换
"""
import sys
import os

# 把当前文件所在的文件夹加入Python搜索路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
import streamlit as st
import pandas as pd


# 添加项目路径并设置数据目录
_CURRENT_FILE = os.path.abspath(__file__)
_APP_DIR = os.path.dirname(_CURRENT_FILE)
_PROJECT_DIR = _APP_DIR  # 数据文件直接放在项目根目录下
DATA_DIR = _PROJECT_DIR  # 数据目录就是项目目录本身

sys.path.append(_APP_DIR)
sys.path.append(os.path.join(_APP_DIR, 'src'))

from backend_core import (
    create_system,
    get_pure_style_options,
)

# ======================================
# 页面配置
# ======================================
st.set_page_config(
    page_title="智能穿搭推荐系统",
    page_icon="👔",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ======================================
# 全局状态管理
# ======================================
if 'system' not in st.session_state:
    with st.spinner('正在加载数据...'):
        st.session_state.system = create_system(DATA_DIR)

if 'owned_items' not in st.session_state:
    st.session_state.owned_items = []  # list of itemIDs

if 'current_language' not in st.session_state:
    st.session_state.current_language = 'cn'

if 'last_recommendation_type' not in st.session_state:
    st.session_state.last_recommendation_type = None

if 'last_recommendation_items' not in st.session_state:
    st.session_state.last_recommendation_items = []

system = st.session_state.system

# ======================================
# 国际化文本
# ======================================
def get_text(key, lang='cn'):
    """获取国际化文本"""
    texts = {
        'cn': {
            'title': '🧥 智能穿搭推荐系统',
            'subtitle': '根据天气或已有衣物，智能为您推荐最佳穿搭方案',
            'mode': '选择推荐模式',
            'mode_weather': '🌤️ 根据天气推荐',
            'mode_clothing': '👗 根据衣物推荐',
            'language': '🔤 语言选择',
            'chinese': '中文',
            'english': 'English',
            'gender': '👤 性别',
            'male': '男',
            'female': '女',
            'child': '童',
            'style': '🎨 风格偏好',
            'style_any': '不限',
            'get_recommendation': '🎯 获取推荐',
            'weather_params': '🌡️ 天气参数',
            'temperature': '温度 (°C)',
            'humidity': '湿度 (%)',
            'uv_index': '紫外线指数',
            'weather_condition': '天气状况',
            'sunny': '晴天',
            'cloudy': '多云',
            'windy': '大风',
            'rainy': '雨天',
            'thunderstorm': '雷暴',
            'snowy': '雪天',
            'foggy': '雾天',
            'hazy': '霾天',
            'recommended_outfit': '✨ 推荐穿搭方案',
            'target_season': '目标季节',
            'target_thick': '衣物厚度',
            'needs': '需求分析',
            'tips': '💡 穿搭小贴士',
            'search_clothing': '🔍 搜索您的衣物',
            'search_placeholder': '输入关键词，如"卫衣"、"衬衫"、"牛仔裤"、"sweatshirt"',
            'your_clothing': '👕 您已添加的衣物',
            'add_item': '➕ 添加',
            'remove_item': '➖ 移除',
            'clear_all': '🗑️ 清空所有',
            'no_items_added': '还没有添加衣物，使用上方搜索框添加您的衣物',
            'item_count': '已添加件数',
            'missing_categories': '📦 需要补充的品类',
            'suggested_items': '🎁 推荐补充单品',
            'complete_outfit': '👗 完整穿搭方案',
            'owned_items_section': '已有衣物',
            'recommended_items_section': '推荐补充',
            'clothing_analysis': '📊 衣物分析',
            'rating_title': '⭐ 请为本次推荐打分',
            'rating_subtitle': '您的评价将帮助我们改进推荐效果',
            'rating_0': '0星 - 完全不满意',
            'rating_1': '1星 - 很不满意',
            'rating_2': '2星 - 不太满意',
            'rating_3': '3星 - 一般',
            'rating_4': '4星 - 比较满意',
            'rating_5': '5星 - 非常满意',
            'rating_feedback': '💬 您的建议（可选）',
            'rating_submit': '📤 提交评分',
            'rating_thanks': '✅ 感谢您的反馈！评分已记录',
            'rating_stats': '📈 评分统计',
            'no_rating_yet': '暂无评分数据',
            'avg_rating': '平均评分',
            'total_ratings': '总评分次数',
            'search_results': '搜索结果',
            'no_search_results': '没有找到匹配的衣物，请尝试其他关键词',
            'click_to_add': '点击添加',
            'already_added': '✓ 已添加',
            'reason': '推荐理由',
            'match_reason': '匹配说明',
            'fashion_tips': '时尚小贴士',
        },
        'en': {
            'title': '🧥 Smart Outfit Recommendation System',
            'subtitle': 'Get the best outfit recommendations based on weather or your existing clothing',
            'mode': 'Select Mode',
            'mode_weather': '🌤️ Weather-based Recommendation',
            'mode_clothing': '👗 Clothing-based Recommendation',
            'language': '🔤 Language',
            'chinese': '中文',
            'english': 'English',
            'gender': '👤 Gender',
            'male': 'Male',
            'female': 'Female',
            'child': 'Child',
            'style': '🎨 Style Preference',
            'style_any': 'Any',
            'get_recommendation': '🎯 Get Recommendation',
            'weather_params': '🌡️ Weather Parameters',
            'temperature': 'Temperature (°C)',
            'humidity': 'Humidity (%)',
            'uv_index': 'UV Index',
            'weather_condition': 'Weather Condition',
            'sunny': 'Sunny',
            'cloudy': 'Cloudy',
            'windy': 'Windy',
            'rainy': 'Rainy',
            'thunderstorm': 'Thunderstorm',
            'snowy': 'Snowy',
            'foggy': 'Foggy',
            'hazy': 'Hazy',
            'recommended_outfit': '✨ Recommended Outfit',
            'target_season': 'Target Season',
            'target_thick': 'Clothing Thickness',
            'needs': 'Needs Analysis',
            'tips': '💡 Fashion Tips',
            'search_clothing': '🔍 Search Your Clothing',
            'search_placeholder': 'Enter keywords like "sweatshirt", "shirt", "jeans"',
            'your_clothing': '👕 Your Added Clothing',
            'add_item': '➕ Add',
            'remove_item': '➖ Remove',
            'clear_all': '🗑️ Clear All',
            'no_items_added': 'No clothing added yet. Use the search box above to add your items.',
            'item_count': 'Items Added',
            'missing_categories': '📦 Missing Categories',
            'suggested_items': '🎁 Suggested Items',
            'complete_outfit': '👗 Complete Outfit',
            'owned_items_section': 'Owned Items',
            'recommended_items_section': 'Recommended Items',
            'clothing_analysis': '📊 Clothing Analysis',
            'rating_title': '⭐ Rate This Recommendation',
            'rating_subtitle': 'Your feedback helps us improve',
            'rating_0': '0 stars - Very Dissatisfied',
            'rating_1': '1 star - Dissatisfied',
            'rating_2': '2 stars - Somewhat Dissatisfied',
            'rating_3': '3 stars - Neutral',
            'rating_4': '4 stars - Satisfied',
            'rating_5': '5 stars - Very Satisfied',
            'rating_feedback': '💬 Your Suggestions (optional)',
            'rating_submit': '📤 Submit Rating',
            'rating_thanks': '✅ Thank you! Your rating has been recorded',
            'rating_stats': '📈 Rating Statistics',
            'no_rating_yet': 'No rating data yet',
            'avg_rating': 'Average Rating',
            'total_ratings': 'Total Ratings',
            'search_results': 'Search Results',
            'no_search_results': 'No matching items found. Try different keywords.',
            'click_to_add': 'Click to add',
            'already_added': '✓ Added',
            'reason': 'Reason',
            'match_reason': 'Match Reason',
            'fashion_tips': 'Fashion Tips',
        }
    }
    return texts[lang].get(key, key)

# ======================================
# 通用样式
# ======================================
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 15px;
        margin-bottom: 20px;
    }
    .item-card {
        background: #f8f9fa;
        padding: 12px;
        border-radius: 10px;
        margin: 8px 0;
        border-left: 4px solid #667eea;
    }
    .item-card-added {
        background: #e8f5e9;
        padding: 12px;
        border-radius: 10px;
        margin: 8px 0;
        border-left: 4px solid #4caf50;
    }
    .tip-box {
        background: #fff3cd;
        padding: 12px;
        border-radius: 8px;
        margin: 8px 0;
        border-left: 4px solid #ffc107;
    }
    .weather-info {
        background: #e3f2fd;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .rating-section {
        background: linear-gradient(135deg, #fff5f5 0%, #ffe8e8 100%);
        padding: 20px;
        border-radius: 15px;
        margin-top: 20px;
        border: 2px solid #ffd700;
    }
    .category-label {
        font-weight: bold;
        color: #667eea;
        font-size: 1.05em;
    }
    .search-result-item {
        padding: 10px;
        background: #ffffff;
        border-radius: 8px;
        margin: 6px 0;
        border: 1px solid #e0e0e0;
        transition: all 0.2s;
    }
    .search-result-item:hover {
        border-color: #667eea;
        background: #f5f3ff;
    }
    .star-display {
        font-size: 1.5em;
        color: #ffd700;
    }
</style>
""", unsafe_allow_html=True)


# ======================================
# 语言选择
# ======================================
lang = st.session_state.current_language

# 标题
st.markdown(f"<h1 style='text-align: center;'>{get_text('title', lang)}</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; color: #666; font-size: 1.1em;'>{get_text('subtitle', lang)}</p>", unsafe_allow_html=True)

# 侧边栏
with st.sidebar:
    st.markdown(f"## {get_text('language', lang)}")
    lang_choice = st.radio(
        "",
        options=['cn', 'en'],
        format_func=lambda x: get_text('chinese' if x == 'cn' else 'english', lang),
        index=0 if lang == 'cn' else 1,
        key='lang_radio'
    )
    if lang_choice != lang:
        st.session_state.current_language = lang_choice
        st.rerun()
    
    st.markdown("---")
    
    # 模式选择
    st.markdown(f"## {get_text('mode', lang)}")
    mode = st.radio(
        "",
        options=['weather', 'clothing'],
        format_func=lambda x: get_text('mode_weather' if x == 'weather' else 'mode_clothing', lang),
        index=0,
        key='mode_radio'
    )

# ======================================
# 天气推荐渲染
# ======================================
def render_weather_recommendation(rec_system, label_df, lang):
    """渲染天气推荐界面"""
    system = rec_system
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"### {get_text('weather_params', lang)}")
        
        # 性别
        gender_label = get_text('gender', lang)
        gender_options = [get_text('male', lang), get_text('female', lang), get_text('child', lang)]
        gender_display = st.selectbox(gender_label, gender_options, index=1, key='w_gender')
        gender_map = {get_text('male', lang): '男', get_text('female', lang): '女', get_text('child', lang): '童'}
        gender = gender_map[gender_display]
        
        # 风格
        style_label = get_text('style', lang)
        style_options = get_pure_style_options(lang)
        selected_style_display = st.selectbox(style_label, style_options, index=0, key='w_style')
        style_tag = None
        if selected_style_display != style_options[0]:  # 不是"不限"
            style_tag = selected_style_display
        
        # 天气参数
        temperature = st.slider(get_text('temperature', lang), -10, 40, 20, key='w_temp')
        humidity = st.slider(get_text('humidity', lang), 0, 100, 60, key='w_humidity')
        uv_index = st.slider(get_text('uv_index', lang), 0, 11, 5, key='w_uv')
        
        weather_label = get_text('weather_condition', lang)
        weather_opts = [get_text('sunny', lang), get_text('cloudy', lang), get_text('windy', lang),
                       get_text('rainy', lang), get_text('thunderstorm', lang), get_text('snowy', lang)]
        weather_display = st.selectbox(weather_label, weather_opts, index=1, key='w_weather')
        
        weather_cond_map = {
            get_text('sunny', lang): 'sunny',
            get_text('cloudy', lang): 'cloudy',
            get_text('windy', lang): 'windy',
            get_text('rainy', lang): 'rainy',
            get_text('thunderstorm', lang): 'thunderstorm',
            get_text('snowy', lang): 'snowy',
        }
        weather_condition = weather_cond_map[weather_display]
    
    with col2:
        st.markdown("### 📊 参数概览")
        st.info(f"""
        **{get_text('gender', lang)}:** {gender_display}  
        **{get_text('style', lang)}:** {selected_style_display}  
        **{get_text('temperature', lang)}:** {temperature}°C  
        **{get_text('humidity', lang)}:** {humidity}%  
        **{get_text('uv_index', lang)}:** {uv_index}  
        **{get_text('weather_condition', lang)}:** {weather_display}
        """)
    
    # 获取推荐
    if st.button(f"🎯 {get_text('get_recommendation', lang)}", type='primary', key='w_btn'):
        with st.spinner(lang == 'cn' and '正在为您生成推荐...' or 'Generating recommendation...'):
            result = system['weather_rec'].recommend(
                temperature=temperature,
                humidity=humidity,
                uv_index=uv_index,
                weather_condition=weather_condition,
                gender=gender,
                style_tag=style_tag,
                lang=lang
            )
            st.session_state.current_weather_result = result
            st.session_state.last_recommendation_type = 'weather'
            # 记录推荐的衣物ID
            items = []
            for cat, info in result['outfit'].items():
                if 'itemID' in info:
                    items.append(info['itemID'])
            st.session_state.last_recommendation_items = items
    
    # 显示结果（如果有）
    if 'current_weather_result' in st.session_state:
        result = st.session_state.current_weather_result
        
        st.markdown("---")
        st.markdown(f"### {get_text('recommended_outfit', lang)}")
        
        # 天气分析
        if 'weather_analysis' in result:
            with st.container():
                st.markdown('<div class="weather-info">', unsafe_allow_html=True)
                col_a, col_b = st.columns(2)
                with col_a:
                    st.markdown(f"**{get_text('target_season', lang)}:** {result.get('target_season', '')}")
                    st.markdown(f"**{get_text('target_thick', lang)}:** {result.get('target_thick', '')}")
                with col_b:
                    needs = result['weather_analysis'].get('needs', [])
                    needs_cn = {
                        'heat_protection': lang == 'cn' and '防暑' or 'Heat protection',
                        'warm_protection': lang == 'cn' and '保暖' or 'Warmth',
                        'uv_protection': lang == 'cn' and '防晒' or 'UV protection',
                        'rain_protection': lang == 'cn' and '防雨' or 'Rain protection',
                        'wind_protection': lang == 'cn' and '防风' or 'Wind protection',
                        'snow_protection': lang == 'cn' and '防雪' or 'Snow protection',
                        'humidity_control': lang == 'cn' and '除湿' or 'Humidity control',
                        'dryness_control': lang == 'cn' and '保湿' or 'Moisturize',
                    }
                    if needs:
                        needs_text = [needs_cn.get(n, n) for n in needs]
                        st.markdown(f"**{get_text('needs', lang)}:** {'、'.join(needs_text)}")
                    else:
                        st.markdown(f"**{get_text('needs', lang)}:** {lang == 'cn' and '无特殊需求' or 'No special needs'}")
                st.markdown('</div>', unsafe_allow_html=True)
        
        # 显示穿搭
        if 'outfit' in result:
            outfit = result['outfit']
            cols = st.columns(3)
            col_idx = 0
            
            for cat, info in outfit.items():
                with cols[col_idx % 3]:
                    st.markdown(f'<div class="item-card">', unsafe_allow_html=True)
                    st.markdown(f'<span class="category-label">{cat}</span>')
                    st.markdown(f"📌 **{info.get('title', '')}**")
                    st.markdown(f"{get_text('style', lang)}: {info.get('style', '')}")
                    if 'reason' in info and info['reason']:
                        st.markdown(f"💡 {info['reason']}")
                    st.markdown('</div>', unsafe_allow_html=True)
                col_idx += 1
        
        # 小贴士
        if 'tips' in result and result['tips']:
            st.markdown(f"### {get_text('tips', lang)}")
            for tip in result['tips']:
                st.markdown(f'<div class="tip-box">{tip}</div>', unsafe_allow_html=True)
        
        # 评分部分
        render_rating_section('weather', st.session_state.last_recommendation_items, lang)


# ======================================
# 衣物推荐渲染
# ======================================
def render_clothing_recommendation(rec_system, label_df, lang):
    """渲染基于衣物的推荐界面 - 关键词搜索方式"""
    system = rec_system
    
    # 性别选择
    col_g, col_s = st.columns(2)
    with col_g:
        gender_label = get_text('gender', lang)
        gender_options = [get_text('male', lang), get_text('female', lang), get_text('child', lang)]
        gender_display = st.selectbox(gender_label, gender_options, index=1, key='c_gender')
        gender_map = {get_text('male', lang): '男', get_text('female', lang): '女', get_text('child', lang): '童'}
        gender = gender_map[gender_display]
    
    with col_s:
        style_label = get_text('style', lang)
        style_options = get_pure_style_options(lang)
        selected_style_display = st.selectbox(style_label, style_options, index=0, key='c_style')
        style_tag = None
        if selected_style_display != style_options[0]:
            style_tag = selected_style_display
    
    st.markdown("---")
    
    # ============================================================
    # 搜索并添加已有衣物
    # ============================================================
    st.markdown(f"### {get_text('search_clothing', lang)}")
    
    # 搜索输入框
    search_query = st.text_input(
        "",
        placeholder=get_text('search_placeholder', lang),
        key='c_search_input'
    )
    
    # 搜索结果
    if search_query and search_query.strip():
        search_results = system['loader'].search_items(search_query.strip(), gender, lang)
        
        if search_results:
            st.markdown(f"**{get_text('search_results', lang)} ({len(search_results)})**")
            
            # 以卡片形式展示结果
            result_cols = st.columns(2)
            for idx, item in enumerate(search_results[:20]):
                col = result_cols[idx % 2]
                with col:
                    is_added = item['itemID'] in st.session_state.owned_items
                    
                    if is_added:
                        st.markdown('<div class="item-card-added">', unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="search-result-item">', unsafe_allow_html=True)
                    
                    st.markdown(f"📌 **{item['title']}**")
                    st.markdown(f"{get_text('style', lang)}: {item.get('style', '')}")
                    
                    # 添加/移除按钮
                    if is_added:
                        if st.button(f"{get_text('remove_item', lang)}", key=f"remove_{item['itemID']}"):
                            st.session_state.owned_items.remove(item['itemID'])
                            st.rerun()
                    else:
                        if st.button(f"{get_text('add_item', lang)}", key=f"add_{item['itemID']}"):
                            st.session_state.owned_items.append(item['itemID'])
                            st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info(get_text('no_search_results', lang))
    
    st.markdown("---")
    
    # ============================================================
    # 显示已添加的衣物
    # ============================================================
    st.markdown(f"### {get_text('your_clothing', lang)}")
    
    # 添加的衣物列表
    if st.session_state.owned_items:
        # 显示已添加的衣物信息
        added_items_detail = []
        for item_id in st.session_state.owned_items:
            item = system['loader'].get_item_by_id(item_id, lang, gender)
            if item:
                added_items_detail.append(item)
        
        st.markdown(f"**{get_text('item_count', lang)}: {len(added_items_detail)}**")
        
        # 显示每件衣物
        cols = st.columns(2)
        for idx, item in enumerate(added_items_detail):
            with cols[idx % 2]:
                st.markdown('<div class="item-card-added">', unsafe_allow_html=True)
                st.markdown(f"📌 **{item.get('title', '')}**")
                st.markdown(f"{get_text('style', lang)}: {item.get('style', '')}")
                st.markdown(f"ID: {item.get('itemID', '')}")
                if st.button(f"{get_text('remove_item', lang)}", key=f"remove_added_{item['itemID']}"):
                    st.session_state.owned_items.remove(item['itemID'])
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
        
        # 清空按钮
        if st.button(f"{get_text('clear_all', lang)}", key='clear_all_btn'):
            st.session_state.owned_items = []
            st.rerun()
    else:
        st.info(get_text('no_items_added', lang))
    
    st.markdown("---")
    
    # 获取推荐按钮
    if st.button(f"🎯 {get_text('get_recommendation', lang)}", type='primary', key='c_btn'):
        with st.spinner(lang == 'cn' and '正在为您生成推荐...' or 'Generating recommendation...'):
            result = system['clothing_rec'].recommend(
                owned_item_ids=st.session_state.owned_items,
                gender=gender,
                style_tag=style_tag,
                lang=lang
            )
            st.session_state.current_clothing_result = result
            st.session_state.last_recommendation_type = 'clothing'
            
            # 记录推荐的衣物
            items = []
            if 'complete_outfit' in result:
                co = result['complete_outfit']
                for item in co.get('owned', []):
                    if 'itemID' in item:
                        items.append(item['itemID'])
                for item in co.get('recommended', []):
                    if 'itemID' in item:
                        items.append(item['itemID'])
            st.session_state.last_recommendation_items = items
    
    # 显示结果
    if 'current_clothing_result' in st.session_state:
        result = st.session_state.current_clothing_result
        
        st.markdown(f"### {get_text('recommended_outfit', lang)}")
        
        # 衣物分析
        if 'analysis' in result:
            st.markdown(f"#### {get_text('clothing_analysis', lang)}")
            col_a1, col_a2 = st.columns(2)
            with col_a1:
                st.info(f"{get_text('item_count', lang)}: {result['analysis'].get('category_count', 0)}")
            with col_a2:
                categories = result['analysis'].get('categories', [])
                if categories:
                    st.info(f"{lang == 'cn' and '已有品类' or 'Categories'}: {', '.join(categories)}")
        
        # 显示已有衣物
        if 'complete_outfit' in result:
            co = result['complete_outfit']
            
            # 已有衣物
            if co.get('owned'):
                st.markdown(f"#### {get_text('owned_items_section', lang)}")
                cols = st.columns(3)
                for idx, item in enumerate(co['owned']):
                    with cols[idx % 3]:
                        st.markdown('<div class="item-card-added">', unsafe_allow_html=True)
                        cat_label = item.get('category_cn', item.get('category', ''))
                        st.markdown(f'<span class="category-label">{cat_label}</span>', unsafe_allow_html=True)
                        st.markdown(f"📌 **{item.get('title', '')}**")
                        st.markdown(f"{get_text('style', lang)}: {item.get('style', '')}")
                        st.markdown('</div>', unsafe_allow_html=True)
            
            # 推荐补充的衣物
            if co.get('recommended'):
                st.markdown(f"#### {get_text('recommended_items_section', lang)}")
                cols = st.columns(3)
                for idx, item in enumerate(co['recommended']):
                    with cols[idx % 3]:
                        st.markdown('<div class="item-card">', unsafe_allow_html=True)
                        cat_label = item.get('category_cn', item.get('category', ''))
                        st.markdown(f'<span class="category-label">{cat_label}</span>', unsafe_allow_html=True)
                        st.markdown(f"📌 **{item.get('title', '')}**")
                        st.markdown(f"{get_text('style', lang)}: {item.get('style', '')}")
                        st.markdown('</div>', unsafe_allow_html=True)
        
        # 缺失品类
        if 'missing_categories_cn' in result and result['missing_categories_cn']:
            st.markdown(f"#### {get_text('missing_categories', lang)}")
            st.warning("、".join(result['missing_categories_cn']))
        
        # 推荐补充
        if 'suggestions' in result and result['suggestions']:
            st.markdown(f"#### {get_text('suggested_items', lang)}")
            for cat, items in result['suggestions'].items():
                if items:
                    with st.expander(f"📦 {items[0].get('category_cn', cat)} ({len(items)} 件)"):
                        for item in items:
                            st.markdown(f"- **{item.get('title', '')}** - {item.get('style', '')}")
                            if item.get('match_reason'):
                                st.markdown(f"  💡 {item['match_reason']}")
        
        # 穿搭小贴士
        if 'outfit_tips' in result and result['outfit_tips']:
            st.markdown(f"### {get_text('fashion_tips', lang)}")
            for tip in result['outfit_tips']:
                st.markdown(f'<div class="tip-box">{tip}</div>', unsafe_allow_html=True)
        
        # 评分部分
        render_rating_section('clothing', st.session_state.last_recommendation_items, lang)


# ======================================
# 评分组件
# ======================================
def render_rating_section(recommendation_type, items, lang):
    """渲染推荐结果后的评分组件"""
    
    st.markdown("---")
    st.markdown('<div class="rating-section">', unsafe_allow_html=True)
    
    st.markdown(f"### {get_text('rating_title', lang)}")
    st.markdown(f"<p style='color: #666;'>{get_text('rating_subtitle', lang)}</p>", unsafe_allow_html=True)
    
    # 星号评分
    rating = st.slider(
        "",
        min_value=0,
        max_value=5,
        value=3,
        key=f"rating_slider_{recommendation_type}"
    )
    
    # 显示星星
    stars_html = "⭐" * rating + "☆" * (5 - rating)
    st.markdown(f"<p class='star-display'>{stars_html}</p>", unsafe_allow_html=True)
    
    # 反馈文本
    feedback = st.text_area(
        get_text('rating_feedback', lang),
        key=f"rating_feedback_{recommendation_type}",
        height=80
    )
    
    # 提交按钮
    if st.button(f"{get_text('rating_submit', lang)}", type='primary', key=f"rating_submit_{recommendation_type}"):
        success = system['rating_manager'].add_rating(
            recommendation_type=recommendation_type,
            rating=rating,
            feedback=feedback,
            items=items
        )
        if success:
            st.success(get_text('rating_thanks', lang))
            st.balloons()
    
    # 评分统计
    stats = system['rating_manager'].get_statistics()
    if stats['count'] > 0:
        st.markdown("---")
        st.markdown(f"### {get_text('rating_stats', lang)}")
        
        col_s1, col_s2, col_s3 = st.columns(3)
        with col_s1:
            st.metric(get_text('total_ratings', lang), stats['count'])
        with col_s2:
            st.metric(get_text('avg_rating', lang), f"{stats['avg_rating']:.1f}⭐")
        with col_s3:
            # 显示最新的评分分布
            if 'by_type' in stats and stats['by_type']:
                type_label = lang == 'cn' and '天气推荐平均分' or 'Weather avg'
                if recommendation_type == 'clothing':
                    type_label = lang == 'cn' and '衣物推荐平均分' or 'Clothing avg'
                avg_by_type = stats['by_type'].get(recommendation_type, stats['avg_rating'])
                st.metric(type_label, f"{avg_by_type:.1f}⭐")
    
    st.markdown('</div>', unsafe_allow_html=True)


# ======================================
# 主入口
# ======================================
def main():
    lang = st.session_state.current_language
    
    if mode == 'weather':
        render_weather_recommendation(system, system['label_df'], lang)
    else:
        render_clothing_recommendation(system, system['label_df'], lang)
    
    # 页脚
    st.markdown("---")
    st.markdown(f"<p style='text-align: center; color: #999;'>© 2026 Smart Outfit Recommendation System | {DATA_DIR}</p>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
