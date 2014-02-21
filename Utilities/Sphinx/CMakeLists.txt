find_program(SPHINX_BUILD_EXECUTABLE sphinx-build)

if(SPHINX_BUILD_EXECUTABLE)
  # C++ bindings that must be compiled first
  set(pydeps
    FreeSurferPython
    MRMLCLIPython
    MRMLCorePython
    MRMLDisplayableManagerPython
    MRMLLogicPython
    SlicerBaseLogicPython
    vtkITKPython
    vtkTeemPython
    )

  # Set supplemental paths
  set(pypaths "${CMAKE_BINARY_DIR}/bin")

  # Set output directory
  set(pkg Slicer-${Slicer_VERSION_MAJOR}.${Slicer_VERSION_MINOR})
  set(docdir "${CMAKE_BINARY_DIR}/share/doc/${pkg}/Base")

  # Generate documentation
  add_custom_target(Python-doc
    DEPENDS ${pydeps}
    COMMAND "${CMAKE_COMMAND}" -E make_directory "${docdir}"
    COMMAND "${SPHINX_BUILD_EXECUTABLE}"
            "-Dpypath=${pypaths}"
            "-Dversion=${Slicer_VERSION_MAJOR}.${Slicer_VERSION_MINOR}"
            "${CMAKE_CURRENT_SOURCE_DIR}"
            "${docdir}"
    )
  set_target_properties(Python-doc PROPERTIES LABELS Documentation)
  add_dependencies(doc Python-doc)
else()
  message(WARNING "Warning: sphinx-build not found:"
                  " Python documentation will not be created")
endif()
