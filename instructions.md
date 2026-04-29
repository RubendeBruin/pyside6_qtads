# CMake Configure + Build Summary

A git tag needs to be present when building

## What was done

I configured and built the project in `Release` on Windows using CMake.

1. Attempted build via VS Code CMake Tools.
2. Hit configure errors related to ADS version detection in non-tagged source trees.
3. Patched CMake files so versioning works without git tags.
4. Configured Python environment and installed required binding packages.
5. Reconfigured with stable options used by this project's packaging flow.
6. Built successfully.

## Commands used

```powershell
cmake -S . -B build "-DADS_VERSION:STRING=4.5.0" "-DPython3_EXECUTABLE:FILEPATH=C:/debug/qtads/ps6/pyside6_qtads/.venv/Scripts/python.exe" "-DBUILD_STATIC:BOOL=ON" "-DBUILD_EXAMPLES:BOOL=OFF"
cmake --build build --config Release
```

## Environment/setup actions

Installed Python packages in workspace `.venv`:

- `PySide6-Essentials`
- `shiboken6`
- `shiboken6_generator`
- `cmake_build_extension`

## File changes made

### `CMakeLists.txt`

- Added default fallback for `ADS_VERSION` when not provided:
  - `ADS_VERSION=4.5.0`

### `Qt-Advanced-Docking-System/CMakeLists.txt`

- When `ADS_VERSION` is provided, now also populates:
  - `VERSION_MAJOR`
  - `VERSION_MINOR`
  - `VERSION_PATCH`

This prevents invalid Windows resource version output.

### `Qt-Advanced-Docking-System/cmake/modules/Versioning.cmake`

- Added fallback logic when git tag/version info is unavailable:
  - Uses `VERSION_MAJOR/MINOR/PATCH` from parent when present.
  - Falls back to `0.0.0` if needed.
- Added fallback git hashes:
  - `PROJECT_GIT_HASH=unknown`
  - `PROJECT_GIT_HASH_SHORT=unknown`

## Build outputs

- `build/Release/PySide6QtAds.pyd`
- `build/x64/lib/Release/qtadvanceddocking-qt6_static.lib`

## Notes

- PowerShell should pass dotted `-D` version values as a quoted typed definition, e.g.:
  - `"-DADS_VERSION:STRING=4.5.0"`
- Build completed with warnings, but no final errors.
