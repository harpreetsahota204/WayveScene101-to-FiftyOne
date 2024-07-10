#!/bin/bash

# List of Homebrew packages to install
PACKAGES=(
  ceres-solver
  hwloc
  pkg-config
  parallel
  flann
  qt@5
  mpfr
  hdf5
  libaec
  python@3.12
  glib
  metis
  glog
  tbb
  gcc
  cgal
  eigen
  ninja
  gflags
  openblas
  ca-certificates
  suite-sparse
  isl
  glew
  pcre2
  libomp
  imagemagick
  freeimage
  libmpc
)

# Update Homebrew and upgrade any already-installed packages
brew update
brew upgrade

# Install the packages
for PACKAGE in "${PACKAGES[@]}"; do
  brew install "$PACKAGE"
done

# Add Qt@5 to PATH in .zshrc
echo 'export PATH="/opt/homebrew/opt/qt@5/bin:$PATH"' >> ~/.zshrc

# Set environment variables for Qt@5
export LDFLAGS="-L/opt/homebrew/opt/qt@5/lib"
export CPPFLAGS="-I/opt/homebrew/opt/qt@5/include"
export PKG_CONFIG_PATH="/opt/homebrew/opt/qt@5/lib/pkgconfig"

# Append the Qt@5 environment variables to .zshrc
echo 'export LDFLAGS="-L/opt/homebrew/opt/qt@5/lib"' >> ~/.zshrc
echo 'export CPPFLAGS="-I/opt/homebrew/opt/qt@5/include"' >> ~/.zshrc
echo 'export PKG_CONFIG_PATH="/opt/homebrew/opt/qt@5/lib/pkgconfig"' >> ~/.zshrc

echo "All packages have been installed and environment variables set."