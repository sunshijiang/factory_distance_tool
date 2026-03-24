# Windows EXE 打包说明

当前项目主程序是：

- `app.py`

Windows 上生成 `exe` 的最简方式：

1. 把整个 `factory_distance_tool` 文件夹复制到 Windows 电脑
2. 安装 Python 3.10 或更高版本
3. 双击运行 `build_windows.bat`
4. 打包完成后，在 `dist\FactoryDistanceTool_v1.0.0.exe` 找到可执行文件

## 运行方式

双击 `FactoryDistanceTool_v1.0.0.exe` 后，程序会启动本地服务并自动打开浏览器。

默认地址：

- `http://127.0.0.1:8765`

如果需要局域网访问，可以在命令行运行：

```bat
FactoryDistanceTool_v1.0.0.exe --host 0.0.0.0 --port 8765
```

然后在同一局域网其他设备访问：

- `http://你的Windows电脑IP:8765`

## 为什么这里不能直接给出 exe

当前开发环境是 Linux，不是 Windows。
`PyInstaller` 默认只能在目标系统上打包对应系统的可执行文件：

- Linux 上打包出 Linux 可执行文件
- Windows 上打包出 Windows `exe`

所以要产出可直接运行的 Windows `exe`，需要在 Windows 环境执行打包。
