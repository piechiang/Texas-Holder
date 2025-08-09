# Web Deployment Guide / 网页部署指南

## 🌐 Texas Hold'em Calculator Web Version

This guide explains how to deploy and run the web version of the Texas Hold'em calculator.

本指南解释如何部署和运行德州扑克计算器的网页版本。

## 📋 Prerequisites / 前置要求

### System Requirements / 系统要求
- Python 3.7+ / Python 3.7及以上版本
- pip (Python package installer) / pip包管理器
- Web browser (Chrome, Firefox, Safari, Edge) / 网页浏览器

### Installation / 安装步骤

#### 1. Install Dependencies / 安装依赖
```bash
# Install required packages / 安装所需包
pip install -r requirements.txt

# Alternative: Install manually / 或者手动安装
pip install Flask==3.0.0 Werkzeug==3.0.1
```

#### 2. Verify Installation / 验证安装
```bash
# Test the command-line version first / 先测试命令行版本
python test_calculator.py

# Should show "All tests passed!" / 应该显示"所有测试通过！"
```

## 🚀 Running the Web Application / 运行网页应用

### Development Mode / 开发模式
```bash
# Start the web server / 启动网页服务器
python web_app.py

# Output should show:
# 🎰 Starting Texas Hold'em Web Calculator...
# 🌐 Open your browser and go to: http://localhost:5000
```

### Access the Application / 访问应用
1. Open your web browser / 打开网页浏览器
2. Go to: `http://localhost:5000` 或 `http://127.0.0.1:5000`
3. You should see the Texas Hold'em Calculator interface / 您应该看到德州扑克计算器界面

## 🎯 Using the Web Interface / 使用网页界面

### Basic Usage / 基本使用

1. **Enter Hole Cards / 输入底牌**:
   - Type your two hole cards (e.g., "As", "Kh")
   - Cards will be validated in real-time / 牌面会实时验证

2. **Enter Community Cards / 输入公共牌** (Optional / 可选):
   - **Flop / 翻牌**: First 3 community cards / 前3张公共牌
   - **Turn / 转牌**: 4th community card / 第4张公共牌  
   - **River / 河牌**: 5th community card / 第5张公共牌

3. **Adjust Settings / 调整设置**:
   - **Number of Opponents / 对手数量**: 1-9 players / 1-9个玩家
   - **Pot Size / 底池大小**: Current pot amount / 当前底池金额
   - **Bet to Call / 需跟注**: Amount you need to call / 您需要跟注的金额
   - **Simulations / 模拟次数**: Accuracy vs speed trade-off / 准确性与速度的权衡

4. **Calculate / 计算**:
   - Click "Calculate" button / 点击"计算"按钮
   - Wait for results (2-10 seconds) / 等待结果(2-10秒)

### Features / 功能特点

#### 🎲 Preset Scenarios / 预设场景
- Click "Presets" to load common poker situations / 点击"预设"加载常见扑克情况
- Includes premium hands, drawing hands, and difficult decisions / 包括优质手牌、听牌和困难决策

#### 📊 Real-time Results / 实时结果
- **Probability Bars / 概率条**: Visual representation of win/tie/lose chances / 胜/平/负概率的可视化显示
- **Hand Strength / 手牌强度**: Current hand ranking and description / 当前手牌排名和描述  
- **Betting Advice / 下注建议**: RAISE/CALL/FOLD recommendations with reasoning / RAISE/CALL/FOLD建议及理由

#### 📱 Mobile Friendly / 移动端友好
- Responsive design works on phones and tablets / 响应式设计适用于手机和平板
- Touch-optimized interface / 触摸优化界面

## 🔧 Configuration / 配置

### Server Settings / 服务器设置

To run on different host/port / 在不同主机/端口运行：

```python
# Edit web_app.py, change the last line:
app.run(debug=True, host='0.0.0.0', port=8080)

# host='0.0.0.0' - Allow external connections / 允许外部连接
# host='127.0.0.1' - Local only / 仅本地访问
# port=8080 - Custom port / 自定义端口
```

### Performance Settings / 性能设置

For better performance / 提高性能：

```python
# In web_app.py, adjust default simulations
'num_simulations': 5000,  # Reduce for faster results / 减少以获得更快结果
```

## 🌍 Production Deployment / 生产环境部署

### Using Gunicorn (Recommended) / 使用Gunicorn(推荐)

