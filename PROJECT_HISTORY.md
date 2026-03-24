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
