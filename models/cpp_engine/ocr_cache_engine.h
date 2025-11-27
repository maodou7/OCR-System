/**
 * OCR Cache Engine - C API Header
 * 高性能OCR结果缓存引擎
 * 使用SQLite实现ACID事务保证数据不丢失
 */

#ifndef OCR_CACHE_ENGINE_H
#define OCR_CACHE_ENGINE_H

#ifdef __cplusplus
extern "C" {
#endif

/**
 * 初始化OCR缓存引擎
 * @param db_path 数据库文件路径
 * @return 引擎句柄，失败返回NULL
 */
void* ocr_engine_init(const char* db_path);

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
int ocr_engine_save_result(void* engine, 
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
char* ocr_engine_load_all(void* engine);

/**
 * 保存会话元数据
 * @param engine 引擎句柄
 * @param files_json 文件列表JSON字符串
 * @param cur_index 当前索引
 * @return 0=成功, -1=失败
 */
int ocr_engine_save_session(void* engine, 
                            const char* files_json,
                            int cur_index);

/**
 * 加载会话元数据
 * @param engine 引擎句柄
 * @return JSON格式字符串，需要调用ocr_engine_free_string释放
 */
char* ocr_engine_load_session(void* engine);

/**
 * 检查是否存在缓存数据
 * @param engine 引擎句柄
 * @return 1=存在, 0=不存在
 */
int ocr_engine_has_cache(void* engine);

/**
 * 清除所有缓存数据
 * @param engine 引擎句柄
 */
void ocr_engine_clear(void* engine);

/**
 * 销毁引擎并释放资源
 * @param engine 引擎句柄
 */
void ocr_engine_destroy(void* engine);

/**
 * 释放由引擎分配的字符串内存
 * @param str 字符串指针
 */
void ocr_engine_free_string(char* str);

/**
 * 获取最后的错误信息
 * @param engine 引擎句柄
 * @return 错误信息字符串（不需要释放）
 */
const char* ocr_engine_get_error(void* engine);

#ifdef __cplusplus
}
#endif

#endif // OCR_CACHE_ENGINE_H
