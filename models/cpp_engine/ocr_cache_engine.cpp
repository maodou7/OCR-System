/**
 * OCR Cache Engine - Implementation
 * 使用SQLite实现高性能、ACID安全的OCR结果缓存
 */

#include "ocr_cache_engine.h"
#include <sqlite3.h>
#include <string>
#include <sstream>
#include <cstring>
#include <ctime>
#include <vector>

// 引擎版本信息
#define OCR_CACHE_ENGINE_VERSION "1.0.0"

// 引擎内部结构
struct OCRCacheEngine {
    sqlite3* db;
    std::string last_error;
    std::string init_stage;  // 记录初始化到哪个阶段
    
    OCRCacheEngine() : db(nullptr), init_stage("not_started") {}
    
    // 设置详细错误信息
    void set_error(const std::string& stage, const std::string& message) {
        init_stage = stage;
        last_error = "[" + stage + "] " + message;
    }
};

// 辅助函数：转义JSON字符串
static std::string escape_json_string(const char* str) {
    if (!str) return "null";
    
    std::string result = "\"";
    for (const char* p = str; *p; ++p) {
        switch (*p) {
            case '"':  result += "\\\""; break;
            case '\\': result += "\\\\"; break;
            case '\n': result += "\\n"; break;
            case '\r': result += "\\r"; break;
            case '\t': result += "\\t"; break;
            default:   result += *p; break;
        }
    }
    result += "\"";
    return result;
}

// 辅助函数：获取当前时间戳
static std::string get_timestamp() {
    time_t now = time(nullptr);
    char buf[64];
    
    // 使用线程安全的localtime版本
    #ifdef _WIN32
        struct tm timeinfo;
        if (localtime_s(&timeinfo, &now) == 0) {
            strftime(buf, sizeof(buf), "%Y-%m-%d %H:%M:%S", &timeinfo);
        } else {
            strcpy(buf, "1970-01-01 00:00:00");
        }
    #else
        struct tm* timeinfo = localtime(&now);
        if (timeinfo) {
            strftime(buf, sizeof(buf), "%Y-%m-%d %H:%M:%S", timeinfo);
        } else {
            strcpy(buf, "1970-01-01 00:00:00");
        }
    #endif
    
    return buf;
}

// 初始化数据库表结构
static bool init_database_schema(sqlite3* db, std::string& error) {
    const char* schema[] = {
        // 文件表
        "CREATE TABLE IF NOT EXISTS files ("
        "  id INTEGER PRIMARY KEY AUTOINCREMENT,"
        "  file_path TEXT UNIQUE NOT NULL,"
        "  status TEXT,"
        "  updated_at TEXT"
        ")",
        
        // OCR区域表
        "CREATE TABLE IF NOT EXISTS ocr_rects ("
        "  id INTEGER PRIMARY KEY AUTOINCREMENT,"
        "  file_path TEXT NOT NULL,"
        "  rect_index INTEGER NOT NULL,"
        "  x1 REAL NOT NULL,"
        "  y1 REAL NOT NULL,"
        "  x2 REAL NOT NULL,"
        "  y2 REAL NOT NULL,"
        "  text TEXT,"
        "  FOREIGN KEY(file_path) REFERENCES files(file_path) ON DELETE CASCADE"
        ")",
        
        // 会话元数据表
        "CREATE TABLE IF NOT EXISTS session ("
        "  key TEXT PRIMARY KEY,"
        "  value TEXT,"
        "  updated_at TEXT"
        ")",
        
        // 索引
        "CREATE INDEX IF NOT EXISTS idx_rects_file_path ON ocr_rects(file_path)",
        "CREATE INDEX IF NOT EXISTS idx_rects_file_index ON ocr_rects(file_path, rect_index)"
    };
    
    char* err_msg = nullptr;
    for (const char* sql : schema) {
        if (sqlite3_exec(db, sql, nullptr, nullptr, &err_msg) != SQLITE_OK) {
            error = err_msg ? err_msg : "Unknown error";
            if (err_msg) sqlite3_free(err_msg);
            return false;
        }
    }
    
    return true;
}

// ==================== C API 实现 ====================

