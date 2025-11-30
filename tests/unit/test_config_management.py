"""
配置管理单元测试

测试轻量级配置管理器的功能：
- 配置加载和缓存
- 配置验证
- 默认配置生成
"""

import os
import sys
import tempfile
import shutil
from lightweight_config import LightweightConfig


class TestLightweightConfig:
    """轻量级配置管理器测试"""
    
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """每个测试前后的设置和清理"""
        # 保存原始配置
        self.original_cache = LightweightConfig._config_cache
        self.original_mtime = LightweightConfig._config_file_mtime
        
        # 创建临时目录
        self.temp_dir = tempfile.mkdtemp()
        self.original_get_config_dir = LightweightConfig.get_config_dir
        
        # 修改配置目录为临时目录
        LightweightConfig.get_config_dir = classmethod(lambda cls: self.temp_dir)
        
        # 清除缓存
        LightweightConfig.clear_cache()
        
        yield
        
        # 恢复原始配置
        LightweightConfig._config_cache = self.original_cache
        LightweightConfig._config_file_mtime = self.original_mtime
        LightweightConfig.get_config_dir = self.original_get_config_dir
        
        # 清理临时目录
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_load_default_config(self):
        """测试加载默认配置"""
        config = LightweightConfig.load()
        
        # 验证默认配置存在
        assert config is not None
        assert isinstance(config, dict)
        
        # 验证关键配置项
        assert config['APP_NAME'] == 'OCR系统'
        assert config['APP_VERSION'] == '1.4.1'
        assert config['OCR_ENGINE'] == 'rapid'
        assert config['WINDOW_WIDTH'] == '1400'
        assert config['WINDOW_HEIGHT'] == '800'
    
    def test_config_caching(self):
        """测试配置缓存机制"""
        # 第一次加载
        config1 = LightweightConfig.load()
        
        # 第二次加载（应该使用缓存）
        config2 = LightweightConfig.load()
        
        # 验证返回的是同一个对象（缓存生效）
        assert config1 is config2
        
        # 强制重新加载
        config3 = LightweightConfig.load(force_reload=True)
        
        # 验证配置内容相同但对象不同
        assert config1 == config3
        assert config1 is not config3
    
    def test_save_and_load_config(self):
        """测试保存和加载配置"""
        # 创建测试配置
        test_config = LightweightConfig.DEFAULT_CONFIG.copy()
        test_config['OCR_ENGINE'] = 'paddle'
        test_config['WINDOW_WIDTH'] = '1920'
        test_config['PADDLE_ENABLED'] = 'True'
        
        # 保存配置
        result = LightweightConfig.save(test_config)
        assert result is True
        
        # 清除缓存
        LightweightConfig.clear_cache()
        
        # 重新加载配置
        loaded_config = LightweightConfig.load()
        
        # 验证配置正确保存和加载
        assert loaded_config['OCR_ENGINE'] == 'paddle'
        assert loaded_config['WINDOW_WIDTH'] == '1920'
        assert loaded_config['PADDLE_ENABLED'] == 'True'
    
    def test_config_validation_int(self):
        """测试整数配置验证"""
        # 有效配置
        valid_config = {
            'WINDOW_WIDTH': '1920',
            'WINDOW_HEIGHT': '1080',
        }
        is_valid, errors = LightweightConfig.validate(valid_config)
        assert is_valid is True
        assert len(errors) == 0
        
        # 无效配置（超出范围）
        invalid_config = {
            'WINDOW_WIDTH': '5000',  # 超过最大值3840
            'WINDOW_HEIGHT': '500',  # 小于最小值600
        }
        is_valid, errors = LightweightConfig.validate(invalid_config)
        assert is_valid is False
        assert len(errors) == 2
    
    def test_config_validation_float(self):
        """测试浮点数配置验证"""
        # 有效配置
        valid_config = {
            'OCR_DET_DB_THRESH': '0.3',
            'MAX_DISPLAY_SCALE': '2.0',
        }
        is_valid, errors = LightweightConfig.validate(valid_config)
        assert is_valid is True
        assert len(errors) == 0
        
        # 无效配置（超出范围）
        invalid_config = {
            'OCR_DET_DB_THRESH': '1.5',  # 超过最大值1.0
            'MAX_DISPLAY_SCALE': '0.05',  # 小于最小值0.1
        }
        is_valid, errors = LightweightConfig.validate(invalid_config)
        assert is_valid is False
        assert len(errors) == 2
    
    def test_config_validation_bool(self):
        """测试布尔值配置验证"""
        # 有效配置
        valid_config = {
            'PADDLE_ENABLED': 'True',
            'RAPID_ENABLED': 'False',
            'OCR_SHOW_LOG': 'true',
        }
        is_valid, errors = LightweightConfig.validate(valid_config)
        assert is_valid is True
        assert len(errors) == 0
        
        # 无效配置
        invalid_config = {
            'PADDLE_ENABLED': 'yes',  # 不是标准布尔值
            'RAPID_ENABLED': 'no',
        }
        is_valid, errors = LightweightConfig.validate(invalid_config)
        assert is_valid is False
        assert len(errors) == 2
    
    def test_config_validation_choice(self):
        """测试选项配置验证"""
        # 有效配置
        valid_config = {
            'OCR_ENGINE': 'paddle',
            'OCR_USE_GPU': 'auto',
        }
        is_valid, errors = LightweightConfig.validate(valid_config)
        assert is_valid is True
        assert len(errors) == 0
        
        # 无效配置
        invalid_config = {
            'OCR_ENGINE': 'invalid_engine',
            'OCR_USE_GPU': 'maybe',
        }
        is_valid, errors = LightweightConfig.validate(invalid_config)
        assert is_valid is False
        assert len(errors) == 2
    
    def test_get_set_methods(self):
        """测试get和set方法"""
        # 设置配置值
        result = LightweightConfig.set('OCR_ENGINE', 'paddle')
        assert result is True
        
        # 获取配置值
        value = LightweightConfig.get('OCR_ENGINE')
        assert value == 'paddle'
        
        # 获取不存在的配置（使用默认值）
        value = LightweightConfig.get('NON_EXISTENT_KEY', 'default_value')
        assert value == 'default_value'
    
    def test_get_typed_methods(self):
        """测试类型化的get方法"""
        # 设置测试配置
        test_config = {
            'WINDOW_WIDTH': '1920',
            'MAX_DISPLAY_SCALE': '2.5',
            'PADDLE_ENABLED': 'True',
            'RAPID_ENABLED': 'False',
        }
        LightweightConfig.save(test_config)
        LightweightConfig.clear_cache()
        
        # 测试get_int
        width = LightweightConfig.get_int('WINDOW_WIDTH')
        assert width == 1920
        assert isinstance(width, int)
        
        # 测试get_float
        scale = LightweightConfig.get_float('MAX_DISPLAY_SCALE')
        assert scale == 2.5
        assert isinstance(scale, float)
        
        # 测试get_bool
        paddle_enabled = LightweightConfig.get_bool('PADDLE_ENABLED')
        assert paddle_enabled is True
        assert isinstance(paddle_enabled, bool)
        
        rapid_enabled = LightweightConfig.get_bool('RAPID_ENABLED')
        assert rapid_enabled is False
        assert isinstance(rapid_enabled, bool)
    
    def test_reset_to_default(self):
        """测试重置为默认配置"""
        # 修改配置
        LightweightConfig.set('OCR_ENGINE', 'paddle')
        LightweightConfig.set('WINDOW_WIDTH', '1920')
        
        # 重置为默认配置
        result = LightweightConfig.reset_to_default()
        assert result is True
        
        # 清除缓存并重新加载
        LightweightConfig.clear_cache()
        config = LightweightConfig.load()
        
        # 验证配置已重置
        assert config['OCR_ENGINE'] == 'rapid'
        assert config['WINDOW_WIDTH'] == '1400'
    
    def test_parse_ini_format(self):
        """测试INI格式解析"""
        # 创建测试INI文件
        config_file = LightweightConfig.get_config_file()
        os.makedirs(os.path.dirname(config_file), exist_ok=True)
        
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write("# 测试配置文件\n")
            f.write("\n")
            f.write("[General]\n")
            f.write("OCR_ENGINE = paddle\n")
            f.write("WINDOW_WIDTH = 1920\n")
            f.write('COLOR_PRIMARY = "#FF0000"\n')
            f.write("# 这是注释\n")
            f.write("PADDLE_ENABLED = True\n")
        
        # 清除缓存并加载
        LightweightConfig.clear_cache()
        config = LightweightConfig.load()
        
        # 验证解析结果
        assert config['OCR_ENGINE'] == 'paddle'
        assert config['WINDOW_WIDTH'] == '1920'
        assert config['COLOR_PRIMARY'] == '#FF0000'
        assert config['PADDLE_ENABLED'] == 'True'
    
    def test_cache_invalidation_on_file_change(self):
        """测试文件修改时缓存失效"""
        # 保存初始配置
        initial_config = LightweightConfig.DEFAULT_CONFIG.copy()
        initial_config['OCR_ENGINE'] = 'rapid'
        LightweightConfig.save(initial_config)
        
        # 加载配置（建立缓存）
        config1 = LightweightConfig.load()
        assert config1['OCR_ENGINE'] == 'rapid'
        
        # 直接修改配置文件
        import time
        time.sleep(0.1)  # 确保修改时间不同
        
        config_file = LightweightConfig.get_config_file()
        with open(config_file, 'a', encoding='utf-8') as f:
            f.write("\nOCR_ENGINE = paddle\n")
        
        # 重新加载（应该检测到文件变化）
        config2 = LightweightConfig.load()
        assert config2['OCR_ENGINE'] == 'paddle'


