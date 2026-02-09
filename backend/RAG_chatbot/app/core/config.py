# Configuration Updates for Enhanced RAG Backend with DeepSeek R1 + Tally XML Integration

import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import List


class Settings(BaseSettings):
    # Fix Pydantic namespace warning
    model_config = SettingsConfigDict(
        protected_namespaces=('settings_',),
        env_file=".env",
        case_sensitive=False,
        extra="ignore"
    )
    
    # ================================================================
    # DATABASE SETTINGS
    # ================================================================
    dbhost: str = Field("localhost", env="DB_HOST")
    dbport: int = Field(3306, env="DB_PORT")
    dbname: str = Field("rag_chatbot", env="DB_NAME")
    dbuser: str = Field("root", env="DB_USER")
    dbpassword: str = Field("password", env="DB_PASSWORD")

    @property
    def database_url(self):
        return f"mysql+pymysql://{self.dbuser}:{self.dbpassword}@{self.dbhost}:{self.dbport}/{self.dbname}"

    # ================================================================
    # JWT AND SECURITY
    # ================================================================
    secret_key: str = "your-super-secure-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # ================================================================
    # DEEPSEEK R1 OLLAMA SETTINGS
    # ================================================================
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    ollama_model_name: str = os.getenv("OLLAMA_MODEL_NAME", "phi4:14b")
    ollama_timeout: int = int(os.getenv("OLLAMA_TIMEOUT", "120"))
    
    # Model configuration
    model_temperature: float = float(os.getenv("MODEL_TEMPERATURE", "0.7"))
    model_top_p: float = float(os.getenv("MODEL_TOP_P", "0.9"))
    max_tokens: int = int(os.getenv("MAX_TOKENS", "4000"))

    # ================================================================
    # NEW: TALLY XML OVER HTTP INTEGRATION SETTINGS
    # ================================================================
    # Tally connection method: 'xml' (recommended), 'odbc' (legacy), or 'disabled'
    tally_method: str = os.getenv("TALLY_METHOD", "xml")
    
    # Tally XML HTTP settings (Universal, Platform-Independent)
    tally_host: str = os.getenv("TALLY_HOST", "localhost")
    tally_port: int = int(os.getenv("TALLY_PORT", "9000"))
    tally_timeout: int = int(os.getenv("TALLY_TIMEOUT", "30"))
    tally_company_name: str = os.getenv("TALLY_COMPANY_NAME", "")
    
    @property
    def tally_base_url(self) -> str:
        """Get Tally XML API base URL"""
        return f"http://{self.tally_host}:{self.tally_port}"
    
    # Legacy ODBC settings (deprecated - kept for backward compatibility)
    tally_odbc_dsn: str = os.getenv("TALLY_ODBC_DSN", "TallyODBC64_9000")
    tally_odbc_timeout: int = int(os.getenv("TALLY_ODBC_TIMEOUT", "10"))
    
    # API2Books settings (alternative file-based integration)
    api2books_data_path: str = os.getenv("API2BOOKS_DATA_PATH", "C:/TallyData/")
    api2books_sync_interval: int = int(os.getenv("API2BOOKS_SYNC_INTERVAL", "30"))
    api2books_ftp_server: str = os.getenv("API2BOOKS_FTP_SERVER", "")
    api2books_ftp_username: str = os.getenv("API2BOOKS_FTP_USERNAME", "")
    api2books_ftp_password: str = os.getenv("API2BOOKS_FTP_PASSWORD", "")
    
    # Tally feature flags
    enable_tally_live_data: bool = bool(os.getenv("ENABLE_TALLY_LIVE_DATA", "true").lower() == "true")
    enable_tally_file_processing: bool = bool(os.getenv("ENABLE_TALLY_FILE_PROCESSING", "true").lower() == "true")
    enable_tally_xml: bool = bool(os.getenv("ENABLE_TALLY_XML", "true").lower() == "true")
    
    # Tally data caching
    tally_cache_enabled: bool = bool(os.getenv("TALLY_CACHE_ENABLED", "true").lower() == "true")
    tally_cache_ttl: int = int(os.getenv("TALLY_CACHE_TTL", "300"))  # 5 minutes
    
    @property
    def tally_config(self) -> dict:
        """Get Tally configuration dictionary"""
        return {
            'method': self.tally_method,
            'xml': {
                'host': self.tally_host,
                'port': self.tally_port,
                'base_url': self.tally_base_url,
                'timeout': self.tally_timeout,
                'enabled': self.enable_tally_xml
            },
            'odbc_dsn': self.tally_odbc_dsn,
            'odbc_timeout': self.tally_odbc_timeout,
            'company_name': self.tally_company_name,
            'api2books': {
                'data_path': self.api2books_data_path,
                'sync_interval': self.api2books_sync_interval,
                'ftp_server': self.api2books_ftp_server,
                'ftp_username': self.api2books_ftp_username,
                'ftp_password': self.api2books_ftp_password
            },
            'cache': {
                'enabled': self.tally_cache_enabled,
                'ttl': self.tally_cache_ttl
            },
            'features': {
                'live_data': self.enable_tally_live_data,
                'file_processing': self.enable_tally_file_processing,
                'xml_enabled': self.enable_tally_xml
            }
        }

    # ================================================================
    # GOOGLE DRIVE API SETTINGS
    # ================================================================
    google_drive_credentials_path: str = os.getenv("GOOGLE_DRIVE_CREDENTIALS_PATH", "")
    google_drive_api_enabled: bool = bool(os.getenv("GOOGLE_DRIVE_API_ENABLED", "false").lower() == "true")

    # ================================================================
    # FILE UPLOAD SETTINGS - ENHANCED
    # ================================================================
    upload_path: str = os.getenv("UPLOAD_PATH", "./uploads")
    max_file_size_mb: int = int(os.getenv("MAX_FILE_SIZE_MB", "50"))

    @property
    def max_file_size_bytes(self):
        return self.max_file_size_mb * 1024 * 1024

    # Enhanced file types support (includes Tally formats)
    allowed_file_types: str = os.getenv(
        "ALLOWED_FILE_TYPES",
        "pdf,docx,doc,txt,png,jpg,jpeg,xlsx,xls,csv,xml"
    )

    @property
    def allowed_file_types_list(self):
        return [ft.strip().lower() for ft in self.allowed_file_types.split(",")]

    # ================================================================
    # VECTOR DATABASE SETTINGS
    # ================================================================
    vector_db_type: str = os.getenv("VECTOR_DB_TYPE", "chromadb")
    vector_store_path: str = os.getenv("VECTOR_STORE_PATH", "./vector_store")
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

    # ================================================================
    # OCR AND DOCUMENT PROCESSING
    # ================================================================
    poppler_path: str = os.getenv("POPPLER_PATH", "/usr/bin")
    tesseract_path: str = os.getenv("TESSERACT_PATH", "/usr/bin/tesseract")

    # ================================================================
    # WEB SCRAPING SETTINGS
    # ================================================================
    web_scraping_timeout: int = int(os.getenv("WEB_SCRAPING_TIMEOUT", "30"))
    selenium_headless: bool = bool(os.getenv("SELENIUM_HEADLESS", "true").lower() == "true")
    selenium_wait_time: int = int(os.getenv("SELENIUM_WAIT_TIME", "10"))

    user_agent: str = os.getenv(
        "USER_AGENT",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    )

    # ================================================================
    # PROCESSING SETTINGS
    # ================================================================
    chunk_size: int = int(os.getenv("CHUNK_SIZE", "1000"))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "200"))
    max_chunks_per_document: int = int(os.getenv("MAX_CHUNKS_PER_DOCUMENT", "1000"))

    # ================================================================
    # CORS SETTINGS - ENHANCED
    # ================================================================
    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        os.getenv("FRONTEND_URL", "http://localhost:3000")
    ]

    # ================================================================
    # DEVELOPMENT SETTINGS
    # ================================================================
    debug: bool = bool(os.getenv("DEBUG", "false").lower() == "true")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    app_port: int = int(os.getenv("PORT", "8000"))

    # ================================================================
    # FEATURE FLAGS
    # ================================================================
    enable_google_drive: bool = bool(os.getenv("ENABLE_GOOGLE_DRIVE", "true").lower() == "true")
    enable_enhanced_web_scraping: bool = bool(os.getenv("ENABLE_ENHANCED_WEB_SCRAPING", "true").lower() == "true")
    enable_selenium: bool = bool(os.getenv("ENABLE_SELENIUM", "true").lower() == "true")
    enable_advanced_excel_processing: bool = bool(os.getenv("ENABLE_ADVANCED_EXCEL_PROCESSING", "true").lower() == "true")

    # ================================================================
    # PERFORMANCE SETTINGS
    # ================================================================
    max_concurrent_processing: int = int(os.getenv("MAX_CONCURRENT_PROCESSING", "5"))
    processing_timeout_seconds: int = int(os.getenv("PROCESSING_TIMEOUT_SECONDS", "300"))

    # Batch processing limits
    max_batch_sources: int = int(os.getenv("MAX_BATCH_SOURCES", "10"))
    max_google_drive_folder_files: int = int(os.getenv("MAX_GOOGLE_DRIVE_FOLDER_FILES", "50"))

    # ================================================================
    # CACHE AND PERFORMANCE SETTINGS
    # ================================================================
    enable_content_caching: bool = bool(os.getenv("ENABLE_CONTENT_CACHING", "false").lower() == "true")
    cache_ttl_seconds: int = int(os.getenv("CACHE_TTL_SECONDS", "3600"))

    # ================================================================
    # ERROR HANDLING
    # ================================================================
    max_retry_attempts: int = int(os.getenv("MAX_RETRY_ATTEMPTS", "3"))
    retry_delay_seconds: int = int(os.getenv("RETRY_DELAY_SECONDS", "1"))

    # ================================================================
    # MONITORING AND LOGGING
    # ================================================================
    enable_detailed_logging: bool = bool(os.getenv("ENABLE_DETAILED_LOGGING", "true").lower() == "true")
    log_file_path: str = os.getenv("LOG_FILE_PATH", "./logs/rag_backend.log")


