# api/index.py
import os, sys
# 让函数目录(/api)能导入根目录里的 web_app.py
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# 从你的 Flask 应用导入 app（确保 web_app.py 里有 app = Flask(__name__)）
from web_app import app  # 如果你的实例名不是 app，请改成实际名字

# Vercel 的 Python 运行时会寻找名为 "app" 的 WSGI 对象
# 这里什么都不用改，保持变量名为 app 即可