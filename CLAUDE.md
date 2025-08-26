# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python project that converts images into artistic dice mosaics. The main functionality takes an input image, analyzes its brightness patterns, and generates both SVG and PNG outputs where each pixel region is represented by a dice face (1-6 dots) corresponding to the brightness level.

## Architecture

- **main.py**: Single-file application containing the core `image_to_dice()` function
- **Dependencies**: PIL (Pillow) for image processing, NumPy for numerical operations
- **Output**: Generates both SVG (scalable) and PNG (preview) versions of the dice mosaic

## Key Parameters

- `cell`: Controls dice size in pixels - smaller values create more detailed output with more dice
  - Default: 24 pixels
  - For more detail: use 12, 8, or 6
  - For less detail: use 32, 48, or higher

## Commands

Run the main script:
```bash
python main.py
```

Install dependencies:
```bash
uv sync
```

## Development Notes

- The script processes images by dividing them into blocks of size `cell x cell` pixels
- Each block's average brightness is quantized into 6 levels (1-6 dice faces)
- SVG output uses rounded rectangles with positioned circles for dice dots
- PNG preview is generated using PIL's drawing functions for compatibility