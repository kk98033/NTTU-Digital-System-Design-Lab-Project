# 變counter值 來增加google_api_key
import hvac
import random
import string


def generate_api_key(length=32):
    """生成隨機API_key"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def generate_unique_path(base_path, counter):
    """生成唯一的路徑名稱"""
    return f"{base_path}{counter}"


def store_api_key(api_key, path):
    """將API密鑰存儲在Vault中"""
    # 連接到Vault服務器
    client = hvac.Client(url='http://127.0.0.1:8200')

    # 將API密鑰存儲到Vault中
    client.secrets.kv.v2.create_or_update_secret(
        path=path,
        secret=dict(api_key=api_key)
    )

    print("API密鑰已成功存儲在Vault中！")


if __name__ == "__main__":
    # 生成隨機的API密鑰
    new_api_key = generate_api_key()

    # 定義基本路徑名稱
    base_path = "google_api_key"

    # 初始化計數器 變更counter
    counter = 4

    # 生成唯一的路徑名稱
    new_path = generate_unique_path(base_path, counter)

    # 將API密鑰存儲在Vault中
    store_api_key(new_api_key, new_path)
