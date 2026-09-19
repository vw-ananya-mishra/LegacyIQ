#!/usr/bin/env bash
# LegacyIQ Project Setup Script

# Create project structure
echo "Setting up LegacyIQ project structure..."

mkdir -p LegacyIQ/{backend,frontend,docs}
cd LegacyIQ

# Backend structure
mkdir -p backend/{app,data,agents,utils}
mkdir -p backend/app/{api,services,models}

# Frontend structure
mkdir -p frontend/{public,src,dist}
mkdir -p frontend/src/{components,pages,hooks,utils,types,styles}
mkdir -p frontend/src/components/{agents,dashboard,common,graphs}

# Data directory
mkdir -p data/uploads
mkdir -p data/cache

echo "Project structure created!"
ls -R
