/**
 * OCR Cache Engine - C API Header
 * 高性能OCR结果缓存引擎
 * 使用SQLite实现ACID事务保证数据不丢失
 */

#ifndef OCR_CACHE_ENGINE_H
#define OCR_CACHE_ENGINE_H

// Windows DLL导出宏
#ifdef _WIN32
    #ifdef OCR_CACHE_EXPORTS
        #define OCR_CACHE_API __declspec(dllexport)
    #else
        #define OCR_CACHE_API __declspec(dllimport)
    #endif
#else
    #define OCR_CACHE_API
#endif

#ifdef __cplusplus
extern "C" {
#endif

/**
 * 初始化OCR缓存引擎
 * @param db_path 数据库文件路径
 * @return 引擎句柄，失败返回NULL
 */
OCR_CACHE_API void* ocr_engine_init(const char* db_path);

/**
 * 保存单个文件的OCR识别结果
 * @param engine 引擎句柄
 * @param file_path 文件路径
 * @param status 识别状态
 * @param rect_count 区域数量
 * @param rect_coords 区域坐标数组 [x1,y1,x2,y2, x1,y1,x2,y2, ...]
 * @param rect_texts 区域文本数组
 * @return 0=成功, -1=失败
 */
OCR_CACHE_API int ocr_engine_save_result(void* engine, 
                           const char* file_path,
                           const char* status,
                           int rect_count,
                           const double* rect_coords,
                           const char** rect_texts);

/**
 * 加载所有OCR结果
 * @param engine 引擎句柄
 * @return JSON格式字符串，需要调用ocr_engine_free_string释放
 */
OCR_CACHE_API char* ocr_engine_load_all(void* engine);

/**
 * 保存会话元数据
 * @param engine 引擎句柄
 * @param files_json 文件列表JSON字符串
 * @param cur_index 当前索引
 * @return 0=成功, -1=失败
 */
OCR_CACHE_API int ocr_engine_save_session(void* engine, 
                            const char* files_json,
                            int cur_index);

/**
 * 加载会话元数据
 * @param engine 引擎句柄
 * @return JSON格式字符串，需要调用ocr_engine_free_string释放
 */
OCR_CACHE_API char* ocr_engine_load_session(void* engine);

/**
 * 检查是否存在缓存数据
 * @param engine 引擎句柄
 * @return 1=存在, 0=不存在
 */
OCR_CACHE_API int ocr_engine_has_cache(void* engine);

/**
 * 清除所有缓存数据
 * @param engine 引擎句柄
 */
OCR_CACHE_API void ocr_engine_clear(void* engine);

/**
 * 销毁引擎并释放资源
 * @param engine 引擎句柄
 */
OCR_CACHE_API void ocr_engine_destroy(void* engine);

/**
 * 释放由引擎分配的字符串内存
 * @param str 字符串指针
 */
OCR_CACHE_API void ocr_engine_free_string(char* str);

/**
 * 获取最后的错误信息
 * @param engine 引擎句柄
 * @return 错误信息字符串（不需要释放）
 */
OCR_CACHE_API const char* ocr_engine_get_error(void* engine);

/**
 * 测试引擎是否正常工作
 * 执行基本的数据库操作测试，验证引擎健康状态
 * @param engine 引擎句柄
 * @return 1=正常, 0=异常
 */
OCR_CACHE_API int ocr_engine_test(void* engine);

/**
 * 获取引擎版本信息
 * @return 版本字符串（格式: "OCR Cache Engine v1.0.0 (SQLite 3.x.x)"）
 */
OCR_CACHE_API const char* ocr_engine_version(void);

#ifdef __cplusplus
}
#endif

#endif // OCR_CACHE_ENGINE_H