class TestConfigBackwardCompatibility:
    """测试Config类的向后兼容性"""
    
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """每个测试前后的设置和清理"""
        # 创建临时目录
        self.temp_dir = tempfile.mkdtemp()
        
        # 保存原始方法
        from config import Config
        self.original_get_config_dir = Config._get_config_dir
        
        # 修改配置目录为临时目录
        Config._get_config_dir = classmethod(lambda cls: self.temp_dir)
        LightweightConfig.get_config_dir = classmethod(lambda cls: self.temp_dir)
        
        # 清除缓存
        LightweightConfig.clear_cache()
        
        yield
        
        # 恢复原始方法
        Config._get_config_dir = self.original_get_config_dir
        
        # 清理临时目录
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_load_user_config(self):
        """测试加载用户配置"""
        from config import Config
        
        # 加载配置（应该返回默认配置）
        config = Config.load_user_config()
        
        assert config is not None
        assert isinstance(config, dict)
        assert 'APP_NAME' in config
    
    def test_save_user_config(self):
        """测试保存用户配置"""
        from config import Config
        
        # 保存配置
        test_config = {
            'OCR_ENGINE': 'paddle',
            'WINDOW_WIDTH': 1920,
            'PADDLE_ENABLED': True,
        }
        
        result = Config.save_user_config(test_config)
        assert result is True
        
        # 清除缓存并重新加载
        LightweightConfig.clear_cache()
        loaded_config = Config.load_user_config()
        
        # 验证配置正确保存（注意：值会被转换为字符串）
        assert loaded_config['OCR_ENGINE'] == 'paddle'
        assert loaded_config['WINDOW_WIDTH'] == '1920'
        assert loaded_config['PADDLE_ENABLED'] == 'True'
    
    def test_config_helper_methods(self):
        """测试Config类的辅助方法"""
        from config import Config
        
        # 保存测试配置
        test_config = {
            'WINDOW_WIDTH': '1920',
            'MAX_DISPLAY_SCALE': '2.5',
            'PADDLE_ENABLED': 'True',
        }
        LightweightConfig.save(test_config)
        LightweightConfig.clear_cache()
        
        # 测试get方法
        width = Config.get_config_int('WINDOW_WIDTH')
        assert width == 1920
        
        scale = Config.get_config_float('MAX_DISPLAY_SCALE')
        assert scale == 2.5
        
        enabled = Config.get_config_bool('PADDLE_ENABLED')
        assert enabled is True
        
        # 测试set方法
        result = Config.set_config_value('OCR_ENGINE', 'paddle')
        assert result is True
        
        value = Config.get_config_value('OCR_ENGINE')
        assert value == 'paddle'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
