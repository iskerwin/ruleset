import base64
import os
import requests
from urllib.parse import urlparse
from datetime import datetime

class GFWListConverter:
    def __init__(self):
        self.gfwlist_url = "https://raw.githubusercontent.com/gfwlist/gfwlist/master/gfwlist.txt"
        self.domains = set()
        self.output_dir = "list"
        self.output_file = os.path.join(self.output_dir, "gfwlist.conf")

    def fetch_and_decode(self):
        """获取并解码 GFWList"""
        try:
            response = requests.get(self.gfwlist_url)
            response.raise_for_status()
            return base64.b64decode(response.text).decode('utf-8')
        except Exception as e:
            print(f"Error fetching GFWList: {e}")
            return None

    def parse_rule(self, rule):
        """解析单条规则"""
        if not rule or rule.startswith('!') or rule.startswith('['):
            return None

        # 移除注释
        if '#' in rule:
            rule = rule.split('#')[0].strip()

        # 处理白名单规则
        if rule.startswith("@@"):
            return None

        # 处理常见规则格式
        if rule.startswith('||'):
            domain = rule[2:].split('/')[0].strip('.')
        elif rule.startswith('|') or rule.startswith('.'):
            domain = rule[1:].split('/')[0].strip('.')
        elif rule.startswith('http://') or rule.startswith('https://'):
            domain = urlparse(rule).netloc
        else:
            domain = rule.split('/')[0].strip('.')

        # 清理域名
        domain = domain.split('*')[-1].strip('.')
        return domain if self.is_valid_domain(domain) else None

    def is_valid_domain(self, domain):
        """验证域名有效性"""
        if not domain or '*' in domain or '/' in domain:
            return False
        
        try:
            # 基本域名验证
            parts = domain.split('.')
            return len(parts) >= 2 and all(part.strip() for part in parts)
        except:
            return False

    def convert_to_surge_rules(self):
        """转换为 Surge ruleset 格式"""
        # 确保输出目录存在
        os.makedirs(self.output_dir, exist_ok=True)

        content = self.fetch_and_decode()
        if not content:
            return False

        # 解析规则
        for line in content.splitlines():
            domain = self.parse_rule(line)
            if domain:
                self.domains.add(domain)

        # 写入文件
        with open(self.output_file, 'w', encoding='utf-8') as f:
            # 写入头部信息
            f.write('#!name=GFWList\n')
            f.write('#!desc=Generated from GFWList\n')
            f.write(f'#!updated={datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n\n')
            
            # 写入域名规则
            for domain in sorted(self.domains):
                f.write(f'DOMAIN-SUFFIX,{domain},PROXY\n')

        print(f"Generated {len(self.domains)} rules")
        return True

def main():
    converter = GFWListConverter()
    if converter.convert_to_surge_rules():
        print(f"Rules have been saved to {converter.output_file}")
    else:
        print("Failed to update rules")
        exit(1)

if __name__ == "__main__":
    main()