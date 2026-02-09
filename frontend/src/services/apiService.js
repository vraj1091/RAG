import axios from "axios";

const API_BASE_URL =
  process.env.REACT_APP_API_URL || "http://localhost:8001/api/v1";

class ApiService {
  constructor() {
    this.api = axios.create({
      baseURL: API_BASE_URL,
    });

    this.api.interceptors.request.use((config) => {
      const token = localStorage.getItem("token");
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    this.api.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          console.warn("🔒 Token expired or invalid — logging out...");
          localStorage.removeItem("token");
          localStorage.removeItem("user");
          window.location.href = "/login";
        }
        return Promise.reject(error);
      }
    );
  }

  // ====================================================================
  // AUTHENTICATION
  // ====================================================================
  async register(username, email, password) {
    const response = await this.api.post("/auth/register", {
      username,
      email,
      password,
    });
    return response.data;
  }

  async login(username, password) {
    const formData = new FormData();
    formData.append("username", username);
    formData.append("password", password);

    const response = await this.api.post("/auth/token", formData);

    if (response.data?.access_token) {
      localStorage.setItem("token", response.data.access_token);
    }

    return response.data;
  }

  async getCurrentUser() {
    const response = await this.api.get("/auth/me");
    return response.data;
  }

  // ====================================================================
  // DOCUMENT MANAGEMENT
  // ====================================================================
  async uploadDocument(file, onUploadProgress = null) {
    const formData = new FormData();
    formData.append("file", file);

    const response = await this.api.post("/documents/upload", formData, {
      onUploadProgress: onUploadProgress
        ? (progressEvent) => {
            const percentCompleted = Math.round(
              (progressEvent.loaded * 100) / progressEvent.total
            );
            onUploadProgress(percentCompleted);
          }
        : undefined,
    });

    return response.data;
  }

  async getDocuments(skip = 0, limit = 50) {
    const response = await this.api.get(
      `/documents?skip=${skip}&limit=${limit}`
    );
    return response.data;
  }

  async getDocumentStats() {
    try {
      const response = await this.api.get("/documents/stats");
      return response.data;
    } catch (err) {
      return {
        total_documents: 0,
        processed_documents: 0,
        vector_stats: { total_chunks: 0 }
      };
    }
  }

  async analyzeFinancialExcel(formData) {
    const response = await this.api.post('/documents/analyze-financial-excel', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  }

  async deleteDocument(documentId) {
    const response = await this.api.delete(`/documents/${documentId}`);
    return response.data;
  }

  // ====================================================================
  // EXTERNAL URL PROCESSING
  // ====================================================================
  async processPdfUrl(url) {
    const formData = new FormData();
    formData.append("pdf_url", url);
    const response = await this.api.post("/documents/process-pdf-url", formData);
    return response.data;
  }

  async processWebUrl(url) {
    const formData = new FormData();
    formData.append("web_url", url);
    const response = await this.api.post("/documents/process-web-url", formData);
    return response.data;
  }

  async processGoogleDriveFile(url) {
    const formData = new FormData();
    formData.append("drive_url", url);
    const response = await this.api.post("/documents/process-google-drive-file", formData);
    return response.data;
  }

  async processGoogleDriveFolder(url) {
    const formData = new FormData();
    formData.append("folder_url", url);
    const response = await this.api.post("/documents/process-google-drive-folder", formData);
    return response.data;
  }

  async processWebUrlEnhanced(url) {
    const formData = new FormData();
    formData.append("web_url", url);
    const response = await this.api.post("/documents/process-web-url-enhanced", formData);
    return response.data;
  }

  async processMultipleSources(sourcesData) {
    const response = await this.api.post("/documents/process-multiple-sources", sourcesData);
    return response.data;
  }

  // ====================================================================
  // PREVIEW ENDPOINTS
  // ====================================================================
  async previewGoogleDrive(url) {
    const formData = new FormData();
    formData.append("drive_url", url);
    const response = await this.api.post("/documents/preview-google-drive", formData);
    return response.data;
  }

  async previewWebEnhanced(url) {
    const formData = new FormData();
    formData.append("web_url", url);
    const response = await this.api.post("/documents/preview-web-enhanced", formData);
    return response.data;
  }

  async previewSource(url, sourceType) {
    const formData = new FormData();
    formData.append("source_url", url);
    formData.append("source_type", sourceType);
    const response = await this.api.post("/documents/preview-source", formData);
    return response.data;
  }

  // ====================================================================
  // CHAT / CONVERSATIONS
  // ====================================================================
  async sendMessage(message, conversationId = null, mode = "rag") {
    const params = new URLSearchParams();
    params.append("mode", mode);
    const url = `/chat/?${params.toString()}`;
    const payload = { message };
    if (conversationId !== null && conversationId !== undefined) {
      payload.conversation_id = conversationId;
    }
    const response = await this.api.post(url, payload);
    return response.data;
  }

  async getConversations(skip = 0, limit = 20) {
    try {
      const response = await this.api.get(`/chat/conversations?skip=${skip}&limit=${limit}`);
      return response.data;
    } catch (err) {
      if (err.response?.status === 404) {
        const fallback = await this.api.get(`/conversations?skip=${skip}&limit=${limit}`);
        return fallback.data;
      }
      throw err;
    }
  }

  async getConversationMessages(conversationId, skip = 0, limit = 50) {
    const response = await this.api.get(`/chat/conversations/${conversationId}/messages?skip=${skip}&limit=${limit}`);
    return response.data;
  }

  async deleteConversation(conversationId) {
    const response = await this.api.delete(`/chat/conversations/${conversationId}`);
    return response.data;
  }

  async getChatStats() {
    try {
      const response = await this.api.get("/chat/stats");
      return response.data;
    } catch {
      return { total_conversations: 0 };
    }
  }

  // ====================================================================
  // 🔥 TALLY INTEGRATION - CORRECTED PATHS FROM YOUR SCREENSHOTS
  // ====================================================================

  /**
   * Test Tally connection
   * Route: /api/v1/tally-xml/tally/test-connection
   */
  async testTallyConnection() {
    try {
      const response = await axios.get('http://localhost:8001/api/v1/tally-xml/tally/test-connection');
      return response.data;
    } catch (error) {
      console.error('❌ Error testing Tally connection:', error);
      return { status: 'disconnected', message: 'Connection failed' };
    }
  }

  /**
   * Get Tally companies
   * Route: /api/v1/tally-xml/tally/companies
   */
  async getTallyCompanies() {
    try {
      const response = await axios.get('http://localhost:8001/api/v1/tally-xml/tally/companies');
      return response.data;
    } catch (error) {
      console.error('❌ Error fetching companies:', error);
      return { companies: [] };
    }
  }

  /**
   * 🔥 Get financial metrics (works with your old TallyAnalytics)
   * Route: /api/v1/tally-xml/tally/financial-metrics
   */
  async getTallyFinancialMetrics(params = {}) {
    try {
      const response = await axios.get('http://localhost:8001/api/v1/tally-xml/tally/financial-metrics', { 
        params 
      });
      return response.data;
    } catch (error) {
      console.error('❌ Error fetching financial metrics:', error);
      return { 
        success: false, 
        data: { totalRevenue: 0, totalExpenses: 0, netProfit: 0, cashBalance: 0 } 
      };
    }
  }

  /**
   * Get ledgers
   * Route: /api/v1/tally-xml/tally/ledgers
   */
  async getTallyLedgers(params = {}) {
    try {
      const response = await axios.get('http://localhost:8001/api/v1/tally-xml/tally/ledgers', { params });
      return response.data;
    } catch (error) {
      console.error('❌ Error fetching ledgers:', error);
      return { status: 'error', ledgers: [] };
    }
  }

  /**
   * Get vouchers
   * Route: /api/v1/tally-xml/tally/vouchers
   */
  async getTallyVouchers(params = {}) {
    try {
      const response = await axios.get('http://localhost:8001/api/v1/tally-xml/tally/vouchers', { params });
      return response.data;
    } catch (error) {
      console.error('❌ Error fetching vouchers:', error);
      return { status: 'error', vouchers: [] };
    }
  }

  /**
   * Get stock items
   * Route: /api/v1/tally-xml/tally/stock-items
   */
  async getTallyStockItems(params = {}) {
    try {
      const response = await axios.get('http://localhost:8001/api/v1/tally-xml/tally/stock-items', { params });
      return response.data;
    } catch {
      return { status: 'error', stock_items: [] };
    }
  }

  /**
   * Deprecated - kept for compatibility
   */
  async getTallyLiveData() {
    return this.getTallyFinancialMetrics();
  }

  async getTallyFinancialSummary(companyName = null) {
    return this.getTallyFinancialMetrics({ company_name: companyName });
  }
}

export const apiService = new ApiService();
export default apiService;