void* ocr_engine_init(const char* db_path) {
    if (!db_path) {
        // 无法创建引擎对象来存储错误，直接返回
        return nullptr;
    }
    
    OCRCacheEngine* engine = new OCRCacheEngine();
    engine->init_stage = "created";
    
    // 验证数据库路径
    engine->init_stage = "validating_path";
    if (strlen(db_path) == 0) {
        engine->set_error("validating_path", "Database path is empty");
        delete engine;
        return nullptr;
    }
    
    // 打开数据库
    engine->init_stage = "opening_database";
    int rc = sqlite3_open(db_path, &engine->db);
    if (rc != SQLITE_OK) {
        std::string error_msg = "Failed to open database: ";
        error_msg += sqlite3_errmsg(engine->db);
        error_msg += " (SQLite error code: " + std::to_string(rc) + ")";
        error_msg += " at path: ";
        error_msg += db_path;
        engine->set_error("opening_database", error_msg);
        sqlite3_close(engine->db);
        delete engine;
        return nullptr;
    }
    
    // 验证数据库可写
    engine->init_stage = "testing_write_access";
    char* err_msg = nullptr;
    if (sqlite3_exec(engine->db, "CREATE TABLE IF NOT EXISTS _test_write (id INTEGER)", 
                     nullptr, nullptr, &err_msg) != SQLITE_OK) {
        std::string error_msg = "Database is not writable: ";
        error_msg += err_msg ? err_msg : "Unknown error";
        if (err_msg) sqlite3_free(err_msg);
        engine->set_error("testing_write_access", error_msg);
        sqlite3_close(engine->db);
        delete engine;
        return nullptr;
    }
    sqlite3_exec(engine->db, "DROP TABLE IF EXISTS _test_write", nullptr, nullptr, nullptr);
    
    // 启用外键约束
    engine->init_stage = "configuring_pragmas";
    if (sqlite3_exec(engine->db, "PRAGMA foreign_keys = ON", nullptr, nullptr, &err_msg) != SQLITE_OK) {
        std::string error_msg = "Failed to enable foreign keys: ";
        error_msg += err_msg ? err_msg : "Unknown error";
        if (err_msg) sqlite3_free(err_msg);
        engine->set_error("configuring_pragmas", error_msg);
        sqlite3_close(engine->db);
        delete engine;
        return nullptr;
    }
    
    // 性能优化设置
    sqlite3_exec(engine->db, "PRAGMA journal_mode = WAL", nullptr, nullptr, nullptr);
    sqlite3_exec(engine->db, "PRAGMA synchronous = NORMAL", nullptr, nullptr, nullptr);
    sqlite3_exec(engine->db, "PRAGMA cache_size = 10000", nullptr, nullptr, nullptr);
    
    // 初始化表结构
    engine->init_stage = "creating_schema";
    std::string schema_error;
    if (!init_database_schema(engine->db, schema_error)) {
        engine->set_error("creating_schema", "Failed to create database schema: " + schema_error);
        sqlite3_close(engine->db);
        delete engine;
        return nullptr;
    }
    
    // 验证表结构
    engine->init_stage = "verifying_schema";
    const char* verify_sql = "SELECT name FROM sqlite_master WHERE type='table' AND name IN ('files', 'ocr_rects', 'session')";
    sqlite3_stmt* stmt;
    if (sqlite3_prepare_v2(engine->db, verify_sql, -1, &stmt, nullptr) != SQLITE_OK) {
        engine->set_error("verifying_schema", "Failed to verify schema: " + std::string(sqlite3_errmsg(engine->db)));
        sqlite3_close(engine->db);
        delete engine;
        return nullptr;
    }
    
    int table_count = 0;
    while (sqlite3_step(stmt) == SQLITE_ROW) {
        table_count++;
    }
    sqlite3_finalize(stmt);
    
    if (table_count < 3) {
        engine->set_error("verifying_schema", "Schema verification failed: expected 3 tables, found " + std::to_string(table_count));
        sqlite3_close(engine->db);
        delete engine;
        return nullptr;
    }
    
    engine->init_stage = "completed";
    engine->last_error = "";  // 清除错误信息
    return engine;
}

