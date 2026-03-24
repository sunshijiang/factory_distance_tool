# Project History

用于记录每次修改的主要内容，便于快速了解项目演进。

## 2026-03-24 - Initial project setup

- 初始化 Git 仓库并推送到 GitHub：`sunshijiang/factory_distance_tool`
- 新增 `.gitignore`，忽略 `dist/`、`build/`、`.venv-build/` 等本地产物
- 为 `app.py` 添加模块化结构注释，便于后续维护
- 新增 `PROJECT_GUIDE.md`，整理项目结构、运行方式与优化清单

## 2026-03-24 - Add formal README and history tracking

- 将项目说明整理为正式 `README.md`
- 新增 `PROJECT_HISTORY.md`，作为后续每次修改的统一历史记录文件
- 明确后续协作约定：每次修改后同步更新历史记录并推送到 GitHub

## 2026-03-24 - Add noise calculation fields and CSV export update

- 在 `app.py` 中新增噪声参数表单，支持建筑物名称、声源名称、型号、声功率级、控制措施、运行时段、相对高度 Z 等字段
- 新增距室内边界距离、建筑物插入损失、建筑物外距离等参数，并自动计算室内边界声级与建筑物外噪声
- 扩展工程导入导出和自动保存数据结构，保证新增噪声字段可以随工程一起保存
- 按指定格式重做 CSV 导出表头和内容，输出序号、空间相对位置、室内边界声级、建筑物外噪声等列

## 2026-03-24 - Add building polygons, popup editing and theme switching

- 将设备噪声参数从常驻侧边栏改为点击新增设备或点击已有设备时的弹窗式填写/编辑流程
- 新增建筑物多点描绘能力，可在左侧建筑物列表中选中并编辑建筑物名称与插入损失
- 新增建筑物关联和四方向室内边界距离计算，室内边界声级与建筑物外噪声改为按东南西北分别输出
- 比例尺改为隐藏式设置面板，并新增暖砂、森林、青灰三套界面主题

## 2026-03-24 - Replace system popups with in-page dialogs and add redo

- 将设备新增/编辑、建筑物参数编辑改为页面中央弹出式表单，去掉浏览器默认 `prompt`
- 将清空全部、清空建筑物、清除自动保存、导入覆盖等操作改为页面中央确认对话框，去掉浏览器默认 `confirm`
- 新增统一的页面消息弹窗，替换关键流程中的默认 `alert`
- 增加“恢复撤销”操作，并为撤销/恢复维护独立状态栈

## 2026-03-24 - Add vertex editing and device drag operations

- 为建筑物新增顶点编辑模式，可选中单个顶点并拖拽位置，也可删除单个顶点且保留最少 3 个点
- 为设备新增选择态，支持单击选中、双击编辑、复制设备、删除设备和拖拽移动
- 扩展工程快照与恢复逻辑，保存选中设备、选中建筑物、顶点编辑状态，保证撤销/恢复对新交互同样生效

## 2026-03-24 - Add vertex insertion, context menu and canvas navigation

- 为建筑物新增边线插点能力，可在右键菜单中直接插入新顶点并切换到顶点编辑
- 为设备和建筑物新增右键菜单，常用操作如编辑、复制、删除、插点可直接触发
- 为画布新增滚轮缩放与按住空格拖动平移，提升复杂总图下的浏览和编辑体验
