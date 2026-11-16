import os
import re
from typing import List, Dict, Any


def chunk_markdown_file(file_path: str, chunk_size: int = 500, chunk_overlap: int = 80) -> List[Dict[str, Any]]:
    """
    Chunks a markdown document preserving header context.
    """
    if not os.path.exists(file_path):
        return []

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    filename = os.path.basename(file_path)
    
    # Split by markdown headers
    sections = re.split(r'\n(?=#{1,3}\s)', content)
    chunks: List[Dict[str, Any]] = []
    
    for section_idx, section in enumerate(sections):
        section = section.strip()
        if not section:
            continue

        # Extract section title if present
        header_match = re.match(r'^(#{1,3})\s+(.*)', section)
        header_title = header_match.group(2) if header_match else "General"

        # If section is small enough, keep as single chunk
        if len(section) <= chunk_size:
            chunks.append({
                "text": section,
                "metadata": {
                    "source": filename,
                    "section": header_title,
                    "chunk_id": f"{filename}_{section_idx}_0"
                }
            })
        else:
            # Sub-chunk by paragraphs or sentences
            paragraphs = section.split("\n\n")
            current_chunk = ""
            sub_idx = 0
            
            for p in paragraphs:
                p = p.strip()
                if not p:
                    continue
                if len(current_chunk) + len(p) + 2 > chunk_size and current_chunk:
                    chunks.append({
                        "text": f"[{header_title}]\n{current_chunk}",
                        "metadata": {
                            "source": filename,
                            "section": header_title,
                            "chunk_id": f"{filename}_{section_idx}_{sub_idx}"
                        }
                    })
                    sub_idx += 1
                    # Keep overlap
                    current_chunk = p
                else:
                    current_chunk = f"{current_chunk}\n\n{p}" if current_chunk else p

            if current_chunk:
                chunks.append({
                    "text": f"[{header_title}]\n{current_chunk}",
                    "metadata": {
                        "source": filename,
                        "section": header_title,
                        "chunk_id": f"{filename}_{section_idx}_{sub_idx}"
                    }
                })

    return chunks


def load_all_knowledge_chunks(kb_directory: str) -> List[Dict[str, Any]]:
    """Loads and chunks all markdown files from the knowledge base directory."""
    all_chunks: List[Dict[str, Any]] = []
    if not os.path.exists(kb_directory):
        return all_chunks

    for root, _, files in os.walk(kb_directory):
        for file in files:
            if file.endswith((".md", ".txt")):
                full_path = os.path.join(root, file)
                chunks = chunk_markdown_file(full_path)
                all_chunks.extend(chunks)

    return all_chunks
