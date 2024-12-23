import os
import requests
import hashlib
import json
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 配置远程文件地址和本地保存路径的映射
FILES_CONFIG = {
    "https://ruleset.skk.moe/List/domainset/cdn.conf"         : "list/domainset/cdn.conf",
    "https://ruleset.skk.moe/List/domainset/download.conf"    : "list/domainset/download.conf",
    "https://ruleset.skk.moe/List/domainset/reject.conf"      : "list/domainset/reject.conf",
    "https://ruleset.skk.moe/List/domainset/speedtest.conf"   : "list/domainset/speedtest.conf",
    "https://ruleset.skk.moe/List/ip/domestic.conf"           : "list/ip/domestic.conf",
    "https://ruleset.skk.moe/List/ip/lan.conf"                : "list/ip/lan.conf",
    "https://ruleset.skk.moe/List/ip/reject.conf"             : "list/ip/reject.conf",
    "https://ruleset.skk.moe/List/ip/stream.conf"             : "list/ip/stream.conf",
    "https://ruleset.skk.moe/List/non_ip/ai.conf"             : "list/non_ip/ai.conf",
    "https://ruleset.skk.moe/List/non_ip/apple_cdn.conf"      : "list/non_ip/apple_cdn.conf",
    "https://ruleset.skk.moe/List/non_ip/apple_cn.conf"       : "list/non_ip/apple_cn.conf",
    "https://ruleset.skk.moe/List/non_ip/apple_services.conf" : "list/non_ip/apple_services.conf",
    "https://ruleset.skk.moe/List/non_ip/cdn.conf"            : "list/non_ip/cdn.conf",
    "https://ruleset.skk.moe/List/non_ip/domestic.conf"       : "list/non_ip/domestic.conf",
    "https://ruleset.skk.moe/List/non_ip/download.conf"       : "list/non_ip/download.conf",
    "https://ruleset.skk.moe/List/non_ip/global.conf"         : "list/non_ip/global.conf",
    "https://ruleset.skk.moe/List/non_ip/lan.conf"            : "list/non_ip/lan.conf",
    "https://ruleset.skk.moe/List/non_ip/microsoft.conf"      : "list/non_ip/microsoft.conf",
    "https://ruleset.skk.moe/List/non_ip/microsoft_cdn.conf"  : "list/non_ip/microsoft_cdn.conf",
    "https://ruleset.skk.moe/List/non_ip/reject-drop.conf"    : "list/non_ip/reject-drop.conf",
    "https://ruleset.skk.moe/List/non_ip/reject-no-drop.conf" : "list/non_ip/reject-no-drop.conf",
    "https://ruleset.skk.moe/List/non_ip/reject.conf"         : "list/non_ip/reject.conf",
    "https://ruleset.skk.moe/List/non_ip/stream.conf"         : "list/non_ip/stream.conf",
    "https://ruleset.skk.moe/List/non_ip/telegram.conf"       : "list/non_ip/telegram.conf",
    "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/refs/heads/master/rule/Surge/PayPal/PayPal.list" : "list/non_ip/paypal.config",
}

def get_file_hash(content):
    """计算文件内容的 MD5 哈希值"""
    return hashlib.md5(content.encode()).hexdigest()

def load_file_hashes():
    """加载上次同步的文件哈希值"""
    if os.path.exists('.file_hashes.json'):
        with open('.file_hashes.json', 'r') as f:
            return json.load(f)
    return {}

def save_file_hashes(hashes):
    """保存文件哈希值"""
    with open('.file_hashes.json', 'w') as f:
        json.dump(hashes, f)

def process_content(content):
    """处理文件内容，注释掉指定开头的行"""
    # 需要注释的行的开头列表
    patterns_to_comment = [
        'DOMAIN-WILDCARD,',
        'URL-REGEX,'
    ]
    
    processed_lines = []
    for line in content.splitlines():
        should_comment = any(line.strip().startswith(pattern) for pattern in patterns_to_comment)
        if should_comment:
            processed_lines.append('# ' + line)
        else:
            processed_lines.append(line)
    return '\n'.join(processed_lines)

def sync_files():
    # 加载上次同步的文件哈希值
    old_hashes = load_file_hashes()
    new_hashes = {}
    
    logger.info("开始同步文件")
    
    for remote_url, local_path in FILES_CONFIG.items():
        try:
            logger.info(f"正在从 {remote_url} 同步到 {local_path}")
            
            # 下载远程文件
            response = requests.get(remote_url)
            response.raise_for_status()
            content = response.text
            
            logger.info(f"成功获取远程文件，大小: {len(content)} 字节")
            
            # 处理文件内容
            processed_content = process_content(content)
            logger.info("已处理文件内容，注释掉指定开头的行")
            
            # 计算处理后文件的哈希值
            new_hash = get_file_hash(processed_content)
            new_hashes[local_path] = new_hash
            
            # 确保目标目录存在
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            
            # 保存处理后的文件
            with open(local_path, 'w', encoding='utf-8') as f:
                f.write(processed_content)
            logger.info(f"处理后的文件已保存到: {local_path}")
                
        except requests.exceptions.RequestException as e:
            logger.error(f"下载文件失败: {str(e)}")
        except Exception as e:
            logger.error(f"处理文件时出错: {str(e)}")
    
    # 保存新的哈希值
    save_file_hashes(new_hashes)
    logger.info("同步完成")

if __name__ == "__main__":
    sync_files()