int ocr_engine_save_result(void* engine_ptr,
                           const char* file_path,
                           const char* status,
                           int rect_count,
                           const double* rect_coords,
                           const char** rect_texts) {
    if (!engine_ptr) {
        return -1;
    }
    
    OCRCacheEngine* engine = static_cast<OCRCacheEngine*>(engine_ptr);
    
    if (!file_path) {
        engine->set_error("save_result", "File path is NULL");
        return -1;
    }
    
    if (rect_count < 0) {
        engine->set_error("save_result", "Invalid rect_count: " + std::to_string(rect_count));
        return -1;
    }
    
    if (rect_count > 0 && (!rect_coords || !rect_texts)) {
        engine->set_error("save_result", "rect_coords or rect_texts is NULL when rect_count > 0");
        return -1;
    }
    
    char* err_msg = nullptr;
    
    // 开始事务
    if (sqlite3_exec(engine->db, "BEGIN TRANSACTION", nullptr, nullptr, &err_msg) != SQLITE_OK) {
        std::string error_msg = "Failed to begin transaction: ";
        error_msg += err_msg ? err_msg : "Unknown error";
        engine->set_error("save_result", error_msg);
        if (err_msg) sqlite3_free(err_msg);
        return -1;
    }
    
    // 插入或更新文件记录
    std::string timestamp = get_timestamp();
    sqlite3_stmt* stmt;
    const char* sql_file = "INSERT OR REPLACE INTO files (file_path, status, updated_at) VALUES (?, ?, ?)";
    
    if (sqlite3_prepare_v2(engine->db, sql_file, -1, &stmt, nullptr) != SQLITE_OK) {
        std::string error_msg = "Failed to prepare file insert statement: ";
        error_msg += sqlite3_errmsg(engine->db);
        engine->set_error("save_result", error_msg);
        sqlite3_exec(engine->db, "ROLLBACK", nullptr, nullptr, nullptr);
        return -1;
    }
    
    sqlite3_bind_text(stmt, 1, file_path, -1, SQLITE_TRANSIENT);
    sqlite3_bind_text(stmt, 2, status ? status : "", -1, SQLITE_TRANSIENT);
    sqlite3_bind_text(stmt, 3, timestamp.c_str(), -1, SQLITE_TRANSIENT);
    
    if (sqlite3_step(stmt) != SQLITE_DONE) {
        std::string error_msg = "Failed to insert/update file record for '";
        error_msg += file_path;
        error_msg += "': ";
        error_msg += sqlite3_errmsg(engine->db);
        engine->set_error("save_result", error_msg);
        sqlite3_finalize(stmt);
        sqlite3_exec(engine->db, "ROLLBACK", nullptr, nullptr, nullptr);
        return -1;
    }
    sqlite3_finalize(stmt);
    
    // 删除该文件的旧区域数据
    const char* sql_delete = "DELETE FROM ocr_rects WHERE file_path = ?";
    if (sqlite3_prepare_v2(engine->db, sql_delete, -1, &stmt, nullptr) != SQLITE_OK) {
        std::string error_msg = "Failed to prepare delete statement: ";
        error_msg += sqlite3_errmsg(engine->db);
        engine->set_error("save_result", error_msg);
        sqlite3_exec(engine->db, "ROLLBACK", nullptr, nullptr, nullptr);
        return -1;
    }
    
    sqlite3_bind_text(stmt, 1, file_path, -1, SQLITE_TRANSIENT);
    if (sqlite3_step(stmt) != SQLITE_DONE) {
        std::string error_msg = "Failed to delete old rects for '";
        error_msg += file_path;
        error_msg += "': ";
        error_msg += sqlite3_errmsg(engine->db);
        engine->set_error("save_result", error_msg);
        sqlite3_finalize(stmt);
        sqlite3_exec(engine->db, "ROLLBACK", nullptr, nullptr, nullptr);
        return -1;
    }
    sqlite3_finalize(stmt);
    
    // 插入新的区域数据
    if (rect_count > 0 && rect_coords && rect_texts) {
        const char* sql_rect = "INSERT INTO ocr_rects (file_path, rect_index, x1, y1, x2, y2, text) "
                              "VALUES (?, ?, ?, ?, ?, ?, ?)";
        
        if (sqlite3_prepare_v2(engine->db, sql_rect, -1, &stmt, nullptr) != SQLITE_OK) {
            std::string error_msg = "Failed to prepare rect insert statement: ";
            error_msg += sqlite3_errmsg(engine->db);
            engine->set_error("save_result", error_msg);
            sqlite3_exec(engine->db, "ROLLBACK", nullptr, nullptr, nullptr);
            return -1;
        }
        
        for (int i = 0; i < rect_count; ++i) {
            sqlite3_reset(stmt);
            sqlite3_bind_text(stmt, 1, file_path, -1, SQLITE_TRANSIENT);
            sqlite3_bind_int(stmt, 2, i);
            sqlite3_bind_double(stmt, 3, rect_coords[i * 4 + 0]);
            sqlite3_bind_double(stmt, 4, rect_coords[i * 4 + 1]);
            sqlite3_bind_double(stmt, 5, rect_coords[i * 4 + 2]);
            sqlite3_bind_double(stmt, 6, rect_coords[i * 4 + 3]);
            sqlite3_bind_text(stmt, 7, rect_texts[i] ? rect_texts[i] : "", -1, SQLITE_TRANSIENT);
            
            if (sqlite3_step(stmt) != SQLITE_DONE) {
                std::string error_msg = "Failed to insert rect #";
                error_msg += std::to_string(i);
                error_msg += " for '";
                error_msg += file_path;
                error_msg += "': ";
                error_msg += sqlite3_errmsg(engine->db);
                engine->set_error("save_result", error_msg);
                sqlite3_finalize(stmt);
                sqlite3_exec(engine->db, "ROLLBACK", nullptr, nullptr, nullptr);
                return -1;
            }
        }
        
        sqlite3_finalize(stmt);
    }
    
    // 提交事务
    if (sqlite3_exec(engine->db, "COMMIT", nullptr, nullptr, &err_msg) != SQLITE_OK) {
        std::string error_msg = "Failed to commit transaction: ";
        error_msg += err_msg ? err_msg : "Unknown error";
        engine->set_error("save_result", error_msg);
        if (err_msg) sqlite3_free(err_msg);
        sqlite3_exec(engine->db, "ROLLBACK", nullptr, nullptr, nullptr);
        return -1;
    }
    
    return 0;
}

