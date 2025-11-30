# OCR模型文件分析报告

## 执行时间
2024年11月28日

## 分析目标
分析PaddleOCR和RapidOCR模型目录,识别各语言模型的大小,为优化提供数据支持。

---

## 1. PaddleOCR模型分析

### 1.1 模型文件统计

| 模型名称 | 大小 | 用途 | 是否必需 |
|---------|------|------|---------|
| ch_PP-OCRv3_rec_infer | 11.35 MB | 简体中文识别 | ✅ 必需 |
| japan_PP-OCRv3_rec_infer | 10.84 MB | 日文识别 | ❌ 可移除 |
| korean_PP-OCRv3_rec_infer | 10.43 MB | 韩文识别 | ❌ 可移除 |
| cyrillic_PP-OCRv3_rec_infer | 9.52 MB | 俄文识别 | ❌ 可移除 |
| en_PP-OCRv3_rec_infer | 9.50 MB | 英文识别 | ✅ 必需 |
| chinese_cht_mobile_v2.0_rec_infer | 5.67 MB | 繁体中文识别 | ❌ 可移除 |
| ch_PP-OCRv3_det_infer | 3.64 MB | 文本检测 | ✅ 必需 |
| ch_ppocr_mobile_v2.0_cls_infer | 1.38 MB | 方向分类 | ✅ 必需 |

**模型总大小**: 62.33 MB

### 1.2 DLL文件统计

| 文件名 | 大小 | 说明 |
|--------|------|------|
| mklml.dll | 88.36 MB | Intel MKL数学库 |
| opencv_world4100.dll | 61.66 MB | OpenCV库 |
| paddle_inference.dll | 48.45 MB | PaddlePaddle推理引擎 |
| mkldnn.dll | 20.46 MB | 深度学习加速库 |
| onnxruntime.dll | 7.53 MB | ONNX运行时 |
| paddle2onnx.dll | 3.72 MB | 模型转换库 |
| libiomp5md.dll | 1.65 MB | OpenMP库 |
| PaddleOCR-json.exe | 974.50 KB | 主程序 |
| 其他运行时DLL | ~1.25 MB | VC++运行时等 |

**DLL总大小**: 234.01 MB

### 1.3 配置文件

- **配置文件**: 6个 (config_chinese.txt, config_chinese_cht.txt, config_cyrillic.txt, config_en.txt, config_japan.txt, config_korean.txt)
- **字典文件**: 6个 (dict_chinese.txt, dict_chinese_cht.txt, dict_cyrillic.txt, dict_en.txt, dict_japan.txt, dict_korean.txt)

### 1.4 当前使用情况

根据代码分析,系统默认使用 `config_chinese.txt`,包含:
- ✅ 简体中文检测模型 (ch_PP-OCRv3_det_infer)
- ✅ 简体中文识别模型 (ch_PP-OCRv3_rec_infer)
- ✅ 方向分类器 (ch_ppocr_mobile_v2.0_cls_infer)

**实际使用的模型大小**: 16.37 MB (检测3.64MB + 识别11.35MB + 分类1.38MB)

---

## 2. RapidOCR模型分析

### 2.1 模型文件统计

| 模型文件 | 大小 | 用途 |
|---------|------|------|
| rec_ch_PP-OCRv4_infer.onnx | 10.35 MB | 简体中文识别v4 |
| rec_chinese_cht_PP-OCRv3_infer.onnx | 10.65 MB | 繁体中文识别 |
| ch_PP-OCRv3_rec_infer.onnx | 10.20 MB | 简体中文识别v3 |
| rec_japan_PP-OCRv3_infer.onnx | 9.64 MB | 日文识别 |
| rec_korean_PP-OCRv3_infer.onnx | 9.46 MB | 韩文识别 |
| rec_cyrillic_PP-OCRv3_infer.onnx | 8.57 MB | 俄文识别 |
| rec_en_PP-OCRv3_infer.onnx | 8.56 MB | 英文识别 |
| ch_PP-OCRv4_det_infer.onnx | 4.53 MB | 文本检测v4 |
| ch_PP-OCRv3_det_infer.onnx | 2.32 MB | 文本检测v3 |
| RapidOCR-json.exe | 16.07 MB | 主程序 |

**RapidOCR总大小**: 91.05 MB

---

## 3. 压缩包分析

| 文件名 | 大小 | 说明 |
|--------|------|------|
| PaddleOCR-json_v1.4.1_windows_x64.7z | 88.44 MB | PaddleOCR压缩包 |
| RapidOCR-json_v0.2.0.7z | 70.06 MB | RapidOCR压缩包 |

**压缩包总大小**: 158.50 MB

⚠️ **重要**: 这些压缩包在打包时应该被排除,因为已经有解压后的文件。

---

## 4. 优化建议

### 4.1 立即可执行的优化 (预计节省 ~36.46 MB)