```bash
# Install Gunicorn / 安装Gunicorn
pip install gunicorn

# Run with Gunicorn / 使用Gunicorn运行
gunicorn -w 4 -b 0.0.0.0:5000 web_app:app

# -w 4: Use 4 worker processes / 使用4个工作进程
# -b 0.0.0.0:5000: Bind to all interfaces on port 5000 / 绑定所有接口的5000端口
```

### Using Docker / 使用Docker

Create `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "web_app:app"]
```

Build and run / 构建并运行：
```bash
docker build -t texas-holdem-calc .
docker run -p 5000:5000 texas-holdem-calc
```

### Cloud Deployment / 云部署

#### Heroku
1. Create `Procfile`:
   ```
   web: gunicorn web_app:app
   ```

2. Deploy:
   ```bash
   git add .
   git commit -m "Deploy to Heroku"
   git push heroku main
   ```

#### AWS/GCP/Azure
- Use their respective web app services / 使用各自的网页应用服务
- Upload the project files / 上传项目文件
- Configure Python runtime / 配置Python运行时

## 🛠️ Troubleshooting / 故障排除

### Common Issues / 常见问题

#### 1. "Module not found" Error / "找不到模块"错误
```bash
# Ensure you're in the correct directory / 确保在正确目录
cd /path/to/Texas-Holder

# Install dependencies / 安装依赖
pip install -r requirements.txt
```

#### 2. Port Already in Use / 端口已被使用
```bash
# Use different port / 使用不同端口
python web_app.py
# Edit web_app.py to change port / 编辑web_app.py改变端口

# Or kill existing process / 或终止现有进程
lsof -ti:5000 | xargs kill -9  # Linux/Mac
```

#### 3. Slow Calculations / 计算缓慢
- Reduce simulation count in settings / 在设置中减少模拟次数
- Use fewer opponents / 使用更少对手
- Ensure server has sufficient resources / 确保服务器有足够资源

#### 4. Cards Not Validating / 牌面验证失败
- Use correct format: Rank + Suit (e.g., "As", "10h") / 使用正确格式
- Check for duplicate cards / 检查重复牌面
- Ensure all required fields are filled / 确保所有必填字段都已填写

### Performance Tips / 性能提示

1. **Simulation Count / 模拟次数**:
   - 1,000 simulations: Fast, less accurate / 快速，较不准确
   - 5,000 simulations: Good balance / 良好平衡  
   - 10,000+ simulations: Very accurate, slower / 非常准确，较慢

2. **Browser Optimization / 浏览器优化**:
   - Use modern browsers (Chrome, Firefox) / 使用现代浏览器
   - Enable JavaScript / 启用JavaScript
   - Clear cache if experiencing issues / 如有问题请清除缓存

## 🔐 Security Notes / 安全注意事项

### Development vs Production / 开发环境 vs 生产环境

**Development (debug=True):**
- Shows detailed error messages / 显示详细错误信息
- Auto-reloads on code changes / 代码更改时自动重载
- Not secure for public access / 不适合公开访问

**Production (debug=False):**
- Hide detailed errors / 隐藏详细错误
- Better performance / 更好性能
- Use HTTPS in production / 生产环境使用HTTPS

### Best Practices / 最佳实践

1. **Use HTTPS** in production / 生产环境使用HTTPS
2. **Rate limiting** to prevent abuse / 限制请求频率防止滥用
3. **Input validation** on server side / 服务器端输入验证
4. **Monitor resources** usage / 监控资源使用

## 📈 Monitoring / 监控

### Log Analysis / 日志分析
```python
# Add logging to web_app.py / 在web_app.py中添加日志
import logging

logging.basicConfig(level=logging.INFO)
app.logger.info("Calculation request processed")
```

### Health Check Endpoint / 健康检查端点
```python
@app.route('/health')
def health_check():
    return {'status': 'healthy', 'timestamp': time.time()}
```

## 🎉 Success! / 成功！

If everything works correctly, you should have:

如果一切正常，您应该拥有：

✅ Working web interface at http://localhost:5000 / 在http://localhost:5000运行的网页界面  
✅ Real-time probability calculations / 实时概率计算  
✅ Interactive card input with validation / 带验证的交互式牌面输入  
✅ Betting recommendations / 下注建议  
✅ Mobile-friendly design / 移动端友好设计  
✅ Preset scenarios for quick testing / 用于快速测试的预设场景  

Enjoy your Texas Hold'em Calculator! / 享受您的德州扑克计算器！

---

**For support, please check the main README.md or open an issue on GitHub.**

**如需支持，请查看主README.md文件或在GitHub上开启issue。**