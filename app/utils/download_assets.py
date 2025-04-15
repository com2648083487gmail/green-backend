import os
import requests
from pathlib import Path

# 资源下载基础目录
BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / 'static'
IMAGES_DIR = STATIC_DIR / 'images'

# 确保目录存在
def ensure_dir(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

def download_file(url, destination):
    """下载文件到指定位置"""
    try:
        print(f"正在下载: {url} 到 {destination}")
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        with open(destination, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                
        print(f"✅ 成功下载到: {destination}")
        return True
    except Exception as e:
        print(f"❌ 下载失败 {url}: {str(e)}")
        return False

# 定义需要下载的资源
RESOURCES = {
    'icons': [
        {'url': 'https://img.icons8.com/color/96/leaf.png', 'filename': 'icon_leaf.png'},
        {'url': 'https://img.icons8.com/color/96/recycling-symbol.png', 'filename': 'icon_recycle.png'},
        {'url': 'https://img.icons8.com/color/96/deciduous-tree.png', 'filename': 'icon_natural.png'}
    ],
    'category': [
        {'url': 'https://img.icons8.com/ios/200/40C057/armchair.png', 'filename': 'category_chair.png'},
        {'url': 'https://img.icons8.com/ios/200/40C057/table.png', 'filename': 'category_table.png'},
        {'url': 'https://img.icons8.com/ios/200/40C057/bed.png', 'filename': 'category_bed.png'},
        {'url': 'https://img.icons8.com/ios/200/40C057/cupboard.png', 'filename': 'category_收纳.png'},
        {'url': 'https://img.icons8.com/ios/200/40C057/desk.png', 'filename': 'category_书桌.png'},
        {'url': 'https://img.icons8.com/ios/200/40C057/table.png', 'filename': 'category_餐桌.png'}
    ],
    'product': [
        {'url': 'https://images.unsplash.com/photo-1586023492125-27b2c045efd7?q=80&w=800&auto=format&fit=crop', 'filename': 'eco_chair_1.jpg'},
        {'url': 'https://images.unsplash.com/photo-1493663284031-b7e3aefcae8e?q=80&w=800&auto=format&fit=crop', 'filename': 'eco_cabinet_1.jpg'},
        {'url': 'https://images.unsplash.com/photo-1538688525198-9b88f6f53126?q=80&w=800&auto=format&fit=crop', 'filename': 'eco_bed_1.jpg'},
        {'url': 'https://images.unsplash.com/photo-1532372576444-dda954194ad0?q=80&w=800&auto=format&fit=crop', 'filename': 'eco_shelf_1.jpg'},
        {'url': 'https://images.unsplash.com/photo-1594026112284-02bb6f3352fe?q=80&w=800&auto=format&fit=crop', 'filename': 'eco_table_1.jpg'},
        {'url': 'https://images.unsplash.com/photo-1551298370-9d3d53740c72?q=80&w=800&auto=format&fit=crop', 'filename': 'default.jpg'}
    ]
}

def download_all_resources():
    """下载所有资源"""
    # 确保目录存在
    ensure_dir(STATIC_DIR)
    ensure_dir(IMAGES_DIR)
    
    # 为每个资源类型创建目录并下载
    for category, resources in RESOURCES.items():
        category_dir = IMAGES_DIR / category
        ensure_dir(category_dir)
        
        for resource in resources:
            destination = category_dir / resource['filename']
            download_file(resource['url'], destination)
    
    print("所有资源下载完成!")

if __name__ == "__main__":
    download_all_resources() 