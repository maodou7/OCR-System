cmake_minimum_required(VERSION 3.10)
project(OCRCacheEngine)

# 设置C++标准
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# 添加共享库（包含嵌入式SQLite源码）
add_library(ocr_cache SHARED
    ocr_cache_engine.cpp
    ocr_cache_engine.h
    sqlite3.c
)

# SQLite编译选项
target_compile_definitions(ocr_cache PRIVATE
    SQLITE_THREADSAFE=1
    SQLITE_ENABLE_FTS5
    SQLITE_ENABLE_JSON1
    SQLITE_ENABLE_RTREE
)

# 链接系统库（SQLite需要的）
if(UNIX AND NOT APPLE)
    target_link_libraries(ocr_cache pthread dl m)
elseif(APPLE)
    target_link_libraries(ocr_cache pthread)
endif()

# 设置编译选项
target_compile_options(ocr_cache PRIVATE
    -O3
    -Wall
    -Wextra
    -fPIC
)

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
