# 集成测试套件 - 使用说明

## 📋 目录

- [概述](#概述)
- [快速开始](#快速开始)
- [测试脚本](#测试脚本)
- [安装依赖](#安装依赖)
- [运行测试](#运行测试)
- [查看报告](#查看报告)
- [常见问题](#常见问题)

## 概述

本集成测试套件为OCR系统极致优化项目提供全面的测试覆盖，包括：

- ✅ 打包流程和体积分析
- ✅ 功能完整性验证
- ✅ 性能指标测试
- ✅ 干净环境测试
- ✅ 完整工作流和稳定性测试

## 快速开始

### 一键运行（推荐）

```bash
# Windows
run_all_integration_tests.bat

# 选择测试模式:
# 1. 快速测试 (约5分钟)
# 2. 完整测试 (约20-30分钟)
# 3-5. 单项测试
```

### 手动运行

```bash
# 1. 安装依赖
pip install PySide6 Pillow openpyxl PyMuPDF psutil

# 2. 运行快速测试
python test_integration_functionality.py
python test_integration_performance.py
python test_integration_comprehensive.py --quick
```

## 测试脚本

### 1. 打包测试 📦

**文件**: `test_integration_packaging.py`

**功能**:
- 执行打包前清理
- 运行PyInstaller打包
- 分析打包体积
- 验证优化目标

**运行**:
```bash
python test_integration_packaging.py
```

**输出**: `INTEGRATION_TEST_PACKAGING_REPORT.md`

**耗时**: 5-10分钟

---

### 2. 功能测试 ✅

**文件**: `test_integration_functionality.py`

**功能**:
- 测试核心模块导入
- 验证延迟加载机制
- 测试图像加载
- 测试OCR引擎
- 测试Excel导出
- 测试PDF处理
- 测试配置管理
- 测试缓存引擎

**运行**:
```bash
python test_integration_functionality.py
```

**输出**: `INTEGRATION_TEST_FUNCTIONALITY_REPORT.md`

**耗时**: 1-2分钟

---

### 3. 性能测试 ⚡

**文件**: `test_integration_performance.py`

**功能**:
- 测量启动时间
- 测量内存占用
- 检查模块加载
- 测试延迟加载性能
- 对比基线数据

**运行**:
```bash
python test_integration_performance.py
```

**输出**: 
- `INTEGRATION_TEST_PERFORMANCE_REPORT.md`
- `performance_current.json`

**耗时**: 2-3分钟

---

### 4. 干净环境测试 🖥️

**文件**: `test_integration_clean_environment.py`

**功能**:
- 生成测试检查清单
- 生成自动化检查脚本

**运行**:
```bash
python test_integration_clean_environment.py
```

**输出**:
- `CLEAN_ENVIRONMENT_TEST_CHECKLIST.md`
- `clean_env_auto_check.bat`

**使用**:
1. 准备Windows虚拟机
2. 复制打包程序到虚拟机
3. 复制 `clean_env_auto_check.bat` 到程序目录
4. 运行自动化检查
5. 按照检查清单进行完整测试

**耗时**: 30-60分钟（手动）

---

### 5. 完整工作流测试 🔄

**文件**: `test_integration_comprehensive.py`

**功能**:
- 测试完整工作流（启动→加载→识别→导出→清理）
- 内存泄漏测试（100个文件）
- 长时间稳定性测试（5分钟）

**运行**:
```bash
# 完整测试
python test_integration_comprehensive.py

# 快速测试（10个文件，1分钟）
python test_integration_comprehensive.py --quick

# 跳过稳定性测试
python test_integration_comprehensive.py --skip-stability
```

**输出**: `INTEGRATION_TEST_COMPREHENSIVE_REPORT.md`

**耗时**: 
- 完整: 10-15分钟
- 快速: 2-3分钟

## 安装依赖

### 必需依赖

```bash
pip install PySide6 Pillow openpyxl PyMuPDF
```

### 强烈推荐

```bash
pip install psutil  # 用于内存测试
```

### 打包测试额外需要

```bash
pip install pyinstaller
```

### 一键安装

```bash
pip install -r requirements.txt
pip install psutil pyinstaller
```

## 运行测试

### 方式1: 使用批处理脚本（推荐）

```bash
run_all_integration_tests.bat
```

选择测试模式:
- **选项1**: 快速测试（日常开发）
- **选项2**: 完整测试（发布前）
- **选项3-5**: 单项测试

### 方式2: 手动运行

#### 日常开发测试（5分钟）

```bash
python test_integration_functionality.py
python test_integration_performance.py
python test_integration_comprehensive.py --quick
```

#### 发布前完整测试（20-30分钟）

```bash
python test_integration_packaging.py
python test_integration_functionality.py
python test_integration_performance.py
python test_integration_comprehensive.py
python test_integration_clean_environment.py
```

### 方式3: 使用快速指南

参考 `RUN_INTEGRATION_TESTS.md` 获取详细说明。

## 查看报告

### 自动打开

批处理脚本会询问是否自动打开报告。

### 手动打开

```bash
# Windows
start INTEGRATION_TEST_FUNCTIONALITY_REPORT.md
start INTEGRATION_TEST_PERFORMANCE_REPORT.md
start INTEGRATION_TEST_COMPREHENSIVE_REPORT.md

# 或使用默认编辑器
notepad INTEGRATION_TEST_FUNCTIONALITY_REPORT.md
```

### 报告内容

每个报告包含:
- 📊 测试概述
- 📈 详细结果
- ✅ 目标验证
- 💡 优化建议
- 📝 结论

## 验证目标

### 体积优化 ✅

- [x] 核心程序 < 100MB
- [x] 含RapidOCR < 250MB
- [x] 相比完整版减少60-70%

### 性能优化 ✅

- [x] 窗口显示 < 1秒
- [x] 完全就绪 < 3秒
- [x] 空闲内存 < 200MB

### 功能完整性 ✅

- [x] 图像加载和显示
- [x] OCR识别
- [x] Excel导出
- [x] PDF处理
- [x] 延迟加载
- [x] 配置管理

### 稳定性 ✅

- [x] 无内存泄漏（<10MB增长）
- [x] 长时间运行稳定（<20MB增长）
- [x] 错误处理完善

## 常见问题

### Q: psutil未安装

**A**: 
```bash
pip install psutil
```

### Q: 打包测试失败

**A**: 检查:
1. PyInstaller是否安装: `pip install pyinstaller`
2. spec文件是否存在: `Pack/Pyinstaller/ocr_system_core.spec`
3. 磁盘空间是否充足（需要至少1GB）

### Q: 测试超时

**A**: 使用快速模式:
```bash
python test_integration_comprehensive.py --quick
```

### Q: 内存测试不准确

**A**: 
1. 确保psutil已安装
2. 关闭其他程序
3. 确保系统有足够内存（建议4GB+）

### Q: 如何在CI/CD中运行

**A**: 参考 `RUN_INTEGRATION_TESTS.md` 中的GitHub Actions示例。

### Q: 测试失败怎么办

**A**: 
1. 查看详细的测试报告
2. 检查错误信息
3. 根据报告中的建议进行修复
4. 重新运行测试

### Q: 如何建立性能基线

**A**: 
1. 首次运行性能测试会自动创建基线
2. 基线保存在 `performance_baseline.json`
3. 后续运行会自动对比基线

### Q: 虚拟机测试必须做吗

**A**: 
- 日常开发: 不必须
- 发布前: 强烈建议
- 目的: 验证在干净环境中的运行情况

## 测试频率建议

### 每次提交前
```bash
python test_integration_functionality.py
```

### 每日构建
```bash
run_all_integration_tests.bat
# 选择: 1. 快速测试
```

### 发布前
```bash
run_all_integration_tests.bat
# 选择: 2. 完整测试
# + 虚拟机测试
```

## 文档资源

- 📖 `TASK_12_INTEGRATION_TESTING_COMPLETION.md` - 任务完成报告
- 📖 `RUN_INTEGRATION_TESTS.md` - 快速运行指南
- 📖 `INTEGRATION_TESTS_SUMMARY.md` - 测试套件总结
- 📖 `INTEGRATION_TESTS_README.md` - 本文档

## 技术支持

如有问题，请:
1. 查看测试报告中的错误信息
2. 参考常见问题部分
3. 查看详细文档
4. 提交Issue

## 更新日志

### v1.0 (2024)
- ✅ 创建5个集成测试脚本
- ✅ 实现自动化测试流程
- ✅ 生成详细测试报告
- ✅ 提供一键运行脚本
- ✅ 完善文档说明

## 许可

本测试套件是OCR系统极致优化项目的一部分。

---

**最后更新**: 2024  
**版本**: 1.0  
**维护者**: OCR System Team

**祝测试顺利！** 🎉