char* ocr_engine_load_all(void* engine_ptr) {
    if (!engine_ptr) return nullptr;
    
    OCRCacheEngine* engine = static_cast<OCRCacheEngine*>(engine_ptr);
    std::ostringstream json;
    json << "{";
    
    // 查询所有文件
    const char* sql = "SELECT file_path, status FROM files ORDER BY file_path";
    sqlite3_stmt* stmt;
    
    if (sqlite3_prepare_v2(engine->db, sql, -1, &stmt, nullptr) != SQLITE_OK) {
        std::string error_msg = "Failed to prepare load_all query: ";
        error_msg += sqlite3_errmsg(engine->db);
        engine->set_error("load_all", error_msg);
        return nullptr;
    }
    
    bool first_file = true;
    while (sqlite3_step(stmt) == SQLITE_ROW) {
        const char* file_path = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 0));
        const char* status = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 1));
        
        if (!first_file) json << ",";
        first_file = false;
        
        json << escape_json_string(file_path) << ":{";
        json << "\"status\":" << escape_json_string(status) << ",";
        json << "\"rects\":[";
        
        // 查询该文件的所有区域
        const char* sql_rects = "SELECT x1, y1, x2, y2, text FROM ocr_rects "
                               "WHERE file_path = ? ORDER BY rect_index";
        sqlite3_stmt* stmt_rects;
        
        if (sqlite3_prepare_v2(engine->db, sql_rects, -1, &stmt_rects, nullptr) == SQLITE_OK) {
            sqlite3_bind_text(stmt_rects, 1, file_path, -1, SQLITE_TRANSIENT);
            
            bool first_rect = true;
            while (sqlite3_step(stmt_rects) == SQLITE_ROW) {
                if (!first_rect) json << ",";
                first_rect = false;
                
                double x1 = sqlite3_column_double(stmt_rects, 0);
                double y1 = sqlite3_column_double(stmt_rects, 1);
                double x2 = sqlite3_column_double(stmt_rects, 2);
                double y2 = sqlite3_column_double(stmt_rects, 3);
                const char* text = reinterpret_cast<const char*>(sqlite3_column_text(stmt_rects, 4));
                
                json << "{";
                json << "\"x1\":" << x1 << ",";
                json << "\"y1\":" << y1 << ",";
                json << "\"x2\":" << x2 << ",";
                json << "\"y2\":" << y2 << ",";
                json << "\"text\":" << escape_json_string(text);
                json << "}";
            }
            
            sqlite3_finalize(stmt_rects);
        }
        
        json << "]}";
    }
    
    sqlite3_finalize(stmt);
    json << "}";
    
    std::string result = json.str();
    char* output = new char[result.length() + 1];
    strcpy(output, result.c_str());
    return output;
}

