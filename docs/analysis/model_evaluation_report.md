# OCR模型评估报告 - Mobile vs Server

**评估时间**: 2025-11-28 22:15:00

## 1. 当前模型配置

| 模型类型 | 模型名称 | 版本 | 大小(MB) |
|---------|---------|------|----------|
| detection | ch_PP-OCRv3_det_infer | server | 3.64 |
| recognition_ch | ch_PP-OCRv3_rec_infer | server | 11.35 |
| recognition_en | en_PP-OCRv3_rec_infer | server | 9.5 |
| classification | ch_ppocr_mobile_v2.0_cls_infer | mobile | 1.38 |

**总计**: 25.87 MB

## 2. 识别准确率测试

**总体准确率**: 87.18%

**统计**: 102/117 字符正确

### 详细测试结果

| 测试用例 | 期望文本 | 识别文本 | 准确率 | 状态 |
|---------|---------|---------|--------|------|
| simple_chinese | 你好世界 | 你好世界 | 100.0% | ✓ |
| simple_english | Hello World | Hello World | 100.0% | ✓ |
| mixed_text | OCR识别测试Test123 | OCR识别测试Test123 | 100.0% | ✓ |
| numbers | 1234567890 | 1234567890 | 100.0% | ✓ |
| long_chinese | 这是一段较长的中文文本用于测试OCR识别准确率 | 这是一段较长的中文文本用于测试OCR识 | 82.6% | ✗ |
| long_english | This is a longer English text for testing OCR accuracy | This is a longer English text for testing | 75.6% | ✗ |
| punctuation | 你好这是测试 | 你好这是测试 | 100.0% | ✓ |
| special_chars | 价格99元 | 价格99元 | 100.0% | ✓ |

## 3. Mobile vs Server 对比分析

### 当前配置 (Server版本)

- **检测模型**: ch_PP-OCRv3_det_infer (~3.6 MB)
- **识别模型**: ch_PP-OCRv3_rec_infer (~11.3 MB)
- **分类模型**: ch_ppocr_mobile_v2.0_cls_infer (~1.4 MB) [已是Mobile版]

### 如果切换到 Mobile 版本

- **检测模型**: ch_ppocr_mobile_v2.0_det_infer (~2.6 MB) [节省 ~1 MB]
- **识别模型**: ch_ppocr_mobile_v2.0_rec_infer (~4.4 MB) [节省 ~7 MB]
- **预计总节省**: ~8 MB

## 4. 建议

当前Server模型准确率较低 (<90%)。
建议: 保持使用Server模型，或检查测试数据和配置。

## 5. 注意事项

1. 本评估使用合成测试图片，实际场景可能有差异
2. Mobile模型体积更小但精度可能略低
3. 建议使用实际业务图片进行更全面的测试
4. 如需下载Mobile模型，请访问PaddleOCR官方仓库
