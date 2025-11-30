cmake_minimum_required(VERSION 3.10)
project(OCRCacheEngine)

# 设置C++标准
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# 设置构建类型为Release（如果未指定）
if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Release)
endif()

# 添加共享库（包含嵌入式SQLite源码）
add_library(ocr_cache SHARED
    ocr_cache_engine.cpp
    ocr_cache_engine.h
    sqlite3.c
)

# SQLite编译选项（精简版，移除不必要的功能）
target_compile_definitions(ocr_cache PRIVATE
    SQLITE_THREADSAFE=1
    SQLITE_OMIT_DEPRECATED
    SQLITE_OMIT_LOAD_EXTENSION
    SQLITE_OMIT_PROGRESS_CALLBACK
    SQLITE_OMIT_SHARED_CACHE
    SQLITE_DEFAULT_MEMSTATUS=0
    SQLITE_DEFAULT_WAL_SYNCHRONOUS=1
    SQLITE_LIKE_DOESNT_MATCH_BLOBS
    SQLITE_MAX_EXPR_DEPTH=0
    SQLITE_OMIT_DECLTYPE
    SQLITE_OMIT_AUTOINIT
    OCR_CACHE_EXPORTS  # 定义导出宏
)

# 链接系统库（SQLite需要的）
if(UNIX AND NOT APPLE)
    target_link_libraries(ocr_cache pthread dl m)
elseif(APPLE)
    target_link_libraries(ocr_cache pthread)
endif()

# 设置编译选项 - 最高优化级别
target_compile_options(ocr_cache PRIVATE
    -O3                    # 最高优化级别
    -Wall                  # 所有警告
    -Wextra                # 额外警告
    -fPIC                  # 位置无关代码
    -ffunction-sections    # 每个函数单独section
    -fdata-sections        # 每个数据单独section
    -fno-exceptions        # 禁用C++异常（减小体积）
    -fno-rtti              # 禁用运行时类型信息
    -fvisibility=hidden    # 隐藏符号（减小体积）
)

# 设置链接选项 - 移除调试符号和未使用代码
if(UNIX)
    target_link_options(ocr_cache PRIVATE
        -s                      # Strip符号表（移除调试符号）
        -Wl,--gc-sections       # 移除未使用的sections
        -Wl,--as-needed         # 只链接需要的库
    )
    
    # Windows特定的strip选项
    if(WIN32)
        target_link_options(ocr_cache PRIVATE
            -Wl,--strip-all     # 移除所有符号
        )
    endif()
endif()

# 设置输出目录
set_target_properties(ocr_cache PROPERTIES
    LIBRARY_OUTPUT_DIRECTORY "${CMAKE_SOURCE_DIR}/../"
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_SOURCE_DIR}/../"
)

# 安装规则（可选）
install(TARGETS ocr_cache
    LIBRARY DESTINATION lib
    RUNTIME DESTINATION bin
)