# Create global settings instance
settings = Settings()


# ====================================================================
# VALIDATION FUNCTIONS
# ====================================================================
def validate_settings():
    """Validate critical settings and warn about missing configurations"""
    warnings = []

    # Check Ollama/DeepSeek
    try:
        import requests
        response = requests.get(f"{settings.ollama_base_url}/api/tags", timeout=5)
        if response.status_code == 200:
            tags = response.json().get('models', [])
            model_names = [model.get('name', '') for model in tags]
            if settings.ollama_model_name not in model_names:
                warnings.append(f"⚠️ DeepSeek model '{settings.ollama_model_name}' not found. Available: {model_names}")
            else:
                print(f"✅ DeepSeek model '{settings.ollama_model_name}' is available")
        else:
            warnings.append(f"⚠️ Ollama server not responding at {settings.ollama_base_url}")
    except Exception as e:
        warnings.append(f"⚠️ Cannot connect to Ollama: {e}")

    # Check Tally XML (no dependencies needed - uses requests)
    if settings.enable_tally_xml:
        print(f"✅ Tally XML integration enabled")
        print(f"   Tally URL: {settings.tally_base_url}")
        print(f"   Tally Host: {settings.tally_host}")
        print(f"   Tally Port: {settings.tally_port}")
        print(f"   Tally Method: {settings.tally_method}")
        
        # Test Tally connection
        try:
            import requests
            test_xml = "<ENVELOPE><HEADER><VERSION>1</VERSION><TALLYREQUEST>Export</TALLYREQUEST><TYPE>Data</TYPE><ID>List of Companies</ID></HEADER><BODY><DESC><STATICVARIABLES><SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT></STATICVARIABLES></DESC></BODY></ENVELOPE>"
            response = requests.post(settings.tally_base_url, data=test_xml, headers={'Content-Type': 'text/xml'}, timeout=5)
            if response.status_code == 200:
                print(f"✅ Tally connection successful - Server is running")
            else:
                warnings.append(f"⚠️ Tally server responded with status {response.status_code}")
        except requests.exceptions.ConnectionError:
            warnings.append(f"⚠️ Cannot connect to Tally at {settings.tally_base_url} - Ensure TallyPrime is running")
        except Exception as e:
            warnings.append(f"⚠️ Tally connection test failed: {e}")

    # Check legacy ODBC (deprecated)
    if settings.tally_method == "odbc":
        warnings.append("⚠️ ODBC method is deprecated - Consider using XML method instead")
        try:
            import pyodbc
            print(f"✅ pyodbc installed (legacy ODBC support)")
            print(f"   Tally DSN: {settings.tally_odbc_dsn}")
        except ImportError:
            warnings.append("⚠️ ODBC method selected but pyodbc not installed")
            warnings.append("   Recommended: Switch to XML method (set TALLY_METHOD=xml)")

    # Check Google Drive
    if settings.enable_google_drive and not settings.google_drive_credentials_path:
        warnings.append("⚠️ Google Drive enabled but credentials path not set")

    # Check Selenium
    if settings.enable_selenium:
        try:
            from selenium import webdriver
            print("✅ Selenium available for web scraping")
        except ImportError:
            warnings.append("⚠️ Selenium enabled but package not installed")

    # Create directories
    for dir_path in [settings.upload_path, settings.vector_store_path]:
        if not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
            print(f"✅ Created directory: {dir_path}")

    # Log warnings
    for warning in warnings:
        print(warning)

    if not warnings:
        print("✅ All settings validated successfully")


