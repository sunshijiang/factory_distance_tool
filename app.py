#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import http.server
import socketserver
import threading
import webbrowser


# Frontend single-page app: UI, state, drawing, import/export, and autosave.
HTML = r"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>设备与厂界距离测算工具</title>
  <style>
    :root {
      --bg: #f4efe6;
      --panel: #fffaf2;
      --panel-2: #f8f1e4;
      --line: #dbcdb3;
      --text: #2f2418;
      --muted: #6e5b48;
      --accent: #c45d24;
      --accent-2: #225b54;
      --danger: #a63737;
      --shadow: 0 14px 32px rgba(78, 56, 27, 0.12);
    }

    :root[data-theme="forest"] {
      --bg: #edf4ef;
      --panel: #f8fffa;
      --panel-2: #ebf6ee;
      --line: #bfd5c4;
      --text: #1f3124;
      --muted: #51685a;
      --accent: #b8662b;
      --accent-2: #2f6d4f;
      --danger: #b03e3e;
      --shadow: 0 14px 32px rgba(36, 76, 52, 0.12);
    }

    :root[data-theme="slate"] {
      --bg: #eef2f6;
      --panel: #fbfdff;
      --panel-2: #edf3f8;
      --line: #c6d1dc;
      --text: #20303f;
      --muted: #5b7083;
      --accent: #d36c37;
      --accent-2: #35607f;
      --danger: #b54949;
      --shadow: 0 14px 32px rgba(44, 69, 92, 0.12);
    }

    * { box-sizing: border-box; }

    body {
      margin: 0;
      font-family: "Microsoft YaHei", "PingFang SC", "Noto Sans SC", sans-serif;
      background:
        radial-gradient(circle at top left, rgba(196, 93, 36, 0.18), transparent 30%),
        radial-gradient(circle at bottom right, rgba(34, 91, 84, 0.14), transparent 28%),
        var(--bg);
      color: var(--text);
    }

    .app {
      display: grid;
      grid-template-columns: 320px minmax(0, 1fr);
      min-height: 100vh;
      gap: 18px;
      padding: 18px;
    }

    .panel {
      background: rgba(255, 250, 242, 0.92);
      border: 1px solid rgba(219, 205, 179, 0.9);
      border-radius: 20px;
      padding: 18px;
      box-shadow: var(--shadow);
      backdrop-filter: blur(6px);
    }

    .sidebar {
      display: flex;
      flex-direction: column;
      gap: 14px;
      position: sticky;
      top: 18px;
      height: calc(100vh - 36px);
      overflow: auto;
    }

    .section {
      border: 1px solid var(--line);
      border-radius: 16px;
      padding: 14px;
      background: linear-gradient(180deg, rgba(255,255,255,0.62), rgba(248,241,228,0.62));
    }

    .section h3 {
      margin: 0 0 10px;
      font-size: 15px;
      letter-spacing: 0.04em;
    }

    .muted {
      color: var(--muted);
      font-size: 12px;
      line-height: 1.5;
    }

    .field {
      display: grid;
      gap: 6px;
      margin-bottom: 10px;
    }

    .field label {
      font-size: 12px;
      color: var(--muted);
    }

    .hidden {
      display: none;
    }

    input[type="number"],
    input[type="text"],
    input[type="file"] {
      width: 100%;
      border: 1px solid var(--line);
      background: white;
      border-radius: 12px;
      padding: 10px 12px;
      font-size: 14px;
      color: var(--text);
    }

    input[type="file"] {
      padding: 9px 12px;
    }

    .btn-grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 8px;
    }

    button {
      border: 0;
      border-radius: 12px;
      padding: 10px 12px;
      font-size: 13px;
      font-weight: 600;
      color: white;
      background: var(--accent-2);
      cursor: pointer;
      transition: transform 120ms ease, opacity 120ms ease, box-shadow 120ms ease;
      box-shadow: 0 8px 18px rgba(34, 91, 84, 0.2);
    }

    button:hover {
      transform: translateY(-1px);
    }

    button.secondary {
      background: #8f6f48;
      box-shadow: 0 8px 18px rgba(99, 75, 47, 0.2);
    }

    button.warn {
      background: var(--danger);
      box-shadow: 0 8px 18px rgba(166, 55, 55, 0.18);
    }

    button.active {
      background: var(--accent);
      box-shadow: 0 10px 20px rgba(196, 93, 36, 0.24);
    }

    .status-card {
      display: grid;
      gap: 8px;
      font-size: 13px;
    }

    .status-row {
      display: flex;
      justify-content: space-between;
      gap: 10px;
      padding-bottom: 8px;
      border-bottom: 1px dashed rgba(110, 91, 72, 0.24);
    }

    .status-row:last-child {
      border-bottom: 0;
      padding-bottom: 0;
    }

    .status-key {
      color: var(--muted);
    }

    .canvas-panel {
      display: grid;
      grid-template-rows: auto minmax(0, 1fr);
      gap: 12px;
      min-height: 0;
    }

    .toolbar {
      display: flex;
      justify-content: space-between;
      gap: 12px;
      align-items: center;
      flex-wrap: wrap;
      font-size: 13px;
    }

    .toolbar strong {
      font-size: 16px;
      font-weight: 700;
    }

    .canvas-wrap {
      position: relative;
      background:
        linear-gradient(90deg, rgba(143, 111, 72, 0.08) 1px, transparent 1px),
        linear-gradient(rgba(143, 111, 72, 0.08) 1px, transparent 1px),
        linear-gradient(180deg, #fffaf2, #f3eadb);
      background-size: 24px 24px, 24px 24px, 100% 100%;
      border-radius: 18px;
      border: 1px solid rgba(219, 205, 179, 0.95);
      overflow: auto;
      min-height: 0;
      box-shadow: var(--shadow);
    }

    canvas {
      display: block;
      background: transparent;
      cursor: crosshair;
    }

    .placeholder {
      position: absolute;
      inset: 0;
      display: grid;
      place-items: center;
      pointer-events: none;
      color: var(--muted);
      font-size: 16px;
      text-align: center;
      padding: 24px;
      line-height: 1.7;
    }

    .tooltip {
      position: fixed;
      z-index: 20;
      max-width: 240px;
      pointer-events: none;
      padding: 12px 14px;
      border-radius: 14px;
      background: rgba(37, 28, 19, 0.95);
      color: #fef7ed;
      font-size: 12px;
      line-height: 1.6;
      box-shadow: 0 12px 32px rgba(19, 14, 10, 0.22);
      display: none;
      white-space: pre-line;
    }

    .legend {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      font-size: 12px;
      color: var(--muted);
    }

    .legend span {
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }

    .scale-summary {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 10px;
      margin-bottom: 8px;
    }

    .theme-grid,
    .building-actions {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 8px;
    }

    .theme-grid button {
      padding: 9px 10px;
    }

    .building-list {
      display: grid;
      gap: 8px;
      margin-top: 10px;
      max-height: 180px;
      overflow: auto;
    }

    .building-item {
      width: 100%;
      text-align: left;
      background: rgba(255, 255, 255, 0.8);
      color: var(--text);
      border: 1px solid var(--line);
      box-shadow: none;
    }

    .building-item.active {
      color: white;
      background: var(--accent-2);
      border-color: transparent;
    }

    .dot {
      width: 10px;
      height: 10px;
      border-radius: 999px;
      display: inline-block;
    }

    @media (max-width: 980px) {
      .app {
        grid-template-columns: 1fr;
      }

      .sidebar {
        position: static;
        height: auto;
      }
    }
  </style>
</head>
<body>
  <div class="app">
    <aside class="panel sidebar">
      <div class="section">
        <h3>图片</h3>
        <div class="field">
          <label for="imageInput">上传厂区截图</label>
          <input id="imageInput" type="file" accept=".png,.jpg,.jpeg,image/png,image/jpeg">
        </div>
        <div class="muted">支持 PNG/JPG。图片会随工程一起保存。重新上传会清空现有比例尺、厂界和设备点。</div>
      </div>

      <div class="section">
        <h3>工程</h3>
        <div class="field">
          <label for="projectName">工程名称</label>
          <input id="projectName" type="text" value="未命名工程">
        </div>
        <div class="btn-grid">
          <button id="exportProject">导出工程</button>
          <button id="importProjectButton" class="secondary">导入工程</button>
        </div>
        <div class="btn-grid" style="margin-top: 8px;">
          <button id="exportCsv">导出CSV</button>
          <button id="restoreAutosave" class="secondary">恢复自动保存</button>
        </div>
        <div class="btn-grid" style="margin-top: 8px;">
          <button id="clearAutosave" class="secondary">清除自动保存</button>
        </div>
        <input id="projectImportInput" type="file" accept=".json,application/json" style="display: none;">
        <div class="muted" id="autosaveStatus">自动保存：等待首次修改</div>
      </div>

      <div class="section">
        <h3>比例尺</h3>
        <div class="scale-summary">
          <button id="toggleScalePanel" class="secondary" type="button">比例尺设置</button>
          <div class="muted" id="scaleSummaryText">未设置</div>
        </div>
        <div id="scalePanel" class="hidden">
        <div class="field">
          <label for="actualLength">实际长度</label>
          <input id="actualLength" type="number" min="0" step="0.01" value="10">
        </div>
        <div class="field">
          <label for="unitInput">单位</label>
          <input id="unitInput" type="text" value="米">
        </div>
        <div class="btn-grid">
          <button id="modeScale">设置尺寸</button>
          <button id="clearScale" class="secondary">清除尺寸</button>
        </div>
        <div class="muted">点击图片上的两个点，作为参考线段。系统会根据“实际长度”建立像素与真实距离的换算比例。</div>
        </div>
      </div>

      <div class="section">
        <h3>坐标原点</h3>
        <div class="btn-grid">
          <button id="modeOrigin">设置原点</button>
          <button id="clearOrigin" class="secondary">清除原点</button>
        </div>
        <div class="muted">点击“设置原点”后，在图片上单击一次即可设定坐标原点。设备坐标按 X 向右为正、Y 向上为正计算。</div>
      </div>

      <div class="section">
        <h3>厂界</h3>
        <div class="btn-grid">
          <button id="modeEast">东厂界</button>
          <button id="modeSouth">南厂界</button>
          <button id="modeWest">西厂界</button>
          <button id="modeNorth">北厂界</button>
        </div>
        <div class="muted">选择一个方向后，在图片上点击两个点绘制该方向的一段边界线。同一方向可以连续添加多段线，适用于不规则厂房。</div>
      </div>

      <div class="section">
        <h3>设备</h3>
        <div class="btn-grid">
          <button id="modeDevice">添加设备</button>
          <button id="cancelPending" class="secondary">取消当前操作</button>
        </div>
        <div class="btn-grid" style="margin-top: 8px;">
          <button id="undoAction" class="secondary">撤销最近一步</button>
          <button id="clearAll" class="warn">清空全部</button>
        </div>
        <div class="muted">添加设备模式下，点击图片即可放置声源点，并弹出设备信息填写窗口。点击已有设备可再次编辑型号、声功率级等信息。鼠标悬停在设备点上可以查看厂界距离和噪声结果。</div>
      </div>

      <div class="section hidden" id="noiseDraftSection">
        <h3>噪声参数</h3>
        <div class="field">
          <label for="buildingNameInput">建筑物名称</label>
          <input id="buildingNameInput" type="text" value="建筑物1">
        </div>
        <div class="field">
          <label for="sourceNameInput">声源名称</label>
          <input id="sourceNameInput" type="text" value="设备1">
        </div>
        <div class="field">
          <label for="sourceModelInput">型号</label>
          <input id="sourceModelInput" type="text" value="">
        </div>
        <div class="field">
          <label for="soundPowerLevelInput">声功率级 dB(A)</label>
          <input id="soundPowerLevelInput" type="number" step="0.01" value="90">
        </div>
        <div class="field">
          <label for="controlMeasuresInput">声源控制措施</label>
          <input id="controlMeasuresInput" type="text" value="">
        </div>
        <div class="field">
          <label for="indoorBoundaryDistanceInput">距室内边界距离</label>
          <input id="indoorBoundaryDistanceInput" type="number" min="0.01" step="0.01" value="1">
        </div>
        <div class="field">
          <label for="runtimePeriodInput">运行时段</label>
          <input id="runtimePeriodInput" type="text" value="昼间">
        </div>
        <div class="field">
          <label for="buildingInsertionLossInput">建筑物插入损失 dB(A)</label>
          <input id="buildingInsertionLossInput" type="number" step="0.01" value="21">
        </div>
        <div class="field">
          <label for="outdoorDistanceInput">建筑物外距离</label>
          <input id="outdoorDistanceInput" type="number" min="0.01" step="0.01" value="1">
        </div>
        <div class="field">
          <label for="sourceHeightInput">相对高度 Z</label>
          <input id="sourceHeightInput" type="number" step="0.01" value="0">
        </div>
        <div class="muted">新增声源时会同时记录建筑物名称、声功率级、距室内边界距离、插入损失、建筑物外距离和相对高度 Z，并在 CSV 中计算室内边界声级与建筑物外噪声。</div>
      </div>

      <div class="section">
        <h3>建筑物</h3>
        <div class="building-actions">
          <button id="modeBuilding">绘制建筑物</button>
          <button id="finishBuilding" class="secondary">完成描绘</button>
          <button id="editBuilding" class="secondary">编辑建筑物</button>
          <button id="clearBuildings" class="secondary">清空建筑物</button>
        </div>
        <div class="muted" style="margin-top: 8px;">使用多点依次描绘建筑物轮廓，完成后录入建筑物名称和插入损失。浏览模式下可从列表再次编辑。</div>
        <div id="buildingList" class="building-list"></div>
      </div>

      <div class="section">
        <h3>主题</h3>
        <div class="theme-grid">
          <button id="themeSand" class="secondary" type="button">暖砂</button>
          <button id="themeForest" class="secondary" type="button">森林</button>
          <button id="themeSlate" class="secondary" type="button">青灰</button>
        </div>
      </div>

      <div class="section">
        <h3>状态</h3>
        <div class="status-card">
          <div class="status-row"><span class="status-key">工程名称</span><strong id="statusProject">未命名工程</strong></div>
          <div class="status-row"><span class="status-key">当前模式</span><strong id="statusMode">浏览</strong></div>
          <div class="status-row"><span class="status-key">自动保存</span><strong id="statusSaved">未保存</strong></div>
          <div class="status-row"><span class="status-key">比例尺</span><strong id="statusScale">未设置</strong></div>
          <div class="status-row"><span class="status-key">坐标原点</span><strong id="statusOrigin">未设置</strong></div>
          <div class="status-row"><span class="status-key">厂界完成</span><strong id="statusBoundaries">0 / 4</strong></div>
          <div class="status-row"><span class="status-key">设备数量</span><strong id="statusDevices">0</strong></div>
          <div class="status-row"><span class="status-key">图片尺寸</span><strong id="statusImage">未上传</strong></div>
        </div>
      </div>
    </aside>

    <main class="canvas-panel">
      <section class="panel toolbar">
        <div>
          <strong>设备与厂界距离测算</strong>
          <div class="muted">单文件本地版。所有计算都基于原始图片坐标，不依赖后端服务。</div>
        </div>
        <div class="legend">
          <span><i class="dot" style="background:#da5a36"></i>比例尺</span>
          <span><i class="dot" style="background:#0f6bd8"></i>原点</span>
          <span><i class="dot" style="background:#248f85"></i>东</span>
          <span><i class="dot" style="background:#c28c16"></i>南</span>
          <span><i class="dot" style="background:#7e57c2"></i>西</span>
          <span><i class="dot" style="background:#b83b5e"></i>北</span>
          <span><i class="dot" style="background:#1a1a1a"></i>设备</span>
        </div>
      </section>

      <section class="canvas-wrap panel" id="canvasWrap">
        <canvas id="mainCanvas" width="1200" height="800"></canvas>
        <div class="placeholder" id="placeholder">
          先上传一张厂区截图，然后依次完成比例尺、厂界和设备点标注。<br>
          建议使用鼠标进行绘制，厂界距离按“点到线段最短距离”计算。
        </div>
      </section>
    </main>
  </div>

  <div class="tooltip" id="tooltip"></div>

  <script>
    // Persistent storage configuration.
    const AUTOSAVE_CONFIG = {
      dbName: 'factory-distance-tool',
      storeName: 'projects',
      autosaveKey: 'autosave',
      version: 1
    };

    const canvas = document.getElementById('mainCanvas');
    const ctx = canvas.getContext('2d');
    const tooltip = document.getElementById('tooltip');
    const placeholder = document.getElementById('placeholder');

    const imageInput = document.getElementById('imageInput');
    const projectNameInput = document.getElementById('projectName');
    const projectImportInput = document.getElementById('projectImportInput');
    const actualLengthInput = document.getElementById('actualLength');
    const unitInput = document.getElementById('unitInput');
    const scalePanel = document.getElementById('scalePanel');
    const scaleSummaryText = document.getElementById('scaleSummaryText');
    const buildingNameInput = document.getElementById('buildingNameInput');
    const sourceNameInput = document.getElementById('sourceNameInput');
    const sourceModelInput = document.getElementById('sourceModelInput');
    const soundPowerLevelInput = document.getElementById('soundPowerLevelInput');
    const controlMeasuresInput = document.getElementById('controlMeasuresInput');
    const indoorBoundaryDistanceInput = document.getElementById('indoorBoundaryDistanceInput');
    const runtimePeriodInput = document.getElementById('runtimePeriodInput');
    const buildingInsertionLossInput = document.getElementById('buildingInsertionLossInput');
    const outdoorDistanceInput = document.getElementById('outdoorDistanceInput');
    const sourceHeightInput = document.getElementById('sourceHeightInput');
    const buildingList = document.getElementById('buildingList');
    const autosaveStatus = document.getElementById('autosaveStatus');

    const statusProject = document.getElementById('statusProject');
    const statusMode = document.getElementById('statusMode');
    const statusSaved = document.getElementById('statusSaved');
    const statusScale = document.getElementById('statusScale');
    const statusOrigin = document.getElementById('statusOrigin');
    const statusBoundaries = document.getElementById('statusBoundaries');
    const statusDevices = document.getElementById('statusDevices');
    const statusImage = document.getElementById('statusImage');

    const buttons = {
      scale: document.getElementById('modeScale'),
      origin: document.getElementById('modeOrigin'),
      east: document.getElementById('modeEast'),
      south: document.getElementById('modeSouth'),
      west: document.getElementById('modeWest'),
      north: document.getElementById('modeNorth'),
      device: document.getElementById('modeDevice'),
      building: document.getElementById('modeBuilding')
    };

    const themeButtons = {
      sand: document.getElementById('themeSand'),
      forest: document.getElementById('themeForest'),
      slate: document.getElementById('themeSlate')
    };

    const BOUNDARY_META = {
      east: { label: '东厂界', color: '#248f85', shortLabel: '东' },
      south: { label: '南厂界', color: '#c28c16', shortLabel: '南' },
      west: { label: '西厂界', color: '#7e57c2', shortLabel: '西' },
      north: { label: '北厂界', color: '#b83b5e', shortLabel: '北' }
    };

    // Runtime state for the current project and canvas interaction.
    function createEmptyBoundaries() {
      return {
        east: [],
        south: [],
        west: [],
        north: []
      };
    }

    function createDefaultDeviceDraft() {
      return {
        sourceName: '设备1',
        model: '',
        soundPowerLevel: 90,
        controlMeasures: '',
        runtimePeriod: '昼间',
        outdoorDistance: 1,
        z: 0
      };
    }

    const state = {
      image: null,
      imageName: '',
      imageDataUrl: '',
      projectName: projectNameInput.value.trim() || '未命名工程',
      mode: 'browse',
      pendingPoint: null,
      lastMousePoint: null,
      scale: null,
      origin: null,
      boundaries: createEmptyBoundaries(),
      buildings: [],
      devices: [],
      selectedBuildingId: null,
      hoveredDeviceId: null,
      pendingBuildingPoints: [],
      theme: 'sand',
      deviceDraft: createDefaultDeviceDraft(),
      history: [],
      lastSavedAt: null
    };

    let dbPromise = null;
    let autosaveTimer = null;
    let suppressAutosave = false;

    // Data normalization keeps imported/autosaved payloads backward compatible.
    function deepClone(value) {
      return JSON.parse(JSON.stringify(value));
    }

    function normalizeSegment(segment) {
      if (!segment || !segment.start || !segment.end) {
        return null;
      }
      if (!Number.isFinite(segment.start.x) || !Number.isFinite(segment.start.y) ||
          !Number.isFinite(segment.end.x) || !Number.isFinite(segment.end.y)) {
        return null;
      }
      return {
        id: segment.id || `seg-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
        start: { x: Number(segment.start.x), y: Number(segment.start.y) },
        end: { x: Number(segment.end.x), y: Number(segment.end.y) }
      };
    }

    function normalizeSegments(value) {
      if (Array.isArray(value)) {
        return value.map(normalizeSegment).filter(Boolean);
      }
      const single = normalizeSegment(value);
      return single ? [single] : [];
    }

    function normalizeBoundaries(boundaries) {
      const source = boundaries || {};
      return {
        east: normalizeSegments(source.east),
        south: normalizeSegments(source.south),
        west: normalizeSegments(source.west),
        north: normalizeSegments(source.north)
      };
    }

    function normalizeDevices(devices) {
      if (!Array.isArray(devices)) {
        return [];
      }
      return devices
        .map((device, index) => {
          if (!device || !Number.isFinite(device.x) || !Number.isFinite(device.y)) {
            return null;
          }
          return {
            id: device.id || `dev-import-${Date.now()}-${index}`,
            name: (device.name || device.sourceName || '').trim() || `设备${index + 1}`,
            buildingId: device.buildingId || null,
            buildingName: (device.buildingName || '').trim() || '',
            sourceName: (device.sourceName || device.name || '').trim() || `设备${index + 1}`,
            model: (device.model || '').trim(),
            soundPowerLevel: Number.isFinite(Number(device.soundPowerLevel)) ? Number(device.soundPowerLevel) : 90,
            controlMeasures: (device.controlMeasures || '').trim(),
            runtimePeriod: (device.runtimePeriod || '').trim() || '昼间',
            outdoorDistance: Number.isFinite(Number(device.outdoorDistance)) && Number(device.outdoorDistance) > 0 ? Number(device.outdoorDistance) : 1,
            z: Number.isFinite(Number(device.z)) ? Number(device.z) : 0,
            x: Number(device.x),
            y: Number(device.y)
          };
        })
        .filter(Boolean);
    }

    function normalizeBuildings(buildings) {
      if (!Array.isArray(buildings)) {
        return [];
      }
      return buildings.map((building, index) => {
        if (!building || !Array.isArray(building.points) || building.points.length < 3) {
          return null;
        }
        const points = building.points.map(normalizePoint).filter(Boolean);
        if (points.length < 3) {
          return null;
        }
        return {
          id: building.id || `bld-${Date.now()}-${index}`,
          name: (building.name || '').trim() || `建筑物${index + 1}`,
          insertionLoss: Number.isFinite(Number(building.insertionLoss)) ? Number(building.insertionLoss) : 21,
          points
        };
      }).filter(Boolean);
    }

    function normalizeScale(scale) {
      if (!scale || !scale.start || !scale.end) {
        return null;
      }
      if (!Number.isFinite(scale.start.x) || !Number.isFinite(scale.start.y) ||
          !Number.isFinite(scale.end.x) || !Number.isFinite(scale.end.y) ||
          !Number.isFinite(scale.pixelDistance) || !Number.isFinite(scale.actualDistance) ||
          !Number.isFinite(scale.scale)) {
        return null;
      }
      return {
        start: { x: Number(scale.start.x), y: Number(scale.start.y) },
        end: { x: Number(scale.end.x), y: Number(scale.end.y) },
        pixelDistance: Number(scale.pixelDistance),
        actualDistance: Number(scale.actualDistance),
        unit: (scale.unit || '米').trim() || '米',
        scale: Number(scale.scale)
      };
    }

    function normalizePoint(point) {
      if (!point || !Number.isFinite(point.x) || !Number.isFinite(point.y)) {
        return null;
      }
      return { x: Number(point.x), y: Number(point.y) };
    }

    function normalizeProjectData(raw) {
      const normalizedScale = normalizeScale(raw && raw.scale);
      const draftScaleInputs = (raw && raw.draftScaleInputs) || {};
      const draftSourceInputs = (raw && raw.draftSourceInputs) || {};
      const mode = raw && typeof raw.mode === 'string' ? raw.mode : 'browse';
      const allowedModes = ['browse', 'scale', 'origin', 'device', 'building', 'east', 'south', 'west', 'north'];

      return {
        version: raw && raw.version ? raw.version : 1,
        savedAt: raw && raw.savedAt ? raw.savedAt : null,
        projectName: ((raw && raw.projectName) || '未命名工程').trim() || '未命名工程',
        imageName: (raw && raw.imageName) || '',
        imageDataUrl: (raw && raw.imageDataUrl) || '',
        mode: allowedModes.includes(mode) ? mode : 'browse',
        pendingPoint: normalizePoint(raw && raw.pendingPoint),
        pendingBuildingPoints: Array.isArray(raw && raw.pendingBuildingPoints) ? raw.pendingBuildingPoints.map(normalizePoint).filter(Boolean) : [],
        scale: normalizedScale,
        origin: normalizePoint(raw && raw.origin),
        boundaries: normalizeBoundaries(raw && raw.boundaries),
        buildings: normalizeBuildings(raw && raw.buildings),
        devices: normalizeDevices(raw && raw.devices),
        selectedBuildingId: raw && raw.selectedBuildingId ? raw.selectedBuildingId : null,
        theme: ['sand', 'forest', 'slate'].includes(raw && raw.theme) ? raw.theme : 'sand',
        draftScaleInputs: {
          actualLength: String(draftScaleInputs.actualLength ?? (normalizedScale ? normalizedScale.actualDistance : actualLengthInput.value || '10')),
          unit: String(draftScaleInputs.unit ?? (normalizedScale ? normalizedScale.unit : unitInput.value || '米'))
        },
        draftSourceInputs: {
          sourceName: String(draftSourceInputs.sourceName ?? (sourceNameInput.value || '设备1')),
          model: String(draftSourceInputs.model ?? (sourceModelInput.value || '')),
          soundPowerLevel: String(draftSourceInputs.soundPowerLevel ?? (soundPowerLevelInput.value || '90')),
          controlMeasures: String(draftSourceInputs.controlMeasures ?? (controlMeasuresInput.value || '')),
          runtimePeriod: String(draftSourceInputs.runtimePeriod ?? (runtimePeriodInput.value || '昼间')),
          outdoorDistance: String(draftSourceInputs.outdoorDistance ?? (outdoorDistanceInput.value || '1')),
          z: String(draftSourceInputs.z ?? (sourceHeightInput.value || '0'))
        }
      };
    }

    // UI status sync.
    function setSaveState(summary, detail) {
      statusSaved.textContent = summary;
      autosaveStatus.textContent = detail;
    }

    function applyTheme() {
      document.documentElement.setAttribute('data-theme', state.theme);
    }

    function renderBuildingList() {
      buildingList.innerHTML = '';
      if (!state.buildings.length) {
        const empty = document.createElement('div');
        empty.className = 'muted';
        empty.textContent = '暂无建筑物';
        buildingList.appendChild(empty);
        return;
      }

      state.buildings.forEach((building) => {
        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'building-item' + (state.selectedBuildingId === building.id ? ' active' : '');
        button.textContent = `${building.name} | IL ${formatNumber(building.insertionLoss)} dB(A)`;
        button.addEventListener('click', () => {
          state.selectedBuildingId = building.id;
          syncUiAfterStateChange();
          editSelectedBuilding();
        });
        buildingList.appendChild(button);
      });
    }

    function formatTimestamp(isoString) {
      if (!isoString) {
        return '';
      }
      const date = new Date(isoString);
      if (Number.isNaN(date.getTime())) {
        return '';
      }
      return date.toLocaleString('zh-CN', { hour12: false });
    }

    function refreshSaveStatus() {
      if (state.lastSavedAt) {
        const formatted = formatTimestamp(state.lastSavedAt);
        setSaveState(formatted || '已保存', `自动保存：已保存于 ${formatted || state.lastSavedAt}`);
      } else {
        setSaveState('未保存', '自动保存：等待首次修改');
      }
    }

    function markSavePending() {
      setSaveState('待保存', '自动保存：检测到修改，正在等待保存');
    }

    function markSaveUnavailable(message) {
      setSaveState('不可用', `自动保存：${message}`);
    }

    function updateButtons() {
      Object.values(buttons).forEach((button) => button.classList.remove('active'));
      if (state.mode === 'scale') buttons.scale.classList.add('active');
      if (state.mode === 'origin') buttons.origin.classList.add('active');
      if (state.mode === 'device') buttons.device.classList.add('active');
      if (state.mode === 'building') buttons.building.classList.add('active');
      if (BOUNDARY_META[state.mode]) buttons[state.mode].classList.add('active');
      canvas.style.cursor = state.image ? (state.mode === 'browse' ? 'default' : 'crosshair') : 'not-allowed';
      Object.entries(themeButtons).forEach(([key, button]) => {
        button.classList.toggle('active', state.theme === key);
      });
    }

    function updateStatus() {
      const modeText = {
        browse: '浏览',
        scale: '设置尺寸',
        origin: '设置原点',
        device: '添加设备',
        building: '绘制建筑物',
        east: '绘制东厂界',
        south: '绘制南厂界',
        west: '绘制西厂界',
        north: '绘制北厂界'
      };

      statusProject.textContent = state.projectName || '未命名工程';
      statusMode.textContent = modeText[state.mode] || '浏览';

      if (state.scale) {
        statusScale.textContent = `已设置 (${state.scale.actualDistance} ${state.scale.unit})`;
        scaleSummaryText.textContent = `${state.scale.actualDistance} ${state.scale.unit}`;
      } else {
        statusScale.textContent = '未设置';
        scaleSummaryText.textContent = '未设置';
      }

      if (state.origin) {
        statusOrigin.textContent = `(${state.origin.x.toFixed(0)}, ${state.origin.y.toFixed(0)})`;
      } else {
        statusOrigin.textContent = '未设置';
      }

      const completedDirections = Object.values(state.boundaries).filter((segments) => segments.length > 0).length;
      const totalSegments = Object.values(state.boundaries).reduce((sum, segments) => sum + segments.length, 0);
      statusBoundaries.textContent = `${completedDirections} / 4 方向，${totalSegments} 段，建筑物 ${state.buildings.length}`;
      statusDevices.textContent = String(state.devices.length);
      statusImage.textContent = state.image ? `${state.image.width} × ${state.image.height}` : '未上传';
      placeholder.style.display = state.image ? 'none' : 'grid';
    }

    function syncUiAfterStateChange() {
      projectNameInput.value = state.projectName;
      updateButtons();
      updateStatus();
      renderBuildingList();
      applyTheme();
      render();
    }

    // Project serialization and local autosave.
    function getDraftScaleInputs() {
      return {
        actualLength: actualLengthInput.value || '10',
        unit: (unitInput.value || '米').trim() || '米'
      };
    }

    function getDraftSourceInputs() {
      const draft = state.deviceDraft || createDefaultDeviceDraft();
      return {
        sourceName: draft.sourceName || '设备1',
        model: draft.model || '',
        soundPowerLevel: String(draft.soundPowerLevel ?? 90),
        controlMeasures: draft.controlMeasures || '',
        runtimePeriod: draft.runtimePeriod || '昼间',
        outdoorDistance: String(draft.outdoorDistance ?? 1),
        z: String(draft.z ?? 0)
      };
    }

    function buildProjectPayload() {
      return {
        version: 2,
        savedAt: new Date().toISOString(),
        projectName: state.projectName || '未命名工程',
        imageName: state.imageName,
        imageDataUrl: state.imageDataUrl,
        mode: state.mode,
        pendingPoint: state.pendingPoint ? deepClone(state.pendingPoint) : null,
        pendingBuildingPoints: deepClone(state.pendingBuildingPoints),
        scale: state.scale ? deepClone(state.scale) : null,
        origin: state.origin ? deepClone(state.origin) : null,
        boundaries: deepClone(state.boundaries),
        buildings: deepClone(state.buildings),
        devices: deepClone(state.devices),
        selectedBuildingId: state.selectedBuildingId,
        theme: state.theme,
        draftScaleInputs: getDraftScaleInputs(),
        draftSourceInputs: getDraftSourceInputs()
      };
    }

    function hasProjectContent() {
      const hasBoundaries = Object.values(state.boundaries).some((segments) => segments.length > 0);
      return Boolean(state.imageDataUrl || state.scale || state.origin || hasBoundaries || state.devices.length || state.buildings.length || state.pendingPoint || state.pendingBuildingPoints.length);
    }

    function saveHistory() {
      state.history.push(JSON.stringify({
        scale: state.scale,
        origin: state.origin,
        boundaries: state.boundaries,
        buildings: state.buildings,
        devices: state.devices,
        selectedBuildingId: state.selectedBuildingId
      }));
      if (state.history.length > 50) {
        state.history.shift();
      }
    }

    function scheduleAutosave() {
      if (suppressAutosave) {
        return;
      }
      if (!window.indexedDB) {
        markSaveUnavailable('当前浏览器不支持 IndexedDB，请使用导出工程');
        return;
      }
      clearTimeout(autosaveTimer);
      markSavePending();
      autosaveTimer = window.setTimeout(() => {
        saveAutosaveNow().catch((error) => {
          console.error(error);
          setSaveState('失败', `自动保存：保存失败，${error.message || error}`);
        });
      }, 250);
    }

    function createStoreRequest(mode, executor) {
      return openProjectDb().then((db) => {
        if (!db) {
          return null;
        }
        return new Promise((resolve, reject) => {
          const tx = db.transaction(AUTOSAVE_CONFIG.storeName, mode);
          const store = tx.objectStore(AUTOSAVE_CONFIG.storeName);
          const request = executor(store);
          tx.oncomplete = () => resolve(request ? request.result : undefined);
          tx.onerror = () => reject(tx.error || request.error || new Error('数据库操作失败'));
          tx.onabort = () => reject(tx.error || new Error('数据库操作已取消'));
        });
      });
    }

    function openProjectDb() {
      if (!window.indexedDB) {
        return Promise.resolve(null);
      }
      if (!dbPromise) {
        dbPromise = new Promise((resolve, reject) => {
          const request = indexedDB.open(AUTOSAVE_CONFIG.dbName, AUTOSAVE_CONFIG.version);
          request.onupgradeneeded = () => {
            const db = request.result;
            if (!db.objectStoreNames.contains(AUTOSAVE_CONFIG.storeName)) {
              db.createObjectStore(AUTOSAVE_CONFIG.storeName);
            }
          };
          request.onsuccess = () => resolve(request.result);
          request.onerror = () => reject(request.error || new Error('无法打开自动保存数据库'));
        });
      }
      return dbPromise;
    }

    async function saveAutosaveNow() {
      if (suppressAutosave) {
        return;
      }
      const payload = buildProjectPayload();
      await createStoreRequest('readwrite', (store) => store.put(payload, AUTOSAVE_CONFIG.autosaveKey));
      state.lastSavedAt = payload.savedAt;
      refreshSaveStatus();
    }

    async function clearAutosaveData() {
      await createStoreRequest('readwrite', (store) => store.delete(AUTOSAVE_CONFIG.autosaveKey));
    }

    async function readAutosaveData() {
      return createStoreRequest('readonly', (store) => store.get(AUTOSAVE_CONFIG.autosaveKey));
    }

    // State mutation helpers and undo/reset controls.
    function resetAnnotations() {
      state.pendingPoint = null;
      state.lastMousePoint = null;
      state.scale = null;
      state.origin = null;
      state.boundaries = createEmptyBoundaries();
      state.buildings = [];
      state.devices = [];
      state.selectedBuildingId = null;
      state.hoveredDeviceId = null;
      state.pendingBuildingPoints = [];
      state.history = [];
      hideTooltip();
    }

    function setMode(nextMode, options = {}) {
      state.mode = nextMode;
      state.pendingPoint = null;
      if (nextMode !== 'building') {
        state.pendingBuildingPoints = [];
      }
      syncUiAfterStateChange();
      if (options.autosave !== false) {
        scheduleAutosave();
      }
    }

    function cancelCurrentOperation(options = {}) {
      const changed = state.mode !== 'browse' || Boolean(state.pendingPoint) || state.pendingBuildingPoints.length > 0;
      state.pendingPoint = null;
      state.pendingBuildingPoints = [];
      state.hoveredDeviceId = null;
      state.mode = 'browse';
      hideTooltip();
      syncUiAfterStateChange();
      if (changed && options.autosave !== false) {
        scheduleAutosave();
      }
    }

    function undoLastAction() {
      if (!state.history.length) {
        alert('没有可撤销的操作。');
        return;
      }
      const snapshot = JSON.parse(state.history.pop());
      state.scale = snapshot.scale;
      state.origin = normalizePoint(snapshot.origin);
      state.boundaries = normalizeBoundaries(snapshot.boundaries);
      state.buildings = normalizeBuildings(snapshot.buildings);
      state.devices = normalizeDevices(snapshot.devices);
      state.selectedBuildingId = snapshot.selectedBuildingId || null;
      state.pendingPoint = null;
      state.pendingBuildingPoints = [];
      state.hoveredDeviceId = null;
      hideTooltip();
      syncUiAfterStateChange();
      scheduleAutosave();
    }

    function resetAll() {
      if (!state.image) {
        return;
      }
      if (!confirm('确定要清空比例尺、厂界、建筑物和设备点吗？')) {
        return;
      }
      resetAnnotations();
      cancelCurrentOperation({ autosave: false });
      scheduleAutosave();
    }

    function clearScale() {
      if (!state.scale) {
        return;
      }
      saveHistory();
      state.scale = null;
      syncUiAfterStateChange();
      scheduleAutosave();
    }

    function clearOrigin() {
      if (!state.origin) {
        return;
      }
      saveHistory();
      state.origin = null;
      syncUiAfterStateChange();
      scheduleAutosave();
    }

    // Canvas rendering primitives.
    function getCanvasPoint(event) {
      const rect = canvas.getBoundingClientRect();
      const scaleX = canvas.width / rect.width;
      const scaleY = canvas.height / rect.height;
      return {
        x: (event.clientX - rect.left) * scaleX,
        y: (event.clientY - rect.top) * scaleY
      };
    }

    function distance(a, b) {
      return Math.hypot(a.x - b.x, a.y - b.y);
    }

    function drawCircle(point, color, radius) {
      ctx.beginPath();
      ctx.arc(point.x, point.y, radius, 0, Math.PI * 2);
      ctx.fillStyle = color;
      ctx.fill();
    }

    function drawLine(start, end, options) {
      ctx.save();
      ctx.lineWidth = options.width || 3;
      ctx.strokeStyle = options.color || '#000';
      ctx.setLineDash(options.dash || []);
      ctx.beginPath();
      ctx.moveTo(start.x, start.y);
      ctx.lineTo(end.x, end.y);
      ctx.stroke();
      ctx.restore();

      if (options.label) {
        const midX = (start.x + end.x) / 2;
        const midY = (start.y + end.y) / 2;
        ctx.save();
        ctx.font = 'bold 14px "Microsoft YaHei", sans-serif';
        const paddingX = 8;
        const textWidth = ctx.measureText(options.label).width;
        ctx.fillStyle = 'rgba(255, 250, 242, 0.92)';
        ctx.strokeStyle = 'rgba(47, 36, 24, 0.18)';
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.roundRect(midX - textWidth / 2 - paddingX, midY - 12, textWidth + paddingX * 2, 24, 10);
        ctx.fill();
        ctx.stroke();
        ctx.fillStyle = options.color || '#000';
        ctx.textBaseline = 'middle';
        ctx.fillText(options.label, midX - textWidth / 2, midY);
        ctx.restore();
      }
    }

    function render() {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      if (!state.image) {
        ctx.fillStyle = '#f8f1e4';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        return;
      }

      ctx.drawImage(state.image, 0, 0, canvas.width, canvas.height);

      if (state.scale) {
        drawLine(state.scale.start, state.scale.end, {
          color: '#da5a36',
          width: 4,
          label: `比例尺 ${state.scale.actualDistance} ${state.scale.unit}`
        });
        drawCircle(state.scale.start, '#da5a36', 4);
        drawCircle(state.scale.end, '#da5a36', 4);
      }

      if (state.origin) {
        const size = 10;
        ctx.save();
        ctx.strokeStyle = '#0f6bd8';
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.moveTo(state.origin.x - size, state.origin.y);
        ctx.lineTo(state.origin.x + size, state.origin.y);
        ctx.moveTo(state.origin.x, state.origin.y - size);
        ctx.lineTo(state.origin.x, state.origin.y + size);
        ctx.stroke();
        ctx.restore();
        drawCircle(state.origin, '#0f6bd8', 4);

        ctx.save();
        ctx.font = 'bold 13px "Microsoft YaHei", sans-serif';
        ctx.fillStyle = '#0f6bd8';
        ctx.fillText('原点', state.origin.x + 12, state.origin.y + 16);
        ctx.restore();
      }

      Object.entries(state.boundaries).forEach(([key, segments]) => {
        segments.forEach((segment, index) => {
          const suffix = segments.length > 1 ? `${BOUNDARY_META[key].shortLabel}${index + 1}` : BOUNDARY_META[key].label;
          drawLine(segment.start, segment.end, {
            color: BOUNDARY_META[key].color,
            width: 4,
            label: suffix
          });
        });
      });

      state.buildings.forEach((building, index) => {
        const isSelected = building.id === state.selectedBuildingId;
        ctx.save();
        ctx.beginPath();
        building.points.forEach((point, pointIndex) => {
          if (pointIndex === 0) {
            ctx.moveTo(point.x, point.y);
          } else {
            ctx.lineTo(point.x, point.y);
          }
        });
        ctx.closePath();
        ctx.fillStyle = isSelected ? 'rgba(196, 93, 36, 0.18)' : 'rgba(34, 91, 84, 0.12)';
        ctx.strokeStyle = isSelected ? '#c45d24' : '#225b54';
        ctx.lineWidth = isSelected ? 3 : 2;
        ctx.setLineDash([10, 6]);
        ctx.fill();
        ctx.stroke();
        ctx.restore();

        const center = getPolygonCentroid(building.points);
        ctx.save();
        ctx.font = 'bold 13px "Microsoft YaHei", sans-serif';
        ctx.fillStyle = isSelected ? '#c45d24' : '#225b54';
        ctx.fillText(building.name || `建筑物${index + 1}`, center.x + 10, center.y);
        ctx.restore();
      });

      if (state.mode === 'building' && state.pendingBuildingPoints.length) {
        ctx.save();
        ctx.strokeStyle = '#225b54';
        ctx.lineWidth = 2;
        ctx.setLineDash([8, 8]);
        ctx.beginPath();
        state.pendingBuildingPoints.forEach((point, index) => {
          if (index === 0) {
            ctx.moveTo(point.x, point.y);
          } else {
            ctx.lineTo(point.x, point.y);
          }
        });
        if (state.lastMousePoint) {
          ctx.lineTo(state.lastMousePoint.x, state.lastMousePoint.y);
        }
        ctx.stroke();
        ctx.restore();
        state.pendingBuildingPoints.forEach((point) => drawCircle(point, '#225b54', 4));
      }

      if (state.pendingPoint && (state.mode === 'scale' || BOUNDARY_META[state.mode])) {
        const hoverPoint = state.lastMousePoint || state.pendingPoint;
        drawLine(state.pendingPoint, hoverPoint, {
          color: state.mode === 'scale' ? '#da5a36' : BOUNDARY_META[state.mode].color,
          width: 2,
          dash: [8, 8]
        });
        drawCircle(state.pendingPoint, state.mode === 'scale' ? '#da5a36' : BOUNDARY_META[state.mode].color, 4);
      }

      state.devices.forEach((device) => {
        const hovered = device.id === state.hoveredDeviceId;
        drawCircle({ x: device.x, y: device.y }, hovered ? '#c45d24' : '#1a1a1a', hovered ? 7 : 5);

        ctx.save();
        ctx.font = `${hovered ? 'bold ' : ''}13px "Microsoft YaHei", sans-serif`;
        ctx.fillStyle = hovered ? '#c45d24' : '#24190d';
        ctx.fillText(device.name, device.x + 10, device.y - 10);
        ctx.restore();
      });
    }

    // Geometry and measurement helpers.
    function pointToSegmentDistance(point, segment) {
      const ax = segment.start.x;
      const ay = segment.start.y;
      const bx = segment.end.x;
      const by = segment.end.y;
      const px = point.x;
      const py = point.y;
      const abx = bx - ax;
      const aby = by - ay;
      const abLenSq = abx * abx + aby * aby;

      if (abLenSq === 0) {
        return Math.hypot(px - ax, py - ay);
      }

      const apx = px - ax;
      const apy = py - ay;
      const t = Math.max(0, Math.min(1, (apx * abx + apy * aby) / abLenSq));
      const closestX = ax + abx * t;
      const closestY = ay + aby * t;
      return Math.hypot(px - closestX, py - closestY);
    }

    function getPolygonCentroid(points) {
      const total = points.reduce((acc, point) => ({ x: acc.x + point.x, y: acc.y + point.y }), { x: 0, y: 0 });
      return {
        x: total.x / points.length,
        y: total.y / points.length
      };
    }

    function isPointInPolygon(point, polygon) {
      let inside = false;
      for (let i = 0, j = polygon.length - 1; i < polygon.length; j = i++) {
        const xi = polygon[i].x;
        const yi = polygon[i].y;
        const xj = polygon[j].x;
        const yj = polygon[j].y;
        const intersects = ((yi > point.y) !== (yj > point.y)) &&
          (point.x < ((xj - xi) * (point.y - yi)) / ((yj - yi) || 1e-9) + xi);
        if (intersects) inside = !inside;
      }
      return inside;
    }

    function getSelectedBuilding() {
      return state.buildings.find((building) => building.id === state.selectedBuildingId) || null;
    }

    function getBuildingForDevice(device) {
      if (device.buildingId) {
        const matched = state.buildings.find((building) => building.id === device.buildingId);
        if (matched) {
          return matched;
        }
      }
      return state.buildings.find((building) => isPointInPolygon(device, building.points)) || null;
    }

    function findContainingBuilding(point) {
      return state.buildings.find((building) => isPointInPolygon(point, building.points)) || null;
    }

    function raySegmentDistance(point, start, end, direction) {
      if (direction === 'east' || direction === 'west') {
        if ((start.y > point.y) === (end.y > point.y) || start.y === end.y) {
          return null;
        }
        const t = (point.y - start.y) / (end.y - start.y);
        if (t < 0 || t > 1) {
          return null;
        }
        const x = start.x + (end.x - start.x) * t;
        if (direction === 'east' && x > point.x) return x - point.x;
        if (direction === 'west' && x < point.x) return point.x - x;
        return null;
      }

      if ((start.x > point.x) === (end.x > point.x) || start.x === end.x) {
        return null;
      }
      const t = (point.x - start.x) / (end.x - start.x);
      if (t < 0 || t > 1) {
        return null;
      }
      const y = start.y + (end.y - start.y) * t;
      if (direction === 'south' && y > point.y) return y - point.y;
      if (direction === 'north' && y < point.y) return point.y - y;
      return null;
    }

    function getIndoorDistanceByDirection(device, direction) {
      const building = getBuildingForDevice(device);
      if (!building || !state.scale || !isPointInPolygon(device, building.points)) {
        return null;
      }
      let minPixel = Infinity;
      for (let i = 0; i < building.points.length; i += 1) {
        const start = building.points[i];
        const end = building.points[(i + 1) % building.points.length];
        const hit = raySegmentDistance(device, start, end, direction);
        if (hit != null && hit < minPixel) {
          minPixel = hit;
        }
      }
      return Number.isFinite(minPixel) ? pixelToActual(minPixel) : null;
    }

    function pixelToActual(pixelDistance) {
      if (!state.scale) {
        return null;
      }
      return pixelDistance * state.scale.scale;
    }

    function formatDistanceForBoundary(boundaryKey, point) {
      const boundarySegments = state.boundaries[boundaryKey];
      if (!boundarySegments || !boundarySegments.length) {
        return '未设置';
      }
      if (!state.scale) {
        return '未设置比例尺';
      }

      let minDistance = Infinity;
      boundarySegments.forEach((segment) => {
        const currentDistance = pointToSegmentDistance(point, segment);
        if (currentDistance < minDistance) {
          minDistance = currentDistance;
        }
      });

      const actual = pixelToActual(minDistance);
      return `${actual.toFixed(2)} ${state.scale.unit}`;
    }

    function getDeviceRelativePosition(device) {
      if (!state.origin) {
        return null;
      }

      const deltaX = device.x - state.origin.x;
      const deltaY = state.origin.y - device.y;
      if (state.scale) {
        return {
          x: pixelToActual(deltaX),
          y: pixelToActual(deltaY),
          unit: state.scale.unit
        };
      }

      return {
        x: deltaX,
        y: deltaY,
        unit: 'px'
      };
    }

    function formatNumber(value) {
      return Number(value).toFixed(2);
    }

    function formatRelativePosition(device) {
      const position = getDeviceRelativePosition(device);
      if (!position) {
        return `X=未设置，Y=未设置，Z=${formatNumber(device.z || 0)} m`;
      }
      return `X=${formatNumber(position.x)} ${position.unit}，Y=${formatNumber(position.y)} ${position.unit}，Z=${formatNumber(device.z || 0)} m`;
    }

    function formatDirectionLabel(key) {
      return BOUNDARY_META[key].shortLabel;
    }

    function getBoundaryDistanceValue(boundaryKey, point) {
      const boundarySegments = state.boundaries[boundaryKey];
      if (!boundarySegments || !boundarySegments.length || !state.scale) {
        return null;
      }

      let minDistance = Infinity;
      boundarySegments.forEach((segment) => {
        const currentDistance = pointToSegmentDistance(point, segment);
        if (currentDistance < minDistance) {
          minDistance = currentDistance;
        }
      });

      return pixelToActual(minDistance);
    }

    function getIndoorBoundaryLevel(device, direction) {
      const distanceToIndoorBoundary = getIndoorDistanceByDirection(device, direction);
      if (!Number.isFinite(device.soundPowerLevel) || !Number.isFinite(distanceToIndoorBoundary) || distanceToIndoorBoundary <= 0) {
        return null;
      }
      return device.soundPowerLevel - 20 * Math.log10(distanceToIndoorBoundary) - 8;
    }

    function getOutdoorNoiseLevel(device, direction) {
      const building = getBuildingForDevice(device);
      const indoorBoundaryLevel = getIndoorBoundaryLevel(device, direction);
      if (!building || indoorBoundaryLevel == null || !Number.isFinite(building.insertionLoss) || !Number.isFinite(device.outdoorDistance) || device.outdoorDistance <= 0) {
        return null;
      }
      return indoorBoundaryLevel - building.insertionLoss - 20 * Math.log10(device.outdoorDistance);
    }

    function formatDirectionalSeries(device, formatter) {
      return ['east', 'south', 'west', 'north']
        .map((key) => `${formatDirectionLabel(key)}=${formatter(key)}`)
        .join('，');
    }

    function buildTooltip(device) {
      const building = getBuildingForDevice(device);
      return [
        `建筑物：${building ? building.name : (device.buildingName || '未关联')}`,
        `声源名称：${device.sourceName || device.name}`,
        `相对原点：${formatRelativePosition(device)}`,
        `距室内边界：${formatDirectionalSeries(device, (key) => {
          const value = getIndoorDistanceByDirection(device, key);
          return value == null ? '未设置' : `${formatNumber(value)} ${state.scale ? state.scale.unit : 'm'}`;
        })}`,
        `室内边界声级：${formatDirectionalSeries(device, (key) => {
          const value = getIndoorBoundaryLevel(device, key);
          return value == null ? '未设置' : `${formatNumber(value)} dB(A)`;
        })}`,
        `建筑物外噪声：${formatDirectionalSeries(device, (key) => {
          const value = getOutdoorNoiseLevel(device, key);
          return value == null ? '未设置' : `${formatNumber(value)} dB(A)`;
        })}`,
        `东厂界：${formatDistanceForBoundary('east', device)}`,
        `南厂界：${formatDistanceForBoundary('south', device)}`,
        `西厂界：${formatDistanceForBoundary('west', device)}`,
        `北厂界：${formatDistanceForBoundary('north', device)}`
      ].join('\n');
    }

    function showTooltip(x, y, text) {
      tooltip.textContent = text;
      tooltip.style.left = `${x + 16}px`;
      tooltip.style.top = `${y + 16}px`;
      tooltip.style.display = 'block';
    }

    function hideTooltip() {
      tooltip.style.display = 'none';
    }

    function findHoveredDevice(point) {
      let target = null;
      let minDistance = Infinity;
      state.devices.forEach((device) => {
        const d = Math.hypot(point.x - device.x, point.y - device.y);
        if (d <= 10 && d < minDistance) {
          target = device;
          minDistance = d;
        }
      });
      return target;
    }

    function findClickedBuilding(point) {
      return state.buildings.find((building) => isPointInPolygon(point, building.points)) || null;
    }

    // User interaction workflows for annotation and project lifecycle.
    function requireImage() {
      if (state.image) {
        return true;
      }
      alert('请先上传图片。');
      return false;
    }

    function validateScaleInputs() {
      const actualDistance = Number(actualLengthInput.value);
      const unit = (unitInput.value || '').trim() || '米';
      if (!Number.isFinite(actualDistance) || actualDistance <= 0) {
        alert('请输入大于 0 的实际长度。');
        return null;
      }
      return { actualDistance, unit };
    }

    function validateSourceInputs(defaultName) {
      const draft = state.deviceDraft || createDefaultDeviceDraft();
      const sourceNameInputValue = prompt('声源名称', draft.sourceName || defaultName);
      if (sourceNameInputValue === null) return null;
      const modelInputValue = prompt('型号', draft.model || '');
      if (modelInputValue === null) return null;
      const soundPowerInputValue = prompt('声功率级 dB(A)', String(draft.soundPowerLevel ?? 90));
      if (soundPowerInputValue === null) return null;
      const controlMeasuresInputValue = prompt('声源控制措施', draft.controlMeasures || '');
      if (controlMeasuresInputValue === null) return null;
      const runtimePeriodInputValue = prompt('运行时段', draft.runtimePeriod || '昼间');
      if (runtimePeriodInputValue === null) return null;
      const outdoorDistanceInputValue = prompt('建筑物外距离', String(draft.outdoorDistance ?? 1));
      if (outdoorDistanceInputValue === null) return null;
      const zInputValue = prompt('相对高度 Z', String(draft.z ?? 0));
      if (zInputValue === null) return null;

      const sourceName = (sourceNameInputValue || '').trim() || defaultName;
      const model = (modelInputValue || '').trim();
      const soundPowerLevel = Number(soundPowerInputValue);
      const controlMeasures = (controlMeasuresInputValue || '').trim();
      const runtimePeriod = (runtimePeriodInputValue || '').trim() || '昼间';
      const outdoorDistance = Number(outdoorDistanceInputValue);
      const z = Number(zInputValue);

      if (!Number.isFinite(soundPowerLevel)) {
        alert('请输入有效的声功率级 dB(A)。');
        return null;
      }
      if (!Number.isFinite(outdoorDistance) || outdoorDistance <= 0) {
        alert('请输入大于 0 的建筑物外距离。');
        return null;
      }
      if (!Number.isFinite(z)) {
        alert('请输入有效的相对高度 Z。');
        return null;
      }

      return {
        sourceName,
        model,
        soundPowerLevel,
        controlMeasures,
        runtimePeriod,
        outdoorDistance,
        z
      };
    }

    function editDevice(device) {
      if (!device) {
        return;
      }
      const buildingNames = state.buildings.map((building) => building.name).join(' / ');
      const sourceNameInputValue = prompt('声源名称', device.sourceName || device.name || '');
      if (sourceNameInputValue === null) return;
      const modelInputValue = prompt('型号', device.model || '');
      if (modelInputValue === null) return;
      const soundPowerInputValue = prompt('声功率级 dB(A)', String(device.soundPowerLevel ?? 90));
      if (soundPowerInputValue === null) return;
      const controlMeasuresInputValue = prompt('声源控制措施', device.controlMeasures || '');
      if (controlMeasuresInputValue === null) return;
      const runtimePeriodInputValue = prompt('运行时段', device.runtimePeriod || '昼间');
      if (runtimePeriodInputValue === null) return;
      const outdoorDistanceInputValue = prompt('建筑物外距离', String(device.outdoorDistance ?? 1));
      if (outdoorDistanceInputValue === null) return;
      const zInputValue = prompt('相对高度 Z', String(device.z ?? 0));
      if (zInputValue === null) return;
      let buildingName = prompt(`所属建筑物名称（可留空取消关联）${buildingNames ? '，可选：' + buildingNames : ''}`, (getBuildingForDevice(device) || {}).name || '');
      if (buildingName === null) return;

      const sourceName = (sourceNameInputValue || '').trim() || device.sourceName || device.name;
      const model = (modelInputValue || '').trim();
      const soundPowerLevel = Number(soundPowerInputValue);
      const controlMeasures = (controlMeasuresInputValue || '').trim();
      const runtimePeriod = (runtimePeriodInputValue || '').trim() || '昼间';
      const outdoorDistance = Number(outdoorDistanceInputValue);
      const z = Number(zInputValue);

      if (!Number.isFinite(soundPowerLevel) || !Number.isFinite(outdoorDistance) || outdoorDistance <= 0 || !Number.isFinite(z)) {
        alert('设备信息未更新：请确保声功率级、建筑物外距离和 Z 为有效数字。');
        return;
      }

      buildingName = (buildingName || '').trim();
      const building = state.buildings.find((item) => item.name === buildingName) || null;

      saveHistory();
      Object.assign(device, {
        name: sourceName,
        sourceName,
        model,
        soundPowerLevel,
        controlMeasures,
        runtimePeriod,
        outdoorDistance,
        z,
        buildingId: building ? building.id : null,
        buildingName: building ? building.name : ''
      });
      state.deviceDraft = {
        sourceName,
        model,
        soundPowerLevel,
        controlMeasures,
        runtimePeriod,
        outdoorDistance,
        z
      };
      syncUiAfterStateChange();
      scheduleAutosave();
    }

    function promptBuildingData(existing = null, defaultName = '建筑物1') {
      const nameInputValue = prompt('建筑物名称', existing ? existing.name : defaultName);
      if (nameInputValue === null) return null;
      const insertionLossInputValue = prompt('建筑物插入损失 dB(A)', String(existing ? existing.insertionLoss : 21));
      if (insertionLossInputValue === null) return null;
      const name = (nameInputValue || '').trim() || defaultName;
      const insertionLoss = Number(insertionLossInputValue);
      if (!Number.isFinite(insertionLoss)) {
        alert('请输入有效的建筑物插入损失。');
        return null;
      }
      return { name, insertionLoss };
    }

    function editSelectedBuilding() {
      const building = getSelectedBuilding();
      if (!building) {
        alert('请先在左侧选择一个建筑物。');
        return;
      }
      const next = promptBuildingData(building, building.name);
      if (!next) {
        return;
      }
      saveHistory();
      building.name = next.name;
      building.insertionLoss = next.insertionLoss;
      state.devices.forEach((device) => {
        if (device.buildingId === building.id) {
          device.buildingName = next.name;
        }
      });
      syncUiAfterStateChange();
      scheduleAutosave();
    }

    function finalizeBuilding() {
      if (state.pendingBuildingPoints.length < 3) {
        alert('至少需要 3 个点才能构成建筑物。');
        return;
      }
      const next = promptBuildingData(null, `建筑物${state.buildings.length + 1}`);
      if (!next) {
        return;
      }
      saveHistory();
      const building = {
        id: `bld-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
        name: next.name,
        insertionLoss: next.insertionLoss,
        points: deepClone(state.pendingBuildingPoints)
      };
      state.buildings.push(building);
      state.selectedBuildingId = building.id;
      state.pendingBuildingPoints = [];
      state.mode = 'browse';
      syncUiAfterStateChange();
      scheduleAutosave();
    }

    function addDevice(point) {
      const defaultName = `设备${state.devices.length + 1}`;
      const inputs = validateSourceInputs(defaultName);
      if (!inputs) {
        return;
      }

      saveHistory();
      const building = findContainingBuilding(point) || getSelectedBuilding();
      state.devices.push({
        id: `dev-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
        name: inputs.sourceName,
        buildingId: building ? building.id : null,
        buildingName: building ? building.name : '',
        sourceName: inputs.sourceName,
        model: inputs.model,
        soundPowerLevel: inputs.soundPowerLevel,
        controlMeasures: inputs.controlMeasures,
        runtimePeriod: inputs.runtimePeriod,
        outdoorDistance: inputs.outdoorDistance,
        z: inputs.z,
        x: point.x,
        y: point.y
      });
      state.deviceDraft = {
        sourceName: `设备${state.devices.length + 1}`,
        model: inputs.model,
        soundPowerLevel: inputs.soundPowerLevel,
        controlMeasures: inputs.controlMeasures,
        runtimePeriod: inputs.runtimePeriod,
        outdoorDistance: inputs.outdoorDistance,
        z: inputs.z
      };
      syncUiAfterStateChange();
      scheduleAutosave();
    }

    function finalizeScale(point) {
      const inputs = validateScaleInputs();
      if (!inputs) {
        return;
      }
      const pixelDistance = distance(state.pendingPoint, point);
      if (pixelDistance <= 0) {
        alert('参考线长度必须大于 0。');
        return;
      }
      saveHistory();
      state.scale = {
        start: state.pendingPoint,
        end: point,
        pixelDistance,
        actualDistance: inputs.actualDistance,
        unit: inputs.unit,
        scale: inputs.actualDistance / pixelDistance
      };
      state.pendingPoint = null;
      syncUiAfterStateChange();
      scheduleAutosave();
    }

    function finalizeOrigin(point) {
      saveHistory();
      state.origin = point;
      syncUiAfterStateChange();
      scheduleAutosave();
    }

    function finalizeBoundary(point) {
      const key = state.mode;
      const meta = BOUNDARY_META[key];
      const pixelDistance = distance(state.pendingPoint, point);
      if (pixelDistance <= 0) {
        alert(meta.label + ' 的线段长度必须大于 0。');
        return;
      }
      saveHistory();
      state.boundaries[key].push({
        id: `seg-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
        start: state.pendingPoint,
        end: point
      });
      state.pendingPoint = null;
      syncUiAfterStateChange();
      scheduleAutosave();
    }

    function loadImageFromDataUrl(dataUrl) {
      if (!dataUrl) {
        return Promise.resolve(null);
      }
      return new Promise((resolve, reject) => {
        const img = new Image();
        img.onload = () => resolve(img);
        img.onerror = () => reject(new Error('图片数据无法恢复'));
        img.src = dataUrl;
      });
    }

    async function applyProjectData(rawProject, options = {}) {
      const project = normalizeProjectData(rawProject || {});
      suppressAutosave = true;
      clearTimeout(autosaveTimer);

      try {
        const image = await loadImageFromDataUrl(project.imageDataUrl);
        state.image = image;
        state.imageName = project.imageName;
        state.imageDataUrl = project.imageDataUrl;
        state.projectName = project.projectName;
        state.mode = project.mode;
        state.pendingPoint = project.pendingPoint;
        state.pendingBuildingPoints = project.pendingBuildingPoints;
        state.lastMousePoint = null;
        state.scale = project.scale;
        state.origin = project.origin;
        state.boundaries = project.boundaries;
        state.buildings = project.buildings;
        state.devices = project.devices;
        state.selectedBuildingId = project.selectedBuildingId;
        state.theme = project.theme;
        state.hoveredDeviceId = null;
        state.history = [];
        state.lastSavedAt = project.savedAt;

        actualLengthInput.value = project.draftScaleInputs.actualLength;
        unitInput.value = project.draftScaleInputs.unit;
        sourceNameInput.value = project.draftSourceInputs.sourceName;
        sourceModelInput.value = project.draftSourceInputs.model;
        soundPowerLevelInput.value = project.draftSourceInputs.soundPowerLevel;
        controlMeasuresInput.value = project.draftSourceInputs.controlMeasures;
        runtimePeriodInput.value = project.draftSourceInputs.runtimePeriod;
        outdoorDistanceInput.value = project.draftSourceInputs.outdoorDistance;
        sourceHeightInput.value = project.draftSourceInputs.z;
        state.deviceDraft = {
          sourceName: project.draftSourceInputs.sourceName,
          model: project.draftSourceInputs.model,
          soundPowerLevel: Number(project.draftSourceInputs.soundPowerLevel),
          controlMeasures: project.draftSourceInputs.controlMeasures,
          runtimePeriod: project.draftSourceInputs.runtimePeriod,
          outdoorDistance: Number(project.draftSourceInputs.outdoorDistance),
          z: Number(project.draftSourceInputs.z)
        };

        if (image) {
          canvas.width = image.width;
          canvas.height = image.height;
        } else {
          canvas.width = 1200;
          canvas.height = 800;
        }

        hideTooltip();
        syncUiAfterStateChange();
      } finally {
        suppressAutosave = false;
      }

      if (state.lastSavedAt) {
        refreshSaveStatus();
      } else if (options.resetSaveState !== false) {
        state.lastSavedAt = null;
        refreshSaveStatus();
      }

      if (options.autosaveAfterRestore) {
        scheduleAutosave();
      }
    }

    async function loadAutosaveProject(options = {}) {
      if (!window.indexedDB) {
        markSaveUnavailable('当前浏览器不支持 IndexedDB，请使用导出工程');
        return false;
      }
      const payload = await readAutosaveData();
      if (!payload) {
        if (!options.silent) {
          alert('没有找到自动保存的工程。');
        }
        if (!state.lastSavedAt) {
          refreshSaveStatus();
        }
        return false;
      }
      if (options.confirmOverwrite && hasProjectContent()) {
        const confirmed = confirm('恢复自动保存会覆盖当前页面内容，是否继续？');
        if (!confirmed) {
          return false;
        }
      }
      await applyProjectData(payload, { resetSaveState: false });
      return true;
    }

    async function exportProjectFile() {
      const payload = buildProjectPayload();
      const blob = new Blob([JSON.stringify(payload, null, 2)], {
        type: 'application/json;charset=utf-8'
      });
      const safeName = (state.projectName || '未命名工程').replace(/[\\/:*?"<>|]+/g, '_');
      const link = document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.download = `${safeName}.factory-distance.json`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(link.href);
    }

    function escapeCsvValue(value) {
      const text = value == null ? '' : String(value);
      if (/[",\n]/.test(text)) {
        return '"' + text.replace(/"/g, '""') + '"';
      }
      return text;
    }

    function exportDeviceCsv() {
      if (!state.devices.length) {
        alert('当前没有设备数据可导出。');
        return;
      }

      const coordinateUnit = state.origin ? (state.scale ? state.scale.unit : 'px') : 'px';
      const distanceUnit = (state.scale && state.scale.unit) || (unitInput.value || '米').trim() || '米';
      const headerTop = [
        '序号',
        '建筑物名称',
        '声源名称',
        '型号',
        '声功率级/dB（A）',
        '声源控制措施',
        '空间相对位置/m',
        '',
        '',
        '距室内边界距离/m',
        '',
        '',
        '',
        '室内边界声级/dB（A）',
        '',
        '',
        '',
        '运行时段',
        '建筑物插入损失/dB（A）',
        '建筑物外噪声',
        '',
        '',
        '',
        '建筑物外距离'
      ];
      const headerBottom = [
        '',
        '',
        '',
        '',
        '',
        '',
        `X(${coordinateUnit})`,
        `Y(${coordinateUnit})`,
        'Z(m)',
        '东',
        '南',
        '西',
        '北',
        '东',
        '南',
        '西',
        '北',
        '',
        '',
        '东',
        '南',
        '西',
        '北',
        `${distanceUnit}`
      ];

      const rows = state.devices.map((device, index) => {
        const relative = getDeviceRelativePosition(device);
        const building = getBuildingForDevice(device);
        const indoorDistances = ['east', 'south', 'west', 'north'].map((key) => getIndoorDistanceByDirection(device, key));
        const indoorLevels = ['east', 'south', 'west', 'north'].map((key) => getIndoorBoundaryLevel(device, key));
        const outdoorLevels = ['east', 'south', 'west', 'north'].map((key) => getOutdoorNoiseLevel(device, key));

        return [
          index + 1,
          building ? building.name : (device.buildingName || ''),
          device.sourceName || device.name || '',
          device.model || '',
          formatNumber(device.soundPowerLevel),
          device.controlMeasures || '',
          relative ? formatNumber(relative.x) : '',
          relative ? formatNumber(relative.y) : '',
          formatNumber(device.z || 0),
          ...indoorDistances.map((value) => value == null ? '' : formatNumber(value)),
          ...indoorLevels.map((value) => value == null ? '' : formatNumber(value)),
          device.runtimePeriod || '',
          building ? formatNumber(building.insertionLoss) : '',
          ...outdoorLevels.map((value) => value == null ? '' : formatNumber(value)),
          formatNumber(device.outdoorDistance)
        ];
      });

      const csvText = [headerTop, headerBottom, ...rows]
        .map((row) => row.map(escapeCsvValue).join(','))
        .join('\r\n');

      const safeName = (state.projectName || '未命名工程').replace(/[\\/:*?"<>|]+/g, '_');
      const blob = new Blob(['\ufeff' + csvText], { type: 'text/csv;charset=utf-8;' });
      const link = document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.download = `${safeName}.devices.csv`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(link.href);
    }

    async function importProjectFile(file) {
      if (!file) {
        return;
      }
      if (hasProjectContent()) {
        const confirmed = confirm('导入工程会覆盖当前页面内容，是否继续？');
        if (!confirmed) {
          projectImportInput.value = '';
          return;
        }
      }

      const text = await file.text();
      let parsed;
      try {
        parsed = JSON.parse(text);
      } catch (error) {
        alert('工程文件不是有效的 JSON。');
        projectImportInput.value = '';
        return;
      }

      try {
        await applyProjectData(parsed, { autosaveAfterRestore: true, resetSaveState: true });
      } catch (error) {
        console.error(error);
        alert(`导入失败：${error.message || error}`);
      } finally {
        projectImportInput.value = '';
      }
    }

    function handleCanvasClick(event) {
      if (!requireImage()) {
        return;
      }
      const point = getCanvasPoint(event);

      if (state.mode === 'browse') {
        const clickedDevice = findHoveredDevice(point);
        if (clickedDevice) {
          editDevice(clickedDevice);
          return;
        }
        const clickedBuilding = findClickedBuilding(point);
        if (clickedBuilding) {
          state.selectedBuildingId = clickedBuilding.id;
          syncUiAfterStateChange();
          return;
        }
      }

      if (state.mode === 'scale') {
        if (!state.pendingPoint) {
          state.pendingPoint = point;
          render();
          scheduleAutosave();
          return;
        }
        finalizeScale(point);
        return;
      }

      if (state.mode === 'origin') {
        finalizeOrigin(point);
        return;
      }

      if (state.mode === 'building') {
        state.pendingBuildingPoints.push(point);
        render();
        scheduleAutosave();
        return;
      }

      if (BOUNDARY_META[state.mode]) {
        if (!state.pendingPoint) {
          state.pendingPoint = point;
          render();
          scheduleAutosave();
          return;
        }
        finalizeBoundary(point);
        return;
      }

      if (state.mode === 'device') {
        addDevice(point);
      }
    }

    // DOM event bindings.
    canvas.addEventListener('mousemove', (event) => {
      if (!state.image) {
        hideTooltip();
        return;
      }

      const point = getCanvasPoint(event);
      state.lastMousePoint = point;

      const hovered = findHoveredDevice(point);
      const nextHoveredId = hovered ? hovered.id : null;
      if (nextHoveredId !== state.hoveredDeviceId) {
        state.hoveredDeviceId = nextHoveredId;
        render();
      }

      if (hovered) {
        showTooltip(event.clientX, event.clientY, buildTooltip(hovered));
      } else {
        hideTooltip();
      }

      if (state.pendingPoint && (state.mode === 'scale' || BOUNDARY_META[state.mode])) {
        render();
      }

      if (state.mode === 'building' && state.pendingBuildingPoints.length) {
        render();
      }
    });

    canvas.addEventListener('mouseleave', () => {
      state.hoveredDeviceId = null;
      hideTooltip();
      render();
    });

    canvas.addEventListener('click', handleCanvasClick);

    imageInput.addEventListener('change', (event) => {
      const file = event.target.files[0];
      if (!file) {
        return;
      }
      if (!/^image\/(png|jpeg)$/.test(file.type)) {
        alert('仅支持 JPG/PNG 图片。');
        imageInput.value = '';
        return;
      }

      const shouldReset = hasProjectContent();
      if (shouldReset && !confirm('重新上传图片会清空当前标注，是否继续？')) {
        imageInput.value = '';
        return;
      }

      const reader = new FileReader();
      reader.onload = () => {
        const img = new Image();
        img.onload = () => {
          state.image = img;
          state.imageName = file.name;
          state.imageDataUrl = reader.result;
          canvas.width = img.width;
          canvas.height = img.height;
          resetAnnotations();
          state.lastSavedAt = null;
          setMode('browse', { autosave: false });
          refreshSaveStatus();
          scheduleAutosave();
        };
        img.src = reader.result;
      };
      reader.readAsDataURL(file);
    });

    document.getElementById('modeScale').addEventListener('click', () => {
      if (!requireImage()) return;
      setMode(state.mode === 'scale' ? 'browse' : 'scale');
    });

    document.getElementById('toggleScalePanel').addEventListener('click', () => {
      scalePanel.classList.toggle('hidden');
    });

    document.getElementById('modeOrigin').addEventListener('click', () => {
      if (!requireImage()) return;
      setMode(state.mode === 'origin' ? 'browse' : 'origin');
    });

    document.getElementById('modeEast').addEventListener('click', () => {
      if (!requireImage()) return;
      setMode(state.mode === 'east' ? 'browse' : 'east');
    });

    document.getElementById('modeSouth').addEventListener('click', () => {
      if (!requireImage()) return;
      setMode(state.mode === 'south' ? 'browse' : 'south');
    });

    document.getElementById('modeWest').addEventListener('click', () => {
      if (!requireImage()) return;
      setMode(state.mode === 'west' ? 'browse' : 'west');
    });

    document.getElementById('modeNorth').addEventListener('click', () => {
      if (!requireImage()) return;
      setMode(state.mode === 'north' ? 'browse' : 'north');
    });

    document.getElementById('modeDevice').addEventListener('click', () => {
      if (!requireImage()) return;
      setMode(state.mode === 'device' ? 'browse' : 'device');
    });

    document.getElementById('modeBuilding').addEventListener('click', () => {
      if (!requireImage()) return;
      setMode(state.mode === 'building' ? 'browse' : 'building');
    });

    document.getElementById('finishBuilding').addEventListener('click', () => {
      finalizeBuilding();
    });

    document.getElementById('editBuilding').addEventListener('click', () => {
      editSelectedBuilding();
    });

    document.getElementById('clearBuildings').addEventListener('click', () => {
      if (!state.buildings.length) {
        return;
      }
      if (!confirm('确定要清空所有建筑物吗？')) {
        return;
      }
      saveHistory();
      state.buildings = [];
      state.selectedBuildingId = null;
      state.devices.forEach((device) => {
        device.buildingId = null;
        device.buildingName = '';
      });
      syncUiAfterStateChange();
      scheduleAutosave();
    });

    document.getElementById('cancelPending').addEventListener('click', () => {
      cancelCurrentOperation();
    });

    document.getElementById('undoAction').addEventListener('click', undoLastAction);
    document.getElementById('clearAll').addEventListener('click', resetAll);
    document.getElementById('clearScale').addEventListener('click', clearScale);
    document.getElementById('clearOrigin').addEventListener('click', clearOrigin);

    Object.keys(themeButtons).forEach((key) => {
      themeButtons[key].addEventListener('click', () => {
        state.theme = key;
        syncUiAfterStateChange();
        scheduleAutosave();
      });
    });

    document.getElementById('exportProject').addEventListener('click', () => {
      exportProjectFile();
    });

    document.getElementById('exportCsv').addEventListener('click', () => {
      exportDeviceCsv();
    });

    document.getElementById('importProjectButton').addEventListener('click', () => {
      projectImportInput.click();
    });

    document.getElementById('restoreAutosave').addEventListener('click', () => {
      loadAutosaveProject({ confirmOverwrite: true }).catch((error) => {
        console.error(error);
        alert(`恢复自动保存失败：${error.message || error}`);
      });
    });

    document.getElementById('clearAutosave').addEventListener('click', async () => {
      const confirmed = confirm('确定要清除浏览器中保存的自动保存工程吗？');
      if (!confirmed) {
        return;
      }
      try {
        await clearAutosaveData();
        state.lastSavedAt = null;
        if (hasProjectContent()) {
          setSaveState('未保存', '自动保存：已清除，后续修改会重新自动保存');
        } else {
          refreshSaveStatus();
        }
      } catch (error) {
        console.error(error);
        alert(`清除自动保存失败：${error.message || error}`);
      }
    });

    projectImportInput.addEventListener('change', (event) => {
      const file = event.target.files[0];
      importProjectFile(file).catch((error) => {
        console.error(error);
        alert(`导入失败：${error.message || error}`);
      });
    });

    projectNameInput.addEventListener('input', () => {
      state.projectName = (projectNameInput.value || '').trim() || '未命名工程';
      updateStatus();
      scheduleAutosave();
    });

    actualLengthInput.addEventListener('input', () => {
      scheduleAutosave();
    });

    unitInput.addEventListener('input', () => {
      scheduleAutosave();
    });

    [
      buildingNameInput,
      sourceNameInput,
      sourceModelInput,
      soundPowerLevelInput,
      controlMeasuresInput,
      indoorBoundaryDistanceInput,
      runtimePeriodInput,
      buildingInsertionLossInput,
      outdoorDistanceInput,
      sourceHeightInput
    ].forEach((input) => {
      input.addEventListener('input', () => {
        scheduleAutosave();
      });
    });

    window.addEventListener('keydown', (event) => {
      if (event.key === 'Escape') {
        cancelCurrentOperation();
      }
    });

    window.addEventListener('beforeunload', () => {
      clearTimeout(autosaveTimer);
      if (!suppressAutosave && hasProjectContent()) {
        saveAutosaveNow().catch(() => {});
      }
    });

    // Initial boot: render shell and restore autosave if present.
    async function initializeApp() {
      applyTheme();
      renderBuildingList();
      updateButtons();
      updateStatus();
      refreshSaveStatus();
      render();

      try {
        const restored = await loadAutosaveProject({ silent: true });
        if (!restored) {
          refreshSaveStatus();
        }
      } catch (error) {
        console.error(error);
        markSaveUnavailable('自动恢复失败，请使用导出工程');
      }
    }

    initializeApp();
  </script>
</body>
</html>
"""


# Lightweight HTTP handler that serves the embedded single-page app.
class SinglePageHandler(http.server.BaseHTTPRequestHandler):
    def _send_index(self, include_body=True):
        encoded = HTML.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        if include_body:
            self.wfile.write(encoded)

    def do_GET(self):
        if self.path not in ("/", "/index.html"):
            self.send_error(404, "Not Found")
            return
        self._send_index(include_body=True)

    def do_HEAD(self):
        if self.path not in ("/", "/index.html"):
            self.send_error(404, "Not Found")
            return
        self._send_index(include_body=False)

    def log_message(self, format, *args):
        return


# CLI entrypoint: start local server and optionally open the browser.
def main():
    parser = argparse.ArgumentParser(description="本地设备与厂界距离测算工具")
    parser.add_argument("--host", default="0.0.0.0", help="监听地址，默认 127.0.0.1")
    parser.add_argument("--port", default=8765, type=int, help="监听端口，默认 8765")
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="启动后不自动打开浏览器",
    )
    args = parser.parse_args()

    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer((args.host, args.port), SinglePageHandler) as httpd:
        url = f"http://{args.host}:{args.port}"
        print(f"本地服务已启动：{url}")
        print("按 Ctrl+C 结束。")
        if not args.no_browser:
            threading.Timer(0.5, lambda: webbrowser.open(url)).start()
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n服务已停止。")


if __name__ == "__main__":
    main()
