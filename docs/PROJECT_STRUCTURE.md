# 项目目录结构

本文档说明项目的目录结构和文件组织方式。

## 根目录文件

### 核心应用文件
- `qt_main.py` - 主应用程序入口
- `qt_run.py` - 应用启动脚本
- `qt_run_silent.pyw` - 无窗口启动脚本
- `启动程序(无黑窗).pyw` - 中文启动脚本
- `启动程序点这.bat` - 批处理启动脚本

### OCR引擎相关
- `ocr_cache_manager.py` - OCR缓存管理器
- `ocr_engine_manager.py` - OCR引擎管理器
- `ocr_engine_paddle.py` - PaddleOCR引擎
- `ocr_engine_rapid.py` - RapidOCR引擎
- `ocr_engine_aliyun_new.py` - 阿里云OCR引擎
- `ocr_engine_deepseek.py` - DeepSeek OCR引擎
- `ocr_engine_downloader.py` - 引擎下载器
- `ocr_engine_download_dialog.py` - 下载对话框
- `online_ocr_plugin_manager.py` - 在线OCR插件管理器
- `PPOCR_api.py` - PaddleOCR API封装

### 配置和工具
- `config.py` - 配置文件（不提交到Git）
- `config.py.example` - 配置文件模板
- `lightweight_config.py` - 轻量级配置
- `cache_manager_wrapper.py` - 缓存管理器包装器
- `cache_logging_config.py` - 缓存日志配置
- `dependency_manager.py` - 依赖管理器
- `utils.py` - 工具函数

### 项目文档
- `README.md` - 项目说明文档
- `requirements.txt` - Python依赖列表
- `.gitignore` - Git忽略文件配置
- `.env.example` - 环境变量模板
- `更新日志.txt` - 更新日志

## 目录结构

### `/docs` - 文档目录

#### `/docs/tasks` - 任务完成文档
包含所有 TASK_*.md 文件，记录各个任务的完成情况。

#### `/docs/analysis` - 分析报告
- 依赖分析报告
- 字体使用分析
- 图片资源分析
- 模型大小分析
- 包大小分析
- 启动性能分析
- 各种优化报告

#### `/docs/optimization` - 优化文档
- 配置文件优化
- 模型压缩指南
- 打包优化
- 资源文件优化
- 优化计划和进度

#### `/docs/guides` - 使用指南
- 清理指南
- 引擎下载指南
- 设置指南
- 构建配置
- 集成测试运行指南

#### `/docs/cache` - 缓存相关文档
- 缓存架构文档
- 缓存错误消息
- 缓存故障排除

#### `/docs/integration_tests` - 集成测试文档
- 集成测试README
- 集成测试总结

#### `/docs/completion` - 项目完成文档
- 项目完成总结
- 发布说明

### `/scripts` - 脚本工具目录

#### `/scripts/cleanup` - 清理脚本
- 自动清理冗余文件
- 打包前清理
- 图片资源清理
- 深度清理

#### `/scripts/verification` - 验证脚本
- 缓存诊断
- 启动模块检查
- 导入审查
- 图片清理验证
- 模型压缩集成验证

#### `/scripts/optimization` - 优化脚本
- 模型压缩器
- 模型解压器
- 优化的图片加载器

#### `/scripts/evaluation` - 评估脚本
- 移动端vs服务器端模型评估
- 配置加载基准测试

#### `/scripts/installation` - 安装脚本
- 在线OCR插件安装
- 配置向导

#### `/scripts/build` - 构建脚本
- Nuitka构建脚本

#### `/scripts/testing` - 测试运行脚本
- 运行所有集成测试
- 运行所有属性测试
- 最终验证

### `/tests` - 测试目录

#### `/tests/unit` - 单元测试
- 缓存引擎单元测试
- 配置管理测试
- JSON导入测试
- Qt主程序冒烟测试

#### `/tests/integration` - 集成测试
- 缓存包装器集成测试
- 缓存健壮性集成测试
- 各种集成测试（清洁环境、综合、功能、打包、性能）

#### `/tests/property` - 属性测试
- 缓存包装器属性测试
- 并发安全属性测试
- 内存管理属性测试

#### `/tests/performance` - 性能测试
- 缓存引擎性能测试
- 启动性能测试

#### `/tests/functional` - 功能测试
- 各种功能测试文件

### 其他重要目录

- `/models` - OCR模型文件
- `/Pack` - 打包相关文件
- `/Env-Config` - 环境配置
- `/test_images` - 测试图片
- `/.kiro` - Kiro配置和规范
- `/.ocr_cache` - OCR缓存数据
- `/.pytest_cache` - Pytest缓存
- `/.hypothesis` - Hypothesis测试数据
- `/portable_python` - 便携式Python环境
- `/__pycache__` - Python字节码缓存

## 文件组织原则

1. **核心代码保留在根目录** - 便于直接运行和导入
2. **文档按类型分类** - 便于查找和维护
3. **脚本按功能分类** - 清晰的职责划分
4. **测试按类型分类** - 单元、集成、属性、性能、功能测试分开

## 维护建议

- 新的任务完成文档放入 `/docs/tasks`
- 新的分析报告放入 `/docs/analysis`
- 新的工具脚本根据功能放入 `/scripts` 对应子目录
- 新的测试文件根据类型放入 `/tests` 对应子目录
- 核心功能代码保持在根目录