# ====================================================================
# HELPER FUNCTIONS
# ====================================================================
def is_tally_available() -> bool:
    """Check if Tally XML integration is available"""
    if not settings.enable_tally_xml:
        return False
    try:
        import requests
        test_xml = "<ENVELOPE><HEADER><VERSION>1</VERSION><TALLYREQUEST>Export</TALLYREQUEST><TYPE>Data</TYPE><ID>List of Companies</ID></HEADER><BODY><DESC><STATICVARIABLES><SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT></STATICVARIABLES></DESC></BODY></ENVELOPE>"
        response = requests.post(settings.tally_base_url, data=test_xml, headers={'Content-Type': 'text/xml'}, timeout=5)
        return response.status_code == 200
    except:
        return False


def is_tally_odbc_available() -> bool:
    """Check if legacy Tally ODBC is available (deprecated)"""
    if settings.tally_method != "odbc":
        return False
    try:
        import pyodbc
        return True
    except ImportError:
        return False


def is_google_drive_enabled() -> bool:
    """Check if Google Drive integration is properly configured"""
    return (settings.enable_google_drive and
            settings.google_drive_credentials_path and
            os.path.exists(settings.google_drive_credentials_path))


def is_selenium_available() -> bool:
    """Check if Selenium is available"""
    if not settings.enable_selenium:
        return False
    try:
        from selenium import webdriver
        return True
    except ImportError:
        return False


