cmake_minimum_required(VERSION 3.13)

project(console_charbox)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++17 -pthread")

add_executable(${PROJECT_NAME}_server
        server/server.cpp
        )

add_executable(${PROJECT_NAME}_client
        client/client.cpp
        )