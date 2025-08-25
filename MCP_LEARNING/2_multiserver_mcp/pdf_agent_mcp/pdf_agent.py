import pdfplumber
from mcp.server.fastmcp import FastMCP
import os
import pickle
import tempfile
# from typing import Optional

# Create FastMCP instance
mcp = FastMCP("PDF Agent")

# Persistent cache file in temp directory
CACHE_FILE = os.path.join(tempfile.gettempdir(), "mcp_pdf_cache.pkl")

def load_cache():
    """Load PDF cache from persistent storage"""
    try:
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, 'rb') as f:
                return pickle.load(f)
    except Exception:
        pass
    return {}

def save_cache(cache):
    """Save PDF cache to persistent storage"""
    try:
        with open(CACHE_FILE, 'wb') as f:
            pickle.dump(cache, f)
    except Exception:
        pass

@mcp.tool()
def load_pdf(file_path: str) -> str:
    """Load and extract text from a PDF file.
    
    Args:
        file_path (str): Full path to the PDF file
        
    Returns:
        str: Success message with text preview or error message
    """
    try:
        # Normalize the path
        normalized_path = os.path.normpath(file_path)
        
        # Check if file exists
        if not os.path.exists(normalized_path):
            return f"❌ PDF file not found at: {normalized_path}"
        
        # Check if it's a PDF file
        if not normalized_path.lower().endswith('.pdf'):
            return f"❌ File is not a PDF: {normalized_path}"
        
        # Load existing cache
        pdf_cache = load_cache()
        
        # Check if already loaded
        if normalized_path in pdf_cache:
            content = pdf_cache[normalized_path]
            word_count = len(content.split())
            return f"✅ PDF already loaded!\n📄 File: {os.path.basename(normalized_path)}\n📝 Words: {word_count:,}\n💾 Status: Ready for questions"
        
        # Extract text from PDF
        with pdfplumber.open(normalized_path) as pdf:
            text = ""
            page_count = len(pdf.pages)
            
            for i, page in enumerate(pdf.pages, 1):
                page_text = page.extract_text()
                if page_text:
                    text += f"\n--- Page {i} ---\n{page_text}\n"
            
            if not text.strip():
                return f"❌ No text could be extracted from PDF: {normalized_path}"
            
            # Store in persistent cache
            pdf_cache[normalized_path] = text.strip()
            save_cache(pdf_cache)
            
            # Return success message with preview
            preview = text[:500] + "..." if len(text) > 500 else text
            word_count = len(text.split())
            return f"✅ PDF loaded successfully!\n📄 File: {os.path.basename(normalized_path)}\n📊 Pages: {page_count}\n📝 Words: {word_count:,}\n💾 Status: Cached and ready\n\n📝 Preview:\n{preview}"
            
    except Exception as e:
        return f"❌ Error loading PDF: {str(e)}"

@mcp.tool()
def ask_pdf_question(file_path: str, question: str) -> str:
    """Ask a question about a loaded PDF file.
    
    Args:
        file_path (str): Path to the PDF file (must be loaded first)
        question (str): Question about the PDF content
        
    Returns:
        str: Answer based on PDF content or error message
    """
    try:
        normalized_path = os.path.normpath(file_path)
        
        # Load cache
        pdf_cache = load_cache()
        
        # Check if PDF is loaded in cache
        if normalized_path not in pdf_cache:
            return f"❌ PDF not loaded. Please use load_pdf first for: {os.path.basename(normalized_path)}"
        
        content = pdf_cache[normalized_path]
        
        # Simple keyword-based search and context extraction
        question_lower = question.lower()
        question_words = [word for word in question_lower.split() if len(word) > 2]
        
        # Find relevant sections
        lines = content.split('\n')
        relevant_sections = []
        
        for i, line in enumerate(lines):
            line_lower = line.lower()
            # Check if line contains any question keywords
            if any(word in line_lower for word in question_words):
                # Include context (previous and next lines)
                start = max(0, i-2)
                end = min(len(lines), i+3)
                context = '\n'.join(lines[start:end]).strip()
                if context and context not in relevant_sections:
                    relevant_sections.append(context)
        
        if relevant_sections:
            answer = f"📖 Found {len(relevant_sections)} relevant section(s) for: '{question}'\n\n"
            
            for i, section in enumerate(relevant_sections[:3], 1):  # Limit to top 3 sections
                answer += f"🔍 Section {i}:\n{section}\n\n"
            
            return answer.strip()
        else:
            # Fallback: return first few lines if no specific match
            lines_clean = [line.strip() for line in lines if line.strip() and not line.startswith('---')]
            if lines_clean:
                return f"📖 No specific match found for '{question}', but here's the document content:\n\n" + '\n'.join(lines_clean[:10])
            else:
                return f"❌ No relevant information found in the PDF for question: '{question}'"
            
    except Exception as e:
        return f"❌ Error answering question: {str(e)}"

@mcp.tool()
def list_loaded_pdfs() -> str:
    """List all currently loaded PDF files.
    
    Returns:
        str: List of loaded PDF files
    """
    try:
        pdf_cache = load_cache()
        
        if not pdf_cache:
            return "📭 No PDF files currently loaded."
        
        result = f"📚 Currently loaded PDF files ({len(pdf_cache)}):\n\n"
        for i, (path, content) in enumerate(pdf_cache.items(), 1):
            filename = os.path.basename(path)
            word_count = len(content.split())
            char_count = len(content)
            result += f"{i}. 📄 {filename}\n   📊 {word_count:,} words, {char_count:,} characters\n   📁 {path}\n\n"
        
        return result.strip()
        
    except Exception as e:
        return f"❌ Error listing PDFs: {str(e)}"

@mcp.tool()
def clear_pdf_cache() -> str:
    """Clear all loaded PDF files from cache.
    
    Returns:
        str: Confirmation message
    """
    try:
        if os.path.exists(CACHE_FILE):
            os.remove(CACHE_FILE)
        return "🗑️ PDF cache cleared successfully!"
    except Exception as e:
        return f"❌ Error clearing cache: {str(e)}"

@mcp.tool()
def get_pdf_summary(file_path: str) -> str:
    """Get a summary of the PDF content.
    
    Args:
        file_path (str): Path to the PDF file
        
    Returns:
        str: Summary of PDF content
    """
    try:
        normalized_path = os.path.normpath(file_path)
        pdf_cache = load_cache()
        
        if normalized_path not in pdf_cache:
            return f"❌ PDF not loaded. Please use load_pdf first for: {os.path.basename(normalized_path)}"
        
        content = pdf_cache[normalized_path]
        lines = [line.strip() for line in content.split('\n') if line.strip() and not line.startswith('---')]
        
        # Get first few meaningful lines as summary
        summary_lines = []
        for line in lines[:20]:  # First 20 lines
            if len(line) > 20:  # Skip very short lines
                summary_lines.append(line)
            if len(summary_lines) >= 10:  # Max 10 lines in summary
                break
        
        word_count = len(content.split())
        char_count = len(content)
        
        result = f"📋 Summary of {os.path.basename(normalized_path)}:\n\n"
        result += f"📊 Statistics: {word_count:,} words, {char_count:,} characters\n\n"
        result += f"📝 Content Overview:\n"
        result += '\n'.join(f"• {line}" for line in summary_lines)
        
        return result
        
    except Exception as e:
        return f"❌ Error getting summary: {str(e)}"

# Run the server
if __name__ == "__main__":
    mcp.run(transport="stdio")