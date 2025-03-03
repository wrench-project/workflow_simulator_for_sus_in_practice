cmake_minimum_required(VERSION 3.12)
message(STATUS "Cmake version ${CMAKE_MAJOR_VERSION}.${CMAKE_MINOR_VERSION}.${CMAKE_PATCH_VERSION}")

project(workflow-simulator CXX)

# Disable annoying warnings
add_definitions("-DBOOST_ALLOW_DEPRECATED_HEADERS")

add_definitions("-Wall -Wno-unused-variable -Wno-unused-private-field")

# Make Release the default build type
if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Release)
endif()

set(CMAKE_CXX_STANDARD 17)

set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} "${CMAKE_SOURCE_DIR}/CMakeModules/")

find_package(WRENCH REQUIRED)
find_package(SimGrid REQUIRED)
find_package(FSMod REQUIRED)
if(POLICY CMP0167)
    cmake_policy(SET CMP0167 NEW)
endif()
find_package(Boost REQUIRED)
find_package(Boost COMPONENTS program_options REQUIRED)

# include directories for dependencies and WRENCH libraries
include_directories(src/ ${SimGrid_INCLUDE_DIR}/include /usr/local/include /opt/local/include ${WRENCH_INCLUDE_DIR} ${FSMOD_INCLUDE_DIR} ${SimGrid_INCLUDE_DIR} ${Boost_INCLUDE_DIR})

# source files
set(SOURCE_FILES
        src/SimpleWMS.h
        src/SimpleWMS.cpp
        src/SimpleStandardJobScheduler.h
        src/SimpleStandardJobScheduler.cpp
        src/scheduling_algorithms/TaskSelectionSchemes.cpp
        src/scheduling_algorithms/WorkerSelectionSchemes.cpp
        src/scheduling_algorithms/CoreSelectionSchemes.cpp
        src/main.cpp
        src/PlatformCreator.cpp
        src/PlatformCreator.h
        src/WorkflowCreator.cpp
        src/WorkflowCreator.h
        )

# test files
set(TEST_FILES
        )

# generating the executable
add_executable(workflow_simulator ${SOURCE_FILES})

if (ENABLE_BATSCHED)
    target_link_libraries(workflow_simulator
            ${WRENCH_LIBRARY}
            ${WRENCH_WFCOMMONS_WORKFLOW_PARSER_LIBRARY}
            ${SimGrid_LIBRARY}
            ${Boost_LIBRARIES}
            ${FSMOD_LIBRARY}
            -lzmq )
else()
    target_link_libraries(workflow_simulator
            ${WRENCH_LIBRARY}
            ${WRENCH_WFCOMMONS_WORKFLOW_PARSER_LIBRARY}
            ${SimGrid_LIBRARY}
            ${Boost_LIBRARIES}
            ${FSMOD_LIBRARY}
            )
endif()

install(TARGETS workflow_simulator DESTINATION bin)