int ocr_engine_save_session(void* engine_ptr, const char* files_json, int cur_index) {
    if (!engine_ptr) return -1;
    
    OCRCacheEngine* engine = static_cast<OCRCacheEngine*>(engine_ptr);
    
    if (cur_index < 0) {
        engine->set_error("save_session", "Invalid cur_index: " + std::to_string(cur_index));
        return -1;
    }
    
    std::string timestamp = get_timestamp();
    
    // 保存文件列表
    sqlite3_stmt* stmt;
    const char* sql = "INSERT OR REPLACE INTO session (key, value, updated_at) VALUES (?, ?, ?)";
    
    if (sqlite3_prepare_v2(engine->db, sql, -1, &stmt, nullptr) != SQLITE_OK) {
        std::string error_msg = "Failed to prepare session save statement: ";
        error_msg += sqlite3_errmsg(engine->db);
        engine->set_error("save_session", error_msg);
        return -1;
    }
    
    sqlite3_bind_text(stmt, 1, "files", -1, SQLITE_STATIC);
    sqlite3_bind_text(stmt, 2, files_json ? files_json : "[]", -1, SQLITE_TRANSIENT);
    sqlite3_bind_text(stmt, 3, timestamp.c_str(), -1, SQLITE_TRANSIENT);
    
    if (sqlite3_step(stmt) != SQLITE_DONE) {
        std::string error_msg = "Failed to save session files: ";
        error_msg += sqlite3_errmsg(engine->db);
        engine->set_error("save_session", error_msg);
        sqlite3_finalize(stmt);
        return -1;
    }
    sqlite3_finalize(stmt);
    
    // 保存当前索引
    std::string cur_index_str = std::to_string(cur_index);
    if (sqlite3_prepare_v2(engine->db, sql, -1, &stmt, nullptr) != SQLITE_OK) {
        std::string error_msg = "Failed to prepare session index save statement: ";
        error_msg += sqlite3_errmsg(engine->db);
        engine->set_error("save_session", error_msg);
        return -1;
    }
    
    sqlite3_bind_text(stmt, 1, "cur_index", -1, SQLITE_STATIC);
    sqlite3_bind_text(stmt, 2, cur_index_str.c_str(), -1, SQLITE_TRANSIENT);
    sqlite3_bind_text(stmt, 3, timestamp.c_str(), -1, SQLITE_TRANSIENT);
    
    if (sqlite3_step(stmt) != SQLITE_DONE) {
        std::string error_msg = "Failed to save session index: ";
        error_msg += sqlite3_errmsg(engine->db);
        engine->set_error("save_session", error_msg);
        sqlite3_finalize(stmt);
        return -1;
    }
    sqlite3_finalize(stmt);
    
    return 0;
}

char* ocr_engine_load_session(void* engine_ptr) {
    if (!engine_ptr) return nullptr;
    
    OCRCacheEngine* engine = static_cast<OCRCacheEngine*>(engine_ptr);
    std::ostringstream json;
    json << "{";
    
    const char* sql = "SELECT key, value FROM session WHERE key IN ('files', 'cur_index')";
    sqlite3_stmt* stmt;
    
    if (sqlite3_prepare_v2(engine->db, sql, -1, &stmt, nullptr) != SQLITE_OK) {
        std::string error_msg = "Failed to prepare load_session query: ";
        error_msg += sqlite3_errmsg(engine->db);
        engine->set_error("load_session", error_msg);
        return nullptr;
    }
    
    std::string files_value = "[]";
    std::string cur_index_value = "0";
    
    while (sqlite3_step(stmt) == SQLITE_ROW) {
        const char* key = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 0));
        const char* value = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 1));
        
        if (strcmp(key, "files") == 0) {
            files_value = value ? value : "[]";
        } else if (strcmp(key, "cur_index") == 0) {
            cur_index_value = value ? value : "0";
        }
    }
    
    sqlite3_finalize(stmt);
    
    json << "\"files\":" << files_value << ",";
    json << "\"cur_index\":" << cur_index_value;
    json << "}";
    
    std::string result = json.str();
    char* output = new char[result.length() + 1];
    strcpy(output, result.c_str());
    return output;
}

