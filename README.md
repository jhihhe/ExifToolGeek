ExifGeek // 元数据传输器
========================

[English](README_en.md) | [中文](README.md)

![Platform](https://img.shields.io/badge/Platform-macOS-000000?style=flat-square&logo=apple&logoColor=white)
![Language](https://img.shields.io/badge/Language-Python_3-3776AB?style=flat-square&logo=python&logoColor=white)
![Framework](https://img.shields.io/badge/Framework-PyQt6-41CD52?style=flat-square&logo=qt&logoColor=white)
![Copyright](https://img.shields.io/badge/Copyright-@JhihHe-blueviolet?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

![界面](https://raw.githubusercontent.com/jhihhe/ExifToolGeek/main/界面.png)

ExifGeek 是一个基于 [ExifTool](https://github.com/exiftool/exiftool) 的 macOS 桌面工具，专注于一个高频工作流：

- 从一张「源图片」中**提取完整 EXIF / 元数据**
- 将这些元数据**批量注入**到一张或多张「目标图片」中

界面采用 Dracula 暗色主题与极客风代码排版，底部操作区类似终端里的「编译面板」。

> 版权：@JhihHe  
> ExifTool 仍遵循其原有授权协议。


功能概览
--------

- **双面板工作流**
  - 左侧：源图片、EXIF 预览、复制 / 导出操作
  - 右侧：目标图片列表
- **完整 EXIF 复制**
  - 调用 ExifTool：`-TagsFromFile -all:all -overwrite_original`
  - 支持：单文件、多文件、整文件夹（递归）
- **拖拽支持**
  - 将文件从 Finder 拖到左侧「源图片」区域
  - 将文件或文件夹拖到右侧「目标图片」区域
- **中英文界面切换**
  - 左上角 `中文 / English` 按钮一键切换
  - 所有文字（标题、按钮、状态栏提示）都会更新
- **Dracula 极客风 UI**
  - 半透明「毛玻璃」暗色背景
  - 等宽字体代码排版
  - EXIF 预览区域带「代码高亮」效果
  - 目标路径列表中目录 / 文件名 / 后缀分色显示
- **EXIF 工具按钮**
  - 复制：将 EXIF JSON 复制到剪贴板
  - 导出 TXT：将 EXIF JSON 导出为 `.txt` 文本文件


技术栈
------

- Python 3
- PyQt6 – GUI 框架
- ExifTool – 元数据引擎（随应用打包）
- py2app – 打包为 macOS `.app`


项目结构
--------

主要文件和目录：

- `main.py` – PyQt6 主程序，包含拖拽逻辑、EXIF 读写、中英文切换等
- `setup.py` – 使用 py2app 构建 `ExifGeek.app` 的配置
- `exiftool_src/` – 打包进应用的 ExifTool 目录
- `icon.icns` – Dracula 风格应用图标
- `dist/ExifGeek.app` – 最新构建的最终版应用
- `dist/ExifGeek_prev.app` – 上一版 UI 的备份构建


开发环境准备
------------

1. **克隆仓库**

   ```bash
   git clone <your-repo-url>
   cd trae_exiftoolGUImac
   ```

2. **创建并激活虚拟环境**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **安装依赖**

   ```bash
   pip install -r requirements.txt
   ```

   典型依赖（仅供参考）：

   - `pyqt6`
   - `py2app`
   - `pillow`（用于生成图标，可选）


从源码运行
----------

在项目根目录执行：

```bash
source venv/bin/activate
python3 main.py
```

直接以 PyQt6 窗口形式运行应用，而不是 `.app`。


构建 macOS 应用
----------------

使用 py2app 构建 `dist/ExifGeek.app`：

```bash
source venv/bin/activate
python3 setup.py py2app
```

说明：

- `setup.py` 已配置：
  - 将 `exiftool_src` 打包进应用资源目录
  - 使用 `icon.icns` 作为图标
  - 将版权信息设置为 `@JhihHe`
- 运行时，应用会优先在打包资源中寻找 ExifTool：
  - 若存在 `RESOURCEPATH/exiftool_src/exiftool`，则使用 `perl exiftool`
  - 否则回退到系统 PATH 中的 `exiftool`


使用说明
--------

### 1. 选择界面语言

- 左上角按钮：
  - `中文` – 中文界面
  - `English` – 英文界面


### 2. 选择源图片

- 将文件拖到左侧「源图片」虚线框区域，或点击该区域从文件对话框中选择。
- 选择后：
  - 调用 ExifTool 使用 `-j` 输出 JSON
  - 左侧文本框中显示带颜色的 EXIF 代码风视图

此时可以：

- **复制** – 将 EXIF JSON 复制到剪贴板
- **导出 TXT** – 将 EXIF JSON 保存为 `.txt` 文本文件


### 3. 添加目标图片

- 将文件或文件夹拖到右侧「目标图片」区域：
  - 若拖入文件夹，会递归遍历其中文件
  - 会忽略以 `.` 开头的隐藏文件
- 右侧列表中显示彩色路径：
  - 目录：偏灰蓝色（类似注释）
  - 文件名：绿色
  - 后缀名：紫色


### 4. 注入元数据

- 当存在源图片且目标列表不为空时，底部 `>>> 注入元数据 >>>` 按钮会变为可用状态。
- 点击后：
  - 对每个目标依次执行：

    ```bash
    -TagsFromFile <source> -all:all -overwrite_original <target>
    ```

  - 右下角状态栏会显示「处理中...」以及最终统计（成功 / 总数）


### 5. 清空状态

- 点击 **清空所有**：
  - 重置源图片路径
  - 清空 EXIF 预览内容
  - 清空目标列表
  - 禁用「注入元数据」按钮


国际化（i18n）
--------------

应用内部使用一个简单的 key-value 翻译字典：

- `main.py` 中的 `TRANSLATIONS` 包含 `en` 和 `zh` 两套文本。
- 界面上的文案统一通过 `self.tr(key)` 读取，根据 `self.curr_lang` 决定语言。
- 顶部语言按钮会调用 `change_language('en' | 'zh')`：
  - 更新当前语言
  - 刷新标题、按钮文本、拖拽提示、状态栏等所有文案

如需增加其它语言：

1. 在 `TRANSLATIONS` 中新增一个语言配置（例如 `ja`）。
2. 增加一个对应的切换按钮，并接入 `change_language`。


EXIF 显示细节
--------------

- 从 ExifTool 得到的原始 JSON 会存入 `self.current_meta`，用于：
  - 复制到剪贴板
  - 导出 TXT 文件
- 左侧预览区域使用 HTML + 内联样式：
  - 字段名和字段值使用不同颜色
  - 数字、列表、字典等类型使用不同配色
  - 整体保持等宽字体、接近代码高亮的观感


已知限制
--------

- 没有逐文件的进度条，仅提供简单的总数统计。
- 使用 `-overwrite_original`，不会生成 `_original` 备份文件，也就没有「撤销」。
- 详细错误信息打印在控制台，界面只提示成功统计。


License / 许可
--------------

- ExifGeek 源码：© @JhihHe，保留所有权利。
- ExifTool：版权和许可归 Phil Harvey 及贡献者所有，  
  详情见其官方仓库：https://github.com/exiftool/exiftool


联系
----

如需反馈或功能建议，可以在 GitHub 仓库提交 Issue，或直接联系 **@JhihHe**。

