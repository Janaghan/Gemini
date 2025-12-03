# Gemini Examples

This directory contains various standalone examples demonstrating different capabilities of the Gemini API.

## Directories

-   **`document_understanding/`**:
    -   Examples of processing PDF documents.
    -   Includes handling large local PDFs and PDFs from URLs.

-   **`image_understanding/`**:
    -   Scripts for analyzing images, object detection, and segmentation.
    -   Demonstrates multimodal capabilities.

-   **`structured_output/`**:
    -   Examples of extracting structured data (JSON) from text.
    -   Demonstrates using Pydantic models for schema definition.

-   **`text_to_text/`**:
    -   Basic text generation examples.
    -   Simple prompts and responses.

-   **`function_calling/`**:
    -   Examples of how to define and use tools.
    -   Includes automatic and manual function calling patterns.

-   **`thinking/`**:
    -   Experiments with the "thinking" model (reasoning).
    -   Includes budget management and streaming examples.

## Running Examples

Navigate to the specific directory and run the scripts using `uv run` or `python`.

Example:
```bash
cd image_understanding
uv run object_detection.py
```
