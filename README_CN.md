# Command Line v3.0 Preview  

<p align="center">
  <img src="assets/logo.png" width="120" alt="Command Line Logo"><br>
  <b>A multifunctional Python-based Command Line Tool</b><br>
  <i>一个多功能的 Python 命令行工具</i>
</p>

<p align="center">
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.8+-blue.svg"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-green.svg"></a>
  <a href="https://github.com/chenTom2016/new-command/stargazers"><img src="https://img.shields.io/github/stars/chenTom2016/new-command.svg?style=social"></a>
  <a href="https://github.com/chenTom2016/new-command/issues"><img src="https://img.shields.io/github/issues/chenTom2016/new-command.svg"></a>
  <a href="https://github.com/chenTom2016/new-command/network/members"><img src="https://img.shields.io/github/forks/chenTom2016/new-command.svg"></a>
</p>

---

## 📑 导航 / Navigation
- [✨ 功能概览 / Features](#-功能概览--features)  
- [🚀 快速开始 / Quick Start](#-快速开始--quick-start)  
- [📷 界面预览 / Screenshots](#-界面预览--screenshots)  
- [🛠 开发者 / Author](#-开发者--author)  
- [🌍 English Version](#-english-version)  
- [📄 License](#-license)  

---

## ✨ 功能概览 / Features  

<p align="center">
  <img src="assets/banner.png" width="90%" alt="Command Line Banner">
</p>

- 🖥 **命令行交互 / CLI Shell**
  - 内置命令：`help`, `dir`, `date`, `ip`, `exit`
  - 环境命令：`python`, `node`, `cmd`, `powershell`, `notepad`, `explorer` 等  

- 📦 **模块安装器 / Module Installer**  
  - 类似 `pip`，支持 `install <module-name>` 或 git 地址安装  

- 🎨 **彩色输出 / Colorful Output**  
  - 支持 `color(fg, bg)` 自定义前景色  

- 🖼 **截图工具 / Screenshot Tool**  
  - 支持全屏/区域截图，带预览  

- 📱 **高级二维码生成器 / Advanced QR Tool**  
  - 自定义颜色、LOGO、批量生成、历史记录  

- 🧮 **增强计算器 / Enhanced Calculator**  
  - 支持科学函数、历史记录、内存操作  
  - 内置 Windows 经典彩蛋 `2016 ÷ 13` 🎉  

- 🔒 **文件加解密 / File Encryption & Decryption**  
  - 基于 `cryptography.Fernet`，支持目录递归加解密  

- 🌐 **翻译工具 / Translator**  
  - 基于 Google Translate，命令：`translate <from> <to> <text>`  

- 🔍 **搜索与快捷打开 / Search & Open**  
  - 例如：`{search:Google}: OpenAI`  
  - 或 `{open:www.python.org}`  

- ⚡ **专业模式 / Pro Mode**  
  - 输入 `mode pro` 进入  
  - 支持 `ping`, `open`, `encrypt`, `scan` 等高级命令  

- 📝 **X++ 解释器 / X++ Interpreter**  
  - 轻量级解释器，支持变量、表达式、条件语句、交互模式  

---

## 🚀 快速开始 / Quick Start  

### 环境要求 / Requirements  
- Python 3.8+  
- 安装依赖：  
  ```bash
  pip install tkinter pillow qrcode cryptography googletrans==4.0.0-rc1 colorama requests
  ```

### 启动 / Run  
```bash
python "command Line.py"
```

---

## 📷 界面预览 / Screenshots  

<p align="center">
  <img src="assets/calc.png" width="45%" alt="Calculator Screenshot">
  <img src="assets/qr.png" width="45%" alt="QR Tool Screenshot">
</p>

---

## 🛠 开发者 / Author  
- Author: **Tom (chenTom2016)**  
- GitHub: [chenTom2016](https://github.com/chenTom2016)  

---

## 🌍 English Version  
👉 [Click here for English README](README_EN.md)  

---

## 📄 License  
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.  