def is_ollama_available() -> bool:
    """Check if Ollama server is running"""
    try:
        import requests
        response = requests.get(f"{settings.ollama_base_url}/api/tags", timeout=5)
        return response.status_code == 200
    except:
        return False


def get_supported_file_types() -> List[str]:
    """Get list of all supported file types"""
    base_types = settings.allowed_file_types_list
    
    if is_google_drive_enabled():
        base_types.extend(['google_drive_file', 'google_drive_folder'])
    
    if settings.enable_enhanced_web_scraping:
        base_types.extend(['enhanced_web_url'])
    
    if settings.enable_tally_file_processing:
        base_types.extend(['tally_xml', 'tally_export'])
    
    return list(set(base_types))


def get_environment_info() -> dict:
    """Get current environment information"""
    return {
        "debug_mode": settings.debug,
        "app_port": settings.app_port,
        "ollama_available": is_ollama_available(),
        "ollama_model": settings.ollama_model_name,
        "tally_available": is_tally_available(),
        "tally_method": settings.tally_method,
        "tally_xml_enabled": settings.enable_tally_xml,
        "tally_base_url": settings.tally_base_url,
        "tally_host": settings.tally_host,
        "tally_port": settings.tally_port,
        "google_drive_enabled": is_google_drive_enabled(),
        "selenium_available": is_selenium_available(),
        "enhanced_web_scraping": settings.enable_enhanced_web_scraping,
        "advanced_excel_processing": settings.enable_advanced_excel_processing,
        "supported_file_types": get_supported_file_types(),
        "max_file_size_mb": settings.max_file_size_mb,
        "chunk_size": settings.chunk_size,
        "embedding_model": settings.embedding_model,
        "database": f"{settings.dbhost}:{settings.dbport}/{settings.dbname}"
    }


def get_tally_status() -> dict:
    """Get Tally integration status"""
    return {
        "enabled": settings.enable_tally_live_data,
        "available": is_tally_available(),
        "method": settings.tally_method,
        "xml": {
            "enabled": settings.enable_tally_xml,
            "host": settings.tally_host,
            "port": settings.tally_port,
            "base_url": settings.tally_base_url,
            "timeout": settings.tally_timeout
        },
        "odbc": {
            "dsn": settings.tally_odbc_dsn,
            "available": is_tally_odbc_available(),
            "deprecated": True
        },
        "company": settings.tally_company_name,
        "cache_enabled": settings.tally_cache_enabled,
        "cache_ttl": settings.tally_cache_ttl,
        "file_processing": settings.enable_tally_file_processing
    }


# Run validation when module is imported
if __name__ != "__main__":
    validate_settings()