int ocr_engine_has_cache(void* engine_ptr) {
    if (!engine_ptr) return 0;
    
    OCRCacheEngine* engine = static_cast<OCRCacheEngine*>(engine_ptr);
    const char* sql = "SELECT COUNT(*) FROM files";
    sqlite3_stmt* stmt;
    
    if (sqlite3_prepare_v2(engine->db, sql, -1, &stmt, nullptr) != SQLITE_OK) {
        return 0;
    }
    
    int count = 0;
    if (sqlite3_step(stmt) == SQLITE_ROW) {
        count = sqlite3_column_int(stmt, 0);
    }
    
    sqlite3_finalize(stmt);
    return count > 0 ? 1 : 0;
}

void ocr_engine_clear(void* engine_ptr) {
    if (!engine_ptr) return;
    
    OCRCacheEngine* engine = static_cast<OCRCacheEngine*>(engine_ptr);
    sqlite3_exec(engine->db, "DELETE FROM ocr_rects", nullptr, nullptr, nullptr);
    sqlite3_exec(engine->db, "DELETE FROM files", nullptr, nullptr, nullptr);
    sqlite3_exec(engine->db, "DELETE FROM session", nullptr, nullptr, nullptr);
    sqlite3_exec(engine->db, "VACUUM", nullptr, nullptr, nullptr);
}

void ocr_engine_destroy(void* engine_ptr) {
    if (!engine_ptr) return;
    
    OCRCacheEngine* engine = static_cast<OCRCacheEngine*>(engine_ptr);
    if (engine->db) {
        sqlite3_close(engine->db);
    }
    delete engine;
}

void ocr_engine_free_string(char* str) {
    if (str) {
        delete[] str;
    }
}

const char* ocr_engine_get_error(void* engine_ptr) {
    if (!engine_ptr) return "Invalid engine";
    
    OCRCacheEngine* engine = static_cast<OCRCacheEngine*>(engine_ptr);
    return engine->last_error.c_str();
}

int ocr_engine_test(void* engine_ptr) {
    if (!engine_ptr) return 0;
    
    OCRCacheEngine* engine = static_cast<OCRCacheEngine*>(engine_ptr);
    
    // 测试1: 验证数据库连接
    if (!engine->db) {
        engine->set_error("health_check", "Database connection is NULL");
        return 0;
    }
    
    // 测试2: 执行简单查询
    const char* test_sql = "SELECT COUNT(*) FROM sqlite_master WHERE type='table'";
    sqlite3_stmt* stmt;
    
    if (sqlite3_prepare_v2(engine->db, test_sql, -1, &stmt, nullptr) != SQLITE_OK) {
        engine->set_error("health_check", "Failed to prepare test query: " + std::string(sqlite3_errmsg(engine->db)));
        return 0;
    }
    
    int result = 0;
    if (sqlite3_step(stmt) == SQLITE_ROW) {
        int table_count = sqlite3_column_int(stmt, 0);
        result = (table_count >= 3) ? 1 : 0;
        if (!result) {
            engine->set_error("health_check", "Schema incomplete: found " + std::to_string(table_count) + " tables, expected at least 3");
        }
    } else {
        engine->set_error("health_check", "Failed to execute test query");
        result = 0;
    }
    
    sqlite3_finalize(stmt);
    
    // 测试3: 验证数据库完整性
    if (result) {
        const char* integrity_sql = "PRAGMA integrity_check";
        if (sqlite3_prepare_v2(engine->db, integrity_sql, -1, &stmt, nullptr) == SQLITE_OK) {
            if (sqlite3_step(stmt) == SQLITE_ROW) {
                const char* integrity_result = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 0));
                if (integrity_result && strcmp(integrity_result, "ok") != 0) {
                    engine->set_error("health_check", "Database integrity check failed: " + std::string(integrity_result));
                    result = 0;
                }
            }
            sqlite3_finalize(stmt);
        }
    }
    
    return result;
}

const char* ocr_engine_version(void) {
    static std::string version_info;
    if (version_info.empty()) {
        version_info = "OCR Cache Engine v";
        version_info += OCR_CACHE_ENGINE_VERSION;
        version_info += " (SQLite ";
        version_info += sqlite3_libversion();
        version_info += ")";
    }
    return version_info.c_str();
}
