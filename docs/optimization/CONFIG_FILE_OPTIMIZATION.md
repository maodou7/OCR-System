# 配置文件优化策略

## 概述

本文档说明配置文件的优化打包策略，确保打包体积最小化，同时提供良好的首次运行体验。

## 优化目标

**需求 5.3**: 优化配置文件打包策略
- 确保打包使用 `.example` 配置文件
- 移除开发环境的完整配置
- 添加首次运行时的配置向导

## 实施方案

### 1. 配置文件结构

```
项目根目录/
├── config.py.example      # 配置模板（打包）
├── config.py              # 开发配置（不打包，在.gitignore中）
├── config_wizard.py       # 配置向导（打包）
├── .env.example           # 环境变量模板（打包）
└── .env                   # 环境变量（不打包，在.gitignore中）
```

### 2. 打包策略

#### PyInstaller 配置

在 `ocr_system.spec` 和 `ocr_system_core.spec` 中：

```python
datas = [
    # 配置模板（打包）
    (os.path.join(project_root, 'config.py.example'), '.'),
    
    # 配置向导（打包）
    (os.path.join(project_root, 'config_wizard.py'), '.'),
    
    # 环境变量模板（打包）
    (os.path.join(project_root, '.env.example'), '.'),
]
```

**不打包的文件**:
- `config.py` - 开发环境配置
- `.env` - 开发环境变量

### 3. 首次运行流程

#### 启动流程 (qt_run.py)

```python
def ensure_config_file():
    """确保配置文件存在"""
    
    # 1. 检查 config.py 是否存在
    if not os.path.exists(config_path):
        # 2. 从 config.py.example 复制
        shutil.copy2(config_example_path, config_path)
        
        # 3. 运行配置向导
        run_config_wizard()
```

#### 配置向导功能 (config_wizard.py)

配置向导提供以下功能：

1. **欢迎信息**
   - 显示首次运行欢迎信息
   - 说明配置流程

2. **OCR引擎配置**
   - 检测已安装的OCR引擎
   - 显示引擎下载链接（如果未安装）
   - 说明各引擎的特点和适用场景

3. **在线OCR配置**
   - 说明如何配置API密钥
   - 提供配置文件编辑指导

4. **完成提示**
   - 显示配置完成信息
   - 提供下一步操作指导

### 4. 版本控制

#### .gitignore 配置

```gitignore
# 配置文件（不提交到Git）
config.py              # 开发配置
config_local.py        # 本地配置
*_secret.py            # 包含密钥的配置
.env                   # 环境变量
.env.local             # 本地环境变量
.env.*                 # 其他环境变量文件
!.env.example          # 保留模板文件
```

### 5. 打包前清理

#### cleanup_before_packaging.py

清理脚本会检查并提示：

```python
def clean_dev_config(self):
    """检查开发环境配置"""
    
    # 检查 config.py 和 .env
    if exists('config.py'):
        print("⚠ 发现开发配置文件: config.py")
        print("  提示: 此文件不应打包")
    
    # 验证打包配置
    print("✓ PyInstaller spec 已配置为只打包 .example 文件")
```

## 优势

### 1. 体积优化

- **减少打包体积**: 不包含开发环境的完整配置
- **避免冗余**: 只打包必需的模板文件

### 2. 安全性

- **保护敏感信息**: 开发环境的API密钥不会被打包
- **版本控制安全**: config.py 不会被提交到Git

### 3. 用户体验

- **首次运行引导**: 配置向导提供友好的设置流程
- **自动配置**: 从模板自动创建配置文件
- **灵活配置**: 用户可以随时修改外部配置文件

### 4. 可维护性

- **配置分离**: 开发配置和生产配置分离
- **模板更新**: 更新 config.py.example 即可影响所有新安装
- **向后兼容**: 支持从旧版本配置迁移

## 使用说明

### 开发环境

1. **首次设置**
   ```bash
   # 复制配置模板
   cp config.py.example config.py
   
   # 编辑配置
   vim config.py
   
   # 复制环境变量模板（可选）
   cp .env.example .env
   vim .env
   ```

2. **配置API密钥**
   - 方式1（推荐）: 在 `.env` 中配置
   - 方式2: 在 `config.py` 中直接填写

### 打包环境

1. **打包前清理**
   ```bash
   python cleanup_before_packaging.py
   ```

2. **执行打包**
   ```bash
   cd Pack/Pyinstaller
   pyinstaller ocr_system_core.spec
   ```

3. **验证打包结果**
   - 检查 dist 目录不包含 config.py
   - 检查 dist 目录包含 config.py.example
   - 检查 dist 目录包含 config_wizard.py

### 用户环境

1. **首次运行**
   - 程序自动从 config.py.example 创建 config.py
   - 配置向导自动运行，引导用户完成配置
   - 用户可以选择跳过向导，使用默认配置

2. **修改配置**
   - 编辑程序目录下的 config.py
   - 重启程序生效

3. **重置配置**
   - 删除 config.py
   - 重新运行程序，配置向导会再次运行

## 验证清单

- [x] config.py 已添加到 .gitignore
- [x] PyInstaller spec 文件只包含 config.py.example
- [x] PyInstaller spec 文件包含 config_wizard.py
- [x] qt_run.py 实现首次运行检测
- [x] qt_run.py 集成配置向导
- [x] cleanup_before_packaging.py 检查开发配置
- [x] 配置向导提供友好的用户体验

## 测试场景

### 场景1: 首次运行（无配置文件）

```
1. 用户启动程序
2. 检测到 config.py 不存在
3. 从 config.py.example 创建 config.py
4. 运行配置向导
5. 显示OCR引擎状态
6. 提供配置指导
7. 用户按回车继续
8. 程序正常启动
```

### 场景2: 已有配置文件

```
1. 用户启动程序
2. 检测到 config.py 存在
3. 跳过配置向导
4. 程序正常启动
```

### 场景3: 打包验证

```
1. 运行 cleanup_before_packaging.py
2. 检查是否有开发配置文件警告
3. 执行 PyInstaller 打包
4. 检查 dist 目录内容
5. 验证不包含 config.py
6. 验证包含 config.py.example
7. 验证包含 config_wizard.py
```

## 相关文件

- `config.py.example` - 配置模板
- `config_wizard.py` - 配置向导
- `qt_run.py` - 启动脚本（集成配置向导）
- `cleanup_before_packaging.py` - 打包前清理
- `.gitignore` - 版本控制配置
- `Pack/Pyinstaller/ocr_system.spec` - 完整版打包配置
- `Pack/Pyinstaller/ocr_system_core.spec` - 核心版打包配置

## 总结

通过配置文件优化策略，我们实现了：

1. ✅ **体积优化**: 不打包开发配置，减小打包体积
2. ✅ **安全性**: 保护敏感信息，不泄露API密钥
3. ✅ **用户体验**: 首次运行配置向导，友好的设置流程
4. ✅ **可维护性**: 配置分离，易于更新和维护

**验证需求 5.3**: ✓ 已完成

---

*文档生成时间: 2024-11-29*
