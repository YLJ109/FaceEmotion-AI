"""测试图片检测 API"""
import requests
import sys

# 测试文件路径
test_image = "d:/front-back/FaceEmotion-AI/frontend/src/assets/hero.png"

try:
    with open(test_image, 'rb') as f:
        files = {'file': ('hero.png', f, 'image/png')}
        response = requests.post(
            'http://localhost:8000/api/detect/image', files=files)

    print(f"状态码: {response.status_code}")
    print(f"响应内容: {response.text[:500]}")

    if response.status_code == 500:
        print("\n❌ 服务器内部错误!")
        try:
            error_detail = response.json()
            print(f"错误详情: {error_detail}")
        except:
            pass

except Exception as e:
    print(f"请求失败: {e}")
    import traceback
    traceback.print_exc()
