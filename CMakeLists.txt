cmake_minimum_required (VERSION 3.9)

project (rescal-snow
  DESCRIPTION "Simulating snow self-organization with cellular automata"
  LANGUAGES C
)

set(CMAKE_MODULE_PATH "${CMAKE_SOURCE_DIR}/cmake" ${CMAKE_MODULE_PATH})
find_package(Sanitizers)

find_package(ZLIB 1.2 REQUIRED)
find_package(PNG 1.6 REQUIRED)

set(COMMON_SOURCES
  src/cells.c
  src/lgca.c
  src/doublets.c
  src/format.c
  src/models.c
  src/param.c
  src/simul.c
  src/surface.c
  src/space.c
  src/trace.c
  src/transitions.c
  src/view.c
)

add_executable(rescal
  ${COMMON_SOURCES}
  src/callbacks.c
  src/drand48.c
  src/entry.c
  src/rescal.c
)

add_executable(genesis
  src/format.c
  src/param.c
  src/genesis.c
)

add_executable(regenesis
  src/format.c
  src/regenesis.c
)

add_executable(bin2png
  ${COMMON_SOURCES}
  src/bin2png.c
)

add_executable(csp2png
  ${COMMON_SOURCES}
  src/csp2png.c
)

add_executable(cspinfo
  src/format.c
  src/cspinfo.c
)

add_executable(csp2bin
  src/format.c
  src/csp2bin.c
)

function(setup_target target)
  set_property(TARGET ${target} PROPERTY C_STANDARD 99)
  target_include_directories(${target} PRIVATE src)
  if(MSVC)
    target_compile_options(${target} PRIVATE /W4 /WX)
  else()
    target_compile_options(${target} PRIVATE -Wall -Wextra -pedantic -Werror)
  endif()
  add_sanitizers(${target})
endfunction(setup_target)

target_link_libraries(rescal    PRIVATE png pthread m)
target_link_libraries(genesis   PRIVATE png m)  
target_link_libraries(regenesis PRIVATE m)  
target_link_libraries(bin2png   PRIVATE png m)  
target_link_libraries(csp2png   PRIVATE png m)  

setup_target(rescal)
setup_target(genesis)
setup_target(regenesis)
setup_target(bin2png)
setup_target(csp2png)
setup_target(cspinfo)
setup_target(csp2bin)
