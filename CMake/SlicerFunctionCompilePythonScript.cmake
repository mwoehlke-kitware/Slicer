#-----------------------------------------------------------------------------
function(_slicer_resolve_relative OUTVAR PATH)
  get_filename_component(path ${PATH} REALPATH)
  foreach(rel ${ARGN})
    if(NOT rel MATCHES "/$")
      set(rel ${rel}/)
    endif()

    string(LENGTH ${rel} len)
    string(SUBSTRING ${path} 0 ${len} prefix)

    if(prefix STREQUAL rel)
      string(SUBSTRING ${path} ${len} -1 result)
      set(${OUTVAR} ${result} PARENT_SCOPE)
      return()
    endif()
  endforeach()

  get_filename_component(result ${path} NAME)
  set(${OUTVAR} ${result} PARENT_SCOPE)
endfunction()

#-----------------------------------------------------------------------------
function(_slicer_fcps_compiled_name OUTVAR NAME)
  if(NOT NAME MATCHES "\\.[Pp][Yy]$")
    message(FATAL_ERROR
      "SlicerFunctionCompilePythonScript:"
      " compiled script '${NAME}' must have a '.py' extension"
    )
  endif()
  set(${OUTVAR} ${NAME}c PARENT_SCOPE)
endfunction()

#-----------------------------------------------------------------------------
function(_slicer_install_path OUTVAR NAME DESTINATION)
  get_filename_component(rel ${NAME} PATH)
  if(rel)
    set(${OUTVAR} ${DESTINATION}/${rel} PARENT_SCOPE)
  else()
    set(${OUTVAR} ${DESTINATION} PARENT_SCOPE)
  endif()
endfunction()

#-----------------------------------------------------------------------------
function(slicerFunctionCompilePythonScript)
  # Extract arguments
  cmake_parse_arguments(ARG
    "EXECUTABLE;EXCLUDE_FROM_ALL"
    "TARGET;DESTINATION;INSTALL_DESTINATION;INSTALL_COMPONENT"
    "SCRIPTS;RESOURCES;RELATIVE"
    ${ARGN}
    )

  # Sanity check
  foreach(varname TARGET DESTINATION INSTALL_DESTINATION)
    if(NOT DEFINED ARG_${varname})
      message(FATAL_ERROR
        "SlicerFunctionCompilePythonScript:"
        " required option ${varname} was not specified"
      )
    endif()
  endforeach()

  # Set argument defaults and internal state from arguments
  set(reldirs)
  foreach(rel ${ARG_RELATIVE} ${CMAKE_CURRENT_SOURCE_DIR} ${CMAKE_CURRENT_BINARY_DIR})
    if(NOT IS_ABSOLUTE ${rel})
      set(rel ${CMAKE_CURRENT_SOURCE_DIR}/${rel})
    endif()
    get_filename_component(rel ${rel} REALPATH)
    list(APPEND reldirs ${rel})
  endforeach()

  if(ARG_EXECUTABLE)
    set(install_type PROGRAMS)
  else()
    set(install_type FILES)
  endif()

  if(NOT DEFINED ARG_INSTALL_COMPONENT)
    set(ARG_INSTALL_COMPONENT RuntimeLibraries)
  endif()

  set(all ALL)
  if(ARG_EXCLUDE_FROM_ALL)
    set(all)
  endif()

  # Generate rules to copy scripts and resources
  set(deps)
  foreach(resource ${ARG_RESOURCES})
    # Get output relative and absolute file paths
    _slicer_resolve_relative(out_name ${resource} ${reldirs})
    set(out_path ${ARG_DESTINATION}/${out_name})

    # Add rule to copy resource file
    add_custom_command(VERBATIM
      OUTPUT ${out_path}
      DEPENDS ${resource}
      COMMAND ${CMAKE_COMMAND} -E copy ${resource} ${out_path}
      WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
      )

    # Get install destination and add install rule for resource file
    _slicer_install_path(install_dir ${out_name} ${ARG_INSTALL_DESTINATION})
    install(FILES ${resource}
      DESTINATION ${install_dir}
      COMPONENT ${ARG_INSTALL_COMPONENT}
      )

    # Add output file to target dependencies list
    list(APPEND deps ${out_path})
  endforeach()

  foreach(script ${ARG_SCRIPTS})
    # Get output relative and absolute file paths (also for compiled script)
    _slicer_resolve_relative(out_name ${script} ${reldirs})
    _slicer_fcps_compiled_name(out_name_compiled ${out_name})
    set(out_path ${ARG_DESTINATION}/${out_name})
    set(out_path_compiled ${ARG_DESTINATION}/${out_name_compiled})

    # Add rule to copy script file
    add_custom_command(VERBATIM
      OUTPUT ${out_path}
      DEPENDS ${script}
      COMMAND ${CMAKE_COMMAND} -E copy ${script} ${out_path}
      WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
      )

    # Add rule to compile script file
    add_custom_command(VERBATIM
      OUTPUT ${out_path_compiled}
      DEPENDS ${out_path}
      COMMAND ${PYTHON_EXECUTABLE}
        -c "import py_compile; py_compile.main()"
        ${out_path}
      WORKING_DIRECTORY ${ARG_DESTINATION}
      )

    # Get install destination and add install rule for script files
    _slicer_install_path(install_dir ${out_name} ${ARG_INSTALL_DESTINATION})
    install(${install_type} ${script}
      DESTINATION ${install_dir}
      COMPONENT ${ARG_INSTALL_COMPONENT}
      )

    # Add output files to target dependencies list
    list(APPEND deps ${out_path} ${out_path_compiled})
  endforeach()

  # Create target
  add_custom_target(${ARG_TARGET} ${all} DEPENDS ${deps})
endfunction()
