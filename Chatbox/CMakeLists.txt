cmake_minimum_required(VERSION 3.13)
project(Chatbox)

set(CMAKE_CXX_STANDARD 14)

add_executable(Chatbox
        # bin/Debug/libmysql.dll
        main.cpp)

include_directories(/usr/include/mysql/)
link_directories(/usr/include/mysql/)
target_link_libraries(${PROJECT_NAME} mysqlclient -pthread)