#### 移除非中英文语言模型

| 语言 | 模型大小 | 配置文件 | 字典文件 |
|------|---------|---------|---------|
| 日文 (japan) | 10.84 MB | config_japan.txt | dict_japan.txt |
| 韩文 (korean) | 10.43 MB | config_korean.txt | dict_korean.txt |
| 俄文 (cyrillic) | 9.52 MB | config_cyrillic.txt | dict_cyrillic.txt |
| 繁体中文 (chinese_cht) | 5.67 MB | config_chinese_cht.txt | dict_chinese_cht.txt |

**可节省空间**: 36.46 MB

#### 需要删除的文件和目录:
```
models/PaddleOCR-json/PaddleOCR-json_v1.4.1/models/
├── japan_PP-OCRv3_rec_infer/          (删除)
├── korean_PP-OCRv3_rec_infer/         (删除)
├── cyrillic_PP-OCRv3_rec_infer/       (删除)
├── chinese_cht_mobile_v2.0_rec_infer/ (删除)
├── config_japan.txt                    (删除)
├── config_korean.txt                   (删除)
├── config_cyrillic.txt                 (删除)
├── config_chinese_cht.txt              (删除)
├── dict_japan.txt                      (删除)
├── dict_korean.txt                     (删除)
├── dict_cyrillic.txt                   (删除)
└── dict_chinese_cht.txt                (删除)
```

### 4.2 打包配置优化 (预计节省 ~158.50 MB)

#### 排除压缩包
在PyInstaller的spec文件中排除:
- `models/*.7z`
- `models/*.zip`

这些压缩包仅用于分发,打包时不需要包含。

### 4.3 引擎选择优化

#### 方案A: 仅打包RapidOCR (推荐)
- **优势**: 体积更小 (91 MB vs 296 MB)
- **劣势**: 识别精度可能略低
- **节省空间**: ~205 MB

#### 方案B: 仅打包PaddleOCR
- **优势**: 识别精度更高
- **劣势**: 体积较大
- **节省空间**: ~91 MB

#### 方案C: 两个引擎都打包,但设为可选下载
- **优势**: 用户可选择
- **劣势**: 实现复杂度高
- **初始包大小**: 仅包含一个引擎

### 4.4 DLL优化 (需要进一步研究)

大型DLL文件:
- `mklml.dll` (88.36 MB) - Intel MKL数学库,可能可以使用更小的版本
- `opencv_world4100.dll` (61.66 MB) - OpenCV,可能可以只包含必需模块

⚠️ **注意**: DLL优化需要谨慎,可能影响功能。

---

## 5. 优化效果预估

### 当前状态
- PaddleOCR: 296.35 MB
- RapidOCR: 91.05 MB
- 压缩包: 158.50 MB
- **总计**: ~546 MB

### 优化后 (保守估计)
- 移除非中英文模型: -36.46 MB
- 排除压缩包: -158.50 MB
- 选择单一引擎 (RapidOCR): -205 MB
- **预计节省**: ~400 MB
- **优化后大小**: ~146 MB

### 优化后 (激进方案)
- 移除非中英文模型: -36.46 MB
- 排除压缩包: -158.50 MB
- 选择单一引擎 (RapidOCR): -205 MB
- DLL优化: -50 MB (估计)
- **预计节省**: ~450 MB
- **优化后大小**: ~96 MB

---

## 6. 实施计划

### 阶段1: 立即执行 (任务2.2)
✅ 移除非中英文语言模型
- 删除日文、韩文、俄文、繁体中文模型
- 删除对应的配置和字典文件

### 阶段2: 打包配置 (任务2.4, 2.5)
✅ 更新PyInstaller配置
- 排除.7z压缩包
- 选择默认引擎

### 阶段3: 引擎优化 (任务8)
⏳ 实现引擎可选下载
- 默认打包RapidOCR
- PaddleOCR设为可选下载

### 阶段4: 深度优化 (可选)
⏳ DLL优化
- 研究MKL和OpenCV的精简版本
- 测试功能完整性

---

## 7. 风险评估

### 低风险
- ✅ 移除非中英文模型: 不影响核心功能
- ✅ 排除压缩包: 不影响运行

### 中风险
- ⚠️ 选择单一引擎: 需要确保识别精度满足需求
- ⚠️ 引擎可选下载: 需要实现下载和安装机制

### 高风险
- ⛔ DLL优化: 可能导致功能异常或性能下降

---

## 8. 结论

通过移除非必需的语言模型和优化打包配置,可以显著减小打包体积:
- **最小优化**: 节省 ~195 MB (移除模型 + 排除压缩包)
- **推荐优化**: 节省 ~400 MB (+ 选择单一引擎)
- **激进优化**: 节省 ~450 MB (+ DLL优化)

建议优先执行低风险和中风险的优化措施,在确保功能完整性的前提下逐步推进。
