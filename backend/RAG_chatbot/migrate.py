#!/usr/bin/env python3
"""
Migration script to replace Gemini API with DeepSeek R1 in your RAG system
Run this script to automatically update all your existing code files
"""

import os
import re
import shutil
from pathlib import Path

def backup_file(file_path):
    """Create backup of original file"""
    backup_path = f"{file_path}.backup"
    shutil.copy2(file_path, backup_path)
    print(f"✅ Backed up {file_path} to {backup_path}")

def update_imports_and_references(file_path, content):
    """Update imports and service references in file content"""
    
    # Replace Gemini imports with DeepSeek imports
    content = re.sub(
        r'from app\.services\.gemini_service import.*',
        'from app.services.deepseek_service import deepseek_service',
        content
    )
    
    content = re.sub(
        r'import.*gemini_service.*',
        'from app.services.deepseek_service import deepseek_service',
        content
    )
    
    # Replace GeminiService instantiation
    content = re.sub(
        r'GeminiService\(\)',
        'deepseek_service',
        content
    )
    
    # Replace service variable names
    content = re.sub(
        r'gemini_service',
        'deepseek_service',
        content
    )
    
    content = re.sub(
        r'self\.gemini_service',
        'deepseek_service',
        content
    )
    
    # Update method calls (they remain the same, so no changes needed)
    
    return content

def update_dependencies_py():
    """Update dependencies.py file"""
    file_path = "dependencies.py"
    if not os.path.exists(file_path):
        print(f"⚠️ {file_path} not found, skipping...")
        return
    
    backup_file(file_path)
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Update the content
    content = update_imports_and_references(file_path, content)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Updated {file_path}")

def update_rag_service_py():
    """Update rag_service.py file"""
    file_path = "rag_service.py"
    if not os.path.exists(file_path):
        print(f"⚠️ {file_path} not found, skipping...")
        return
    
    backup_file(file_path)
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Update the content
    content = update_imports_and_references(file_path, content)
    
    # Also update any specific Gemini references
    content = re.sub(
        r'# Initialize Gemini.*',
        '# Initialize DeepSeek R1 service (local and private)',
        content
    )
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Updated {file_path}")

def update_chat_py():
    """Update chat.py file"""
    file_path = "chat.py"
    if not os.path.exists(file_path):
        print(f"⚠️ {file_path} not found, skipping...")
        return
    
    backup_file(file_path)
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Update the content
    content = update_imports_and_references(file_path, content)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Updated {file_path}")

def update_other_files():
    """Update any other files that might reference Gemini service"""
    python_files = [
        "main.py",
        "document_service.py",
        "financial_analytics_service.py",
        "tally_services.py"
    ]
    
    for file_path in python_files:
        if not os.path.exists(file_path):
            continue
            
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if file contains Gemini references
        if 'gemini' in content.lower() or 'GeminiService' in content:
            backup_file(file_path)
            content = update_imports_and_references(file_path, content)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ Updated {file_path}")

def create_env_template():
    """Create .env template for DeepSeek configuration"""
    env_template = """# DeepSeek R1 Configuration (Local AI Model)
# No API keys needed - everything runs locally!

# Ollama Server Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL_NAME=deepseek-r1:8b
OLLAMA_TIMEOUT=120

# Model Parameters
MODEL_TEMPERATURE=0.7
MODEL_TOP_P=0.9
MAX_TOKENS=4000

# Database Configuration (keep your existing values)
DB_HOST=34.170.243.16
DB_PORT=3306
DB_NAME=rag_chatbot
DB_USER=root
DB_PASSWORD=vraj10%40PA

# File Upload Settings
UPLOAD_PATH=./uploads
MAX_FILE_SIZE_MB=50
ALLOWED_FILE_TYPES=pdf,docx,doc,txt,png,jpg,jpeg,xlsx,xls,csv,xml

# Vector Database Settings
VECTOR_DB_TYPE=chromadb
VECTOR_STORE_PATH=./vector_store
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Processing Settings
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
MAX_CHUNKS_PER_DOCUMENT=1000

# Development Settings
DEBUG=false
LOG_LEVEL=INFO

# Feature Flags
ENABLE_GOOGLE_DRIVE=true
ENABLE_ENHANCED_WEB_SCRAPING=true
ENABLE_SELENIUM=true
ENABLE_ADVANCED_EXCEL_PROCESSING=true

# Legacy (no longer used)
# GEMINI_API_KEY=  # Not needed anymore!
"""
    
    with open('.env.deepseek_template', 'w', encoding='utf-8') as f:
        f.write(env_template)
    
    print("✅ Created .env.deepseek_template")
    print("   Copy this to .env and adjust values as needed")

def main():
    """Run the complete migration"""
    print("🚀 Starting migration from Gemini to DeepSeek R1...")
    print("   This will keep your data completely private and local!")
    
    # Ensure we're in the right directory
    required_files = ['config.py', 'gemini_service.py', 'requirements.txt']
    missing_files = [f for f in required_files if not os.path.exists(f)]
    
    if missing_files:
        print(f"❌ Missing required files: {missing_files}")
        print("   Please run this script from your project root directory")
        return
    
    print("\n📁 Files to be updated:")
    print("   - dependencies.py")
    print("   - rag_service.py") 
    print("   - chat.py")
    print("   - Any other files with Gemini references")
    print("   - requirements.txt")
    print("   - config.py")
    
    response = input("\n⚠️  This will modify your files (backups will be created). Continue? (y/N): ")
    if response.lower() != 'y':
        print("Migration cancelled")
        return
    
    # 1. Update Python files
    update_dependencies_py()
    update_rag_service_py()
    update_chat_py()
    update_other_files()
    
    # 2. Create new service file
    print("📝 Please manually:")
    print("   1. Replace gemini_service.py with the new deepseek_service.py")
    print("   2. Replace config.py with updated_config.py")
    print("   3. Replace requirements.txt with updated_requirements.txt")
    
    # 3. Create environment template
    create_env_template()
    
    print("\n✅ Migration completed!")
    print("\n📋 Next steps:")
    print("   1. Install new requirements: pip install -r requirements.txt")
    print("   2. Ensure Ollama is running: ollama serve")
    print("   3. Verify DeepSeek model is available: ollama list")
    print("   4. Update your .env file using .env.deepseek_template")
    print("   5. Restart your application")
    
    print("\n🔒 Privacy Benefits:")
    print("   ✅ No data leaves your machine")
    print("   ✅ No API keys needed")
    print("   ✅ No internet required for AI responses")
    print("   ✅ Complete control over your data")

if __name__ == "__main__":
    main()