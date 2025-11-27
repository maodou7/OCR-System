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

// 引擎内部结构
struct OCRCacheEngine {
    sqlite3* db;
    std::string last_error;
    
    OCRCacheEngine() : db(nullptr) {}
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
    strftime(buf, sizeof(buf), "%Y-%m-%d %H:%M:%S", localtime(&now));
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
    if (!db_path) return nullptr;
    
    OCRCacheEngine* engine = new OCRCacheEngine();
    
    // 打开数据库
    int rc = sqlite3_open(db_path, &engine->db);
    if (rc != SQLITE_OK) {
        engine->last_error = sqlite3_errmsg(engine->db);
        sqlite3_close(engine->db);
        delete engine;
        return nullptr;
    }
    
    // 启用外键约束
    sqlite3_exec(engine->db, "PRAGMA foreign_keys = ON", nullptr, nullptr, nullptr);
    
    // 性能优化设置
    sqlite3_exec(engine->db, "PRAGMA journal_mode = WAL", nullptr, nullptr, nullptr);
    sqlite3_exec(engine->db, "PRAGMA synchronous = NORMAL", nullptr, nullptr, nullptr);
    sqlite3_exec(engine->db, "PRAGMA cache_size = 10000", nullptr, nullptr, nullptr);
    
    // 初始化表结构
    if (!init_database_schema(engine->db, engine->last_error)) {
        sqlite3_close(engine->db);
        delete engine;
        return nullptr;
    }
    
    return engine;
}

int ocr_engine_save_result(void* engine_ptr,
                           const char* file_path,
                           const char* status,
                           int rect_count,
                           const double* rect_coords,
                           const char** rect_texts) {
    if (!engine_ptr || !file_path) return -1;
    
    OCRCacheEngine* engine = static_cast<OCRCacheEngine*>(engine_ptr);
    char* err_msg = nullptr;
    
    // 开始事务
    if (sqlite3_exec(engine->db, "BEGIN TRANSACTION", nullptr, nullptr, &err_msg) != SQLITE_OK) {
        engine->last_error = err_msg ? err_msg : "Failed to begin transaction";
        if (err_msg) sqlite3_free(err_msg);
        return -1;
    }
    
    // 插入或更新文件记录
    std::string timestamp = get_timestamp();
    sqlite3_stmt* stmt;
    const char* sql_file = "INSERT OR REPLACE INTO files (file_path, status, updated_at) VALUES (?, ?, ?)";
    
    if (sqlite3_prepare_v2(engine->db, sql_file, -1, &stmt, nullptr) != SQLITE_OK) {
        engine->last_error = sqlite3_errmsg(engine->db);
        sqlite3_exec(engine->db, "ROLLBACK", nullptr, nullptr, nullptr);
        return -1;
    }
    
    sqlite3_bind_text(stmt, 1, file_path, -1, SQLITE_TRANSIENT);
    sqlite3_bind_text(stmt, 2, status ? status : "", -1, SQLITE_TRANSIENT);
    sqlite3_bind_text(stmt, 3, timestamp.c_str(), -1, SQLITE_TRANSIENT);
    
    if (sqlite3_step(stmt) != SQLITE_DONE) {
        engine->last_error = sqlite3_errmsg(engine->db);
        sqlite3_finalize(stmt);
        sqlite3_exec(engine->db, "ROLLBACK", nullptr, nullptr, nullptr);
        return -1;
    }
    sqlite3_finalize(stmt);
    
    // 删除该文件的旧区域数据
    const char* sql_delete = "DELETE FROM ocr_rects WHERE file_path = ?";
    if (sqlite3_prepare_v2(engine->db, sql_delete, -1, &stmt, nullptr) != SQLITE_OK) {
        engine->last_error = sqlite3_errmsg(engine->db);
        sqlite3_exec(engine->db, "ROLLBACK", nullptr, nullptr, nullptr);
        return -1;
    }
    
    sqlite3_bind_text(stmt, 1, file_path, -1, SQLITE_TRANSIENT);
    sqlite3_step(stmt);
    sqlite3_finalize(stmt);
    
    // 插入新的区域数据
    if (rect_count > 0 && rect_coords && rect_texts) {
        const char* sql_rect = "INSERT INTO ocr_rects (file_path, rect_index, x1, y1, x2, y2, text) "
                              "VALUES (?, ?, ?, ?, ?, ?, ?)";
        
        if (sqlite3_prepare_v2(engine->db, sql_rect, -1, &stmt, nullptr) != SQLITE_OK) {
            engine->last_error = sqlite3_errmsg(engine->db);
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
                engine->last_error = sqlite3_errmsg(engine->db);
                sqlite3_finalize(stmt);
                sqlite3_exec(engine->db, "ROLLBACK", nullptr, nullptr, nullptr);
                return -1;
            }
        }
        
        sqlite3_finalize(stmt);
    }
    
    // 提交事务
    if (sqlite3_exec(engine->db, "COMMIT", nullptr, nullptr, &err_msg) != SQLITE_OK) {
        engine->last_error = err_msg ? err_msg : "Failed to commit";
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
        engine->last_error = sqlite3_errmsg(engine->db);
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
    std::string timestamp = get_timestamp();
    
    // 保存文件列表
    sqlite3_stmt* stmt;
    const char* sql = "INSERT OR REPLACE INTO session (key, value, updated_at) VALUES (?, ?, ?)";
    
    if (sqlite3_prepare_v2(engine->db, sql, -1, &stmt, nullptr) != SQLITE_OK) {
        engine->last_error = sqlite3_errmsg(engine->db);
        return -1;
    }
    
    sqlite3_bind_text(stmt, 1, "files", -1, SQLITE_STATIC);
    sqlite3_bind_text(stmt, 2, files_json ? files_json : "[]", -1, SQLITE_TRANSIENT);
    sqlite3_bind_text(stmt, 3, timestamp.c_str(), -1, SQLITE_TRANSIENT);
    
    if (sqlite3_step(stmt) != SQLITE_DONE) {
        engine->last_error = sqlite3_errmsg(engine->db);
        sqlite3_finalize(stmt);
        return -1;
    }
    sqlite3_finalize(stmt);
    
    // 保存当前索引
    std::string cur_index_str = std::to_string(cur_index);
    if (sqlite3_prepare_v2(engine->db, sql, -1, &stmt, nullptr) != SQLITE_OK) {
        engine->last_error = sqlite3_errmsg(engine->db);
        return -1;
    }
    
    sqlite3_bind_text(stmt, 1, "cur_index", -1, SQLITE_STATIC);
    sqlite3_bind_text(stmt, 2, cur_index_str.c_str(), -1, SQLITE_TRANSIENT);
    sqlite3_bind_text(stmt, 3, timestamp.c_str(), -1, SQLITE_TRANSIENT);
    
    if (sqlite3_step(stmt) != SQLITE_DONE) {
        engine->last_error = sqlite3_errmsg(engine->db);
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
        engine->last_error = sqlite3_errmsg(engine->db);
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
