
set(proj qRestAPI)

# Set dependency list
set(${proj}_DEPENDENCIES "")

# Include dependent projects if any
ExternalProject_Include_Dependencies(${proj} PROJECT_VAR proj DEPENDS_VAR ${proj}_DEPENDENCIES)

if(${CMAKE_PROJECT_NAME}_USE_SYSTEM_${proj})
  message(FATAL_ERROR "Enabling ${CMAKE_PROJECT_NAME}_USE_SYSTEM_${proj} is not supported !")
endif()

# Sanity checks
if(DEFINED qRestAPI_DIR AND NOT EXISTS ${qRestAPI_DIR})
  message(FATAL_ERROR "qRestAPI_DIR variable is defined but corresponds to non-existing directory")
endif()

if(NOT DEFINED qRestAPI_DIR)

  if(NOT DEFINED git_protocol)
    set(git_protocol "git")
  endif()

  ExternalProject_Add(${proj}
    ${${proj}_EP_ARGS}
    GIT_REPOSITORY "${git_protocol}://github.com/commontk/qRestAPI.git"
    GIT_TAG "5a81c92f91c379e1ea1198c858b6147a14f82fbe"
    SOURCE_DIR ${CMAKE_BINARY_DIR}/${proj}
    BINARY_DIR ${proj}-build
    CMAKE_CACHE_ARGS
      ${ep_common_cache_args}
      -DBUILD_SHARED_LIBS:BOOL=OFF
      -DQT_QMAKE_EXECUTABLE:FILEPATH=${QT_QMAKE_EXECUTABLE}
    INSTALL_COMMAND ""
    DEPENDS
      ${${proj}_DEPENDENCIES}
    )
  set(qRestAPI_DIR ${CMAKE_BINARY_DIR}/${proj}-build)

  # Libraries are built static; install is not required
  # ExternalProject_Install_CMake(${proj})

else()
  ExternalProject_Add_Empty(${proj} DEPENDS ${${proj}_DEPENDENCIES})
endif()

mark_as_superbuild(
  VARS qRestAPI_DIR:PATH
  LABELS "FIND_PACKAGE"
  )
