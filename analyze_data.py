import pandas as pd
import os

# 设置路径
data_dir = '.'

# 检查文件结构
print("=" * 60)
print("数据集文件结构")
print("=" * 60)

# 查看所有文件
for folder in ['male', 'female', 'child']:
    folder_path = os.path.join(data_dir, folder)
    if os.path.exists(folder_path):
        print(f"\n📁 {folder}/")
        for file in os.listdir(folder_path):
            print(f"  └── {file}")
            
# 读取示例数据
print("\n" + "=" * 60)
print("数据结构分析")
print("=" * 60)

# 读取女性标签数据
female_label = pd.read_excel('female/label_female.xlsx')
print("\n👩 female/label_female.xlsx")
print(f"  行数: {len(female_label)}")
print(f"  列名: {female_label.columns.tolist()}")
print(f"  前3行预览:")
print(female_label.head(3).to_string())

# 读取女性穿搭数据
female_look = pd.read_excel('female/look_female.xlsx')
print("\n👗 female/look_female.xlsx")
print(f"  行数: {len(female_look)}")
print(f"  列名: {female_look.columns.tolist()}")

# 读取天气数据
weather_df = pd.read_excel('weather_data.xlsx')
print("\n🌤️ weather_data.xlsx")
print(f"  行数: {len(weather_df)}")
print(f"  列名: {weather_df.columns.tolist()}")

# 统计分析
print("\n" + "=" * 60)
print("数据统计分析")
print("=" * 60)

# 合并所有标签数据
all_labels = []
for folder in ['male', 'female', 'child']:
    label_path = os.path.join(data_dir, folder, f'label_{folder}.xlsx')
    if os.path.exists(label_path):
        df = pd.read_excel(label_path)
        df['gender'] = folder
        all_labels.append(df)

all_labels_df = pd.concat(all_labels, ignore_index=True)
print(f"\n📊 衣物单品总数: {len(all_labels_df)}")
print(f"  性别分布:")
print(all_labels_df['gender'].value_counts())
print(f"\n  品类分布:")
print(all_labels_df['category'].value_counts()[:10])
print(f"\n  季节分布:")
print(all_labels_df['season'].value_counts())
print(f"\n  厚度分布:")
print(all_labels_df['thick'].value_counts())

# 合并所有穿搭数据
all_looks = []
for folder in ['male', 'female', 'child']:
    look_path = os.path.join(data_dir, folder, f'look_{folder}.xlsx')
    if os.path.exists(look_path):
        df = pd.read_excel(look_path)
        df['gender'] = folder
        all_looks.append(df)

all_looks_df = pd.concat(all_looks, ignore_index=True)
print(f"\n👔 穿搭组合总数: {len(all_looks_df)}")