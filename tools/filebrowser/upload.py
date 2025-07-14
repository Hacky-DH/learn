import os
import sys
import httpx

# filebrowser需要先登录拿到token再上传文件
# nodejs 实现 https://github.com/filebrowser/filebrowser/issues/2551

user_key = 'FILEBROWSER_USERNAME'
pass_key = 'FILEBROWSER_PASSWORD'
login_url = 'http://.../filebrowser/api/login'
upload_url = 'http://.../filebrowser/api/resources'


def upload():
    if len(sys.argv) < 2:
        print('缺少文件')
        os._exit(1)
    path = sys.argv[1]
    if not os.path.exists(path):
        print(f'找不到 {path}')
        os._exit(1)
    print(f'准备上传 {path}')
    if user_key not in os.environ or pass_key not in os.environ:
        print(f'缺少用户名和密码，设置环境变量{user_key}和{pass_key}')
        os._exit(1)
    # 获取token
    data = {
        "username": os.environ.get(user_key),
        "password": os.environ.get(pass_key)
    }
    response = httpx.post(login_url, json=data)
    token = response.raise_for_status().text
    print('成功获取了token')
    print(f'开始上传...')
    with open(path, 'rb') as f:
        file_contents = f.read()
    headers = {'Content-Type': 'application/octet-stream', 'X-Auth': token}
    url = f"{upload_url}/{file}?override=true"
    response = httpx.post(url, content=file_contents, headers=headers)
    response.raise_for_status()
    print(f'成功上传')


if __name__ == '__main__':
    upload()
