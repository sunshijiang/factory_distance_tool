# Factory Distance Tool

## 项目概述

这是一个本地运行的厂区距离测算工具。

- 使用 `Python` 启动一个本地 HTTP 服务
- 使用浏览器页面完成图片标注、距离计算、工程保存与导出
- 不依赖后端 API，也不需要独立数据库服务
- 适合在厂区截图或平面图上标注设备点与厂界距离

## 主要能力

- 上传厂区截图作为底图，支持 `PNG/JPG`
- 通过两点定义比例尺，建立像素与真实距离换算关系
- 设置坐标原点，输出设备相对坐标
- 绘制东、南、西、北四个方向厂界，且每个方向支持多段线
- 添加设备点并查看到四向厂界的最短距离
- 自动保存到浏览器 `IndexedDB`
- 导入/导出工程 `JSON`
- 导出设备数据 `CSV`

## 工程结构

- `app.py`：唯一核心源码，包含页面 HTML/CSS/JS 和本地 HTTP 服务
- `build_windows.bat`：Windows 下自动创建虚拟环境并执行 `PyInstaller` 打包
- `FactoryDistanceTool.spec`：`PyInstaller` 打包配置
- `WINDOWS_EXE_README.md`：Windows 打包和运行说明
- `dist/`：已生成的可执行文件
- `build/`：打包中间产物
- `.venv-build/`：打包使用的虚拟环境

## `app.py` 模块划分

### 1. 前端页面模板

`app.py` 中的 `HTML` 常量内嵌了完整单页应用：

- 页面布局与控件
- 视觉样式
- 前端状态管理
- Canvas 绘制逻辑
- 工程导入导出与自动保存

### 2. 前端状态与数据规范化

前端维护一个 `state` 对象，负责保存：

- 当前图片与工程名称
- 当前操作模式
- 比例尺、坐标原点
- 四个方向的厂界线段
- 设备点列表
- 撤销历史与自动保存时间

同时提供一组 `normalize*` 方法，确保导入工程、恢复自动保存时的数据兼容和安全。

### 3. 自动保存与工程序列化

核心逻辑：

- `buildProjectPayload()`：把当前工程组织成可保存数据
- `saveAutosaveNow()`：写入 `IndexedDB`
- `loadAutosaveProject()`：恢复自动保存工程
- `exportProjectFile()` / `importProjectFile()`：导出和导入工程文件

工程文件内会保存图片的 `data URL`，因此是自包含的。

### 4. 绘图与几何计算

Canvas 部分负责：

- 绘制底图、比例尺、原点、厂界、设备点
- 根据鼠标状态显示临时辅助线
- 通过“点到线段最短距离”算法计算设备到厂界距离

距离计算核心函数：

- `pointToSegmentDistance()`
- `pixelToActual()`
- `getBoundaryDistanceValue()`

### 5. 交互工作流

包括：

- 设置比例尺
- 设置原点
- 绘制厂界
- 添加设备
- 撤销、清空、恢复自动保存

这些流程由事件绑定和 `handleCanvasClick()` 等函数共同驱动。

### 6. 本地服务层

Python 部分非常轻量：

- `SinglePageHandler`：仅返回首页 HTML
- `main()`：解析命令行参数、启动本地服务、自动打开浏览器

## 运行方式

### 直接运行 Python

```bash
python app.py
```

默认启动本地服务后，在浏览器打开页面。

可选参数：

```bash
python app.py --host 127.0.0.1 --port 8765 --no-browser
```

## Windows 打包

双击运行：

- `build_windows.bat`

执行后会：

- 创建 `.venv-build`
- 安装 `PyInstaller`
- 生成 `dist\FactoryDistanceTool.exe`

## 当前已知注意点

- 项目当前没有 `requirements.txt` 或 `pyproject.toml`
- `dist/` 和 `build/` 中已有历史打包产物，不建议直接提交到 GitHub
- `WINDOWS_EXE_README.md` 中的默认监听地址与源码默认值存在轻微不一致，源码当前默认 `--host 0.0.0.0`
- 前端页面、业务逻辑、服务端代码全部集中在一个文件中，维护成本会随着需求增长而上升

## 建议的 GitHub 管理方式

建议仓库只提交源码和文档，不提交以下内容：

- `.venv-build/`
- `build/`
- `dist/`
- 临时缓存文件

## 后续优化清单

### 架构层

- 将 `app.py` 拆分为 `server`、`template`、`frontend assets` 多文件结构
- 把前端 JS 从内嵌字符串中拆出，降低维护难度
- 增加 `requirements.txt` 或 `pyproject.toml`，明确依赖与 Python 版本

### 功能层

- 支持编辑、删除、拖拽设备点和厂界线段
- 支持缩放、平移画布，提升大图操作体验
- 支持显示设备到最近厂界的投影线
- 支持批量导入设备点数据
- 支持更丰富的工程元数据，如项目编号、备注、测量日期

### 计算层

- 增加测量结果校验提示，例如比例尺缺失、厂界未闭合、原点未设置
- 增加不同计算模式，例如垂直投影距离与最短距离切换
- 增加单位换算能力，如米/毫米自动转换

### 体验层

- 提供更明确的步骤引导和空状态提示
- 增加快捷键说明面板
- 增加错误提示与导入失败原因说明
- 增加操作日志或变更记录面板

### 工程化层

- 增加 `.gitignore`
- 增加 `README.md`
- 增加基本测试，至少覆盖几何计算函数
- 增加 CI，自动检查语法和打包流程

如果后续你要做优化，可以直接从这份清单里挑一项，我可以继续帮你落地实现。
