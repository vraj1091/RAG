import React, { useState, useEffect } from "react";
import toast from "react-hot-toast";
import {
  Upload,
  FileText,
  Globe,
  Link,
  Plus,
  X,
  CheckCircle,
  AlertCircle,
} from "lucide-react";
import { apiService } from "../services/apiService";

// --- Loading Spinner Component ---
const LoadingSpinner = ({ size = "medium", color = "blue" }) => {
  const sizeClasses = {
    small: "w-4 h-4",
    medium: "w-8 h-8",
    large: "w-12 h-12",
  };
  const colorClasses = {
    blue: "border-blue-500",
    white: "border-white",
  };
  return (
    <div
      className={`animate-spin rounded-full ${sizeClasses[size]} border-t-2 border-b-2 ${colorClasses[color]}`}
    ></div>
  );
};

// --- Helper functions ---
const formatFileSize = (bytes) => {
  const k = 1024;
  const sizes = ["Bytes", "KB", "MB", "GB"];
  if (!bytes) return "0 Bytes";
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
};

const getStatusIcon = (status) => {
  switch (status) {
    case "completed":
      return "✅";
    case "processing":
      return "⏳";
    case "failed":
      return "❌";
    default:
      return "⏸️";
  }
};

const TabButton = ({ id, label, icon: Icon, active, setActiveTab }) => (
  <button
    onClick={() => setActiveTab(id)}
    className={`flex items-center px-4 py-2 rounded-lg font-medium transition-all ${
      active
        ? "bg-blue-500 text-white shadow-md"
        : "bg-gray-100 text-gray-700 hover:bg-gray-200"
    }`}
  >
    <Icon className="w-4 h-4 mr-2" />
    {label}
  </button>
);

function KnowledgeBase() {
  const [activeTab, setActiveTab] = useState("upload");
  const [documents, setDocuments] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isProcessing, setIsProcessing] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [fileUrl, setFileUrl] = useState("");
  const [webUrls, setWebUrls] = useState([""]);
  const [previewData, setPreviewData] = useState(null);

  // Load documents & stats
  useEffect(() => {
    loadKnowledgeBase();
  }, []);

  const loadKnowledgeBase = async () => {
    try {
      setLoading(true);
      const [docs, stats] = await Promise.all([
        apiService.getDocuments(),
        apiService.getDocumentStats(),
      ]);
      setDocuments(docs);
      setStats(stats);
    } catch (err) {
      console.error("Failed to load knowledge base:", err);
      toast.error("Failed to load knowledge base");
    } finally {
      setLoading(false);
    }
  };

  // --- Upload Handlers ---
  const handleFileUpload = async (files) => {
    const file = files[0];
    if (!file) return;

    try {
      setIsProcessing(true);
      setUploadProgress(0);

      const result = await apiService.uploadDocument(file, (progress) => {
        setUploadProgress(progress);
      });

      // Simple success message without mentioning financial insights
      toast.success(`${file.name} uploaded successfully!`);
      
      await loadKnowledgeBase();

    } catch (error) {
      toast.error("Upload failed: " + (error.response?.data?.detail || error.message));
    } finally {
      setIsProcessing(false);
      setUploadProgress(0);
    }
  };

  // Smart URL detection for Google Drive files/folders
  const handleFileUrlSubmit = async () => {
    if (!fileUrl.trim()) return;
    
    try {
      setIsProcessing(true);
      
      // Detect Google Drive folder
      if (fileUrl.includes('drive.google.com/drive/folders/')) {
        console.log('📁 Detected Google Drive folder');
        toast.loading('Processing Google Drive folder (all file types)...', { id: 'folder-processing' });
        await apiService.processGoogleDriveFolder(fileUrl);
        toast.success('Google Drive folder processed successfully!', { id: 'folder-processing' });
      }
      // Detect Google Drive file
      else if (fileUrl.includes('drive.google.com/file/') || fileUrl.includes('drive.google.com/uc?id=')) {
        console.log('📄 Detected Google Drive file');
        toast.loading('Processing Google Drive file...', { id: 'file-processing' });
        await apiService.processGoogleDriveFile(fileUrl);
        toast.success('File processed successfully!', { id: 'file-processing' });
      }
      // Regular file URL
      else {
        console.log('🔗 Detected direct file URL');
        toast.loading('Processing file...', { id: 'file-processing' });
        await apiService.processPdfUrl(fileUrl);
        toast.success('File processed successfully!', { id: 'file-processing' });
      }
      
      setFileUrl("");
      await loadKnowledgeBase();
      
    } catch (error) {
      console.error('Processing error:', error);
      toast.error("Processing failed: " + (error.response?.data?.detail || error.message));
    } finally {
      setIsProcessing(false);
    }
  };

  const handleWebUrlsSubmit = async () => {
    const validUrls = webUrls.filter((url) => url.trim());
    if (validUrls.length === 0) return;
    try {
      setIsProcessing(true);
      const sources = validUrls.map((url) => ({ url: url.trim(), type: "web_url" }));
      await apiService.processMultipleSources({ sources });
      toast.success("Web URLs processed!");
      setWebUrls([""]);
      await loadKnowledgeBase();
    } catch (error) {
      toast.error("Web URL processing failed: " + (error.response?.data?.detail || error.message));
    } finally {
      setIsProcessing(false);
    }
  };

  // --- Preview ---
  const previewSource = async (url, type) => {
    if (!url) return;
    try {
      const response = await apiService.previewSource(url, type);
      setPreviewData(response);
    } catch (error) {
      toast.error("Preview failed");
    }
  };

  // --- Web URLs management ---
  const addWebUrlField = () => {
    if (webUrls.length < 5) setWebUrls([...webUrls, ""]);
  };
  const removeWebUrlField = (index) => {
    if (webUrls.length > 1) setWebUrls(webUrls.filter((_, i) => i !== index));
  };
  const updateWebUrl = (index, value) => {
    const newUrls = [...webUrls];
    newUrls[index] = value;
    setWebUrls(newUrls);
  };

  // --- Document deletion ---
  const deleteDocument = async (documentId, filename) => {
    if (!window.confirm(`Delete "${filename}"?`)) return;
    try {
      await apiService.deleteDocument(documentId);
      toast.success("Document deleted");
      await loadKnowledgeBase();
    } catch (error) {
      toast.error("Failed to delete");
    }
  };

  // --- Render ---
  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="large" />
      </div>
    );
  }

  const processingStatus = (stats && stats.processing_status) || {};

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-xl shadow-sm border p-6">
        <h1 className="text-2xl font-bold text-gray-900 flex items-center">
          📚 Knowledge Base ({documents.length} documents)
        </h1>
        <p className="text-gray-600 mt-1">
          Manage your AI knowledge base files – upload, view, and delete documents
        </p>
        {stats && (
          <div className="mt-3 text-sm text-gray-600">
            <span>Local Documents: {stats.local_documents}</span> |{" "}
            <span>External Sources: {stats.external_sources}</span> |{" "}
            <span>Google Drive: {stats.google_drive_sources || 0}</span> |{" "}
            <span>
              Status:{" "}
              {Object.entries(processingStatus).length > 0
                ? Object.entries(processingStatus)
                    .map(([k, v]) => `${k}: ${v}`)
                    .join(", ")
                : "No data"}
            </span>
          </div>
        )}
      </div>

      {/* Tabs */}
      <div className="flex space-x-2 mb-6 bg-gray-50 p-1 rounded-lg">
        <TabButton
          id="upload"
          label="File Upload"
          icon={Upload}
          active={activeTab === "upload"}
          setActiveTab={setActiveTab}
        />
        <TabButton
          id="file-url"
          label="File Links"
          icon={FileText}
          active={activeTab === "file-url"}
          setActiveTab={setActiveTab}
        />
        <TabButton
          id="web-scraping"
          label="Web Sources"
          icon={Globe}
          active={activeTab === "web-scraping"}
          setActiveTab={setActiveTab}
        />
        <TabButton
          id="integrations"
          label="Integrations"
          icon={Link}
          active={activeTab === "integrations"}
          setActiveTab={setActiveTab}
        />
      </div>

      {/* Upload Tab */}
      {activeTab === "upload" && (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-800">
            Upload Documents
          </h3>
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
            <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600 mb-4">
              Drag/drop or click to browse files
            </p>
            <p className="text-sm text-gray-500 mb-4">
              Supported: PDF, DOCX, TXT, PNG, JPG, JPEG, XLSX, XLS
            </p>
            <input
              type="file"
              multiple
              accept=".pdf,.docx,.txt,.png,.jpg,.jpeg,.xlsx,.xls"
              onChange={(e) => handleFileUpload(e.target.files)}
              className="hidden"
              id="file-upload"
              disabled={isProcessing}
            />
            <label
              htmlFor="file-upload"
              className={`inline-block px-6 py-2 bg-blue-500 text-white rounded-lg cursor-pointer hover:bg-blue-600 transition-colors ${
                isProcessing ? "opacity-50 cursor-not-allowed" : ""
              }`}
            >
              {isProcessing ? "Processing..." : "Choose Files"}
            </label>
            {uploadProgress > 0 && uploadProgress < 100 && (
              <div className="mt-4">
                <div className="bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${uploadProgress}%` }}
                  ></div>
                </div>
                <p className="text-sm text-gray-600 mt-2">
                  {Math.round(uploadProgress)}% uploaded
                </p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* File URL Tab */}
      {activeTab === "file-url" && (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-800">
            Add Files from Google Drive or Direct Links
          </h3>
          <p className="text-gray-600 text-sm">
            📄 Paste a Google Drive file/folder link or direct file URL
          </p>
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 mb-3">
            <p className="text-sm text-blue-800">
              <strong>💡 Supported Sources & File Types:</strong>
            </p>
            <ul className="text-sm text-blue-700 mt-1 ml-4 list-disc">
              <li><strong>Documents:</strong> PDF, DOCX, TXT</li>
              <li><strong>Spreadsheets:</strong> XLSX, XLS, CSV</li>
              <li><strong>Images:</strong> PNG, JPG, JPEG (with OCR text extraction)</li>
              <li><strong>Google Drive:</strong> Single files or entire folders</li>
              <li><strong>Direct Links:</strong> Any publicly accessible file URL</li>
            </ul>
          </div>
          <div className="flex space-x-2">
            <input
              type="url"
              value={fileUrl}
              onChange={(e) => setFileUrl(e.target.value)}
              placeholder="https://drive.google.com/... or direct file link"
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={isProcessing}
            />
            <button
              onClick={() => previewSource(fileUrl, "pdf_url")}
              className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
              disabled={!fileUrl.trim() || isProcessing}
            >
              Preview
            </button>
            <button
              onClick={handleFileUrlSubmit}
              className={`px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors ${
                isProcessing || !fileUrl.trim()
                  ? "opacity-50 cursor-not-allowed"
                  : ""
              }`}
              disabled={isProcessing || !fileUrl.trim()}
            >
              {isProcessing ? "Processing..." : "Process File"}
            </button>
          </div>
        </div>
      )}

      {/* Web Scraping Tab */}
      {activeTab === "web-scraping" && (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-800">
            Web Content Scraping
          </h3>
          <p className="text-gray-600 text-sm">
            Add web pages to index their content for searching.
          </p>
          <div className="space-y-3">
            {webUrls.map((url, index) => (
              <div key={index} className="flex space-x-2">
                <input
                  type="url"
                  value={url}
                  onChange={(e) => updateWebUrl(index, e.target.value)}
                  placeholder="https://example.com/page"
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  disabled={isProcessing}
                />
                <button
                  onClick={() => previewSource(url, "web_url")}
                  className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
                  disabled={!url.trim() || isProcessing}
                >
                  Preview
                </button>
                {webUrls.length > 1 && (
                  <button
                    onClick={() => removeWebUrlField(index)}
                    className="px-3 py-2 bg-red-100 text-red-600 rounded-lg hover:bg-red-200 transition-colors"
                    disabled={isProcessing}
                  >
                    <X className="w-4 h-4" />
                  </button>
                )}
              </div>
            ))}
          </div>
          <div className="flex justify-between items-center">
            <button
              onClick={addWebUrlField}
              className="flex items-center px-4 py-2 bg-green-100 text-green-700 rounded-lg hover:bg-green-200 transition-colors"
              disabled={webUrls.length >= 5 || isProcessing}
            >
              <Plus className="w-4 h-4 mr-2" />
              Add Another URL
            </button>
            <button
              onClick={handleWebUrlsSubmit}
              className={`px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors ${
                isProcessing || webUrls.every((url) => !url.trim())
                  ? "opacity-50 cursor-not-allowed"
                  : ""
              }`}
              disabled={isProcessing || webUrls.every((url) => !url.trim())}
            >
              {isProcessing ? "Processing..." : "Process URLs"}
            </button>
          </div>
        </div>
      )}

      {/* Integrations Tab */}
      {activeTab === "integrations" && (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-800">
            Advanced Integrations
          </h3>
          <div className="border border-gray-200 rounded-lg p-4">
            <p className="text-gray-600 mb-3">Available & Coming Soon:</p>
            <ul className="text-sm text-gray-600 space-y-2">
              <li>✅ Google Drive (Available now!)</li>
              <li>⏳ Confluence integration</li>
              <li>⏳ GitHub repository sync</li>
              <li>⏳ Dropbox integration</li>
              <li>⏳ OneDrive support</li>
            </ul>
          </div>
        </div>
      )}

      {/* Document List */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden mt-8">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">
            Your Documents
          </h3>
        </div>
        <div className="overflow-x-auto">
          <div className="space-y-3 p-6">
            {documents.length > 0 ? (
              documents.map((doc) => (
                <div
                  key={doc.id}
                  className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                >
                  <div className="flex items-center">
                    <span className="text-2xl mr-3">
                      {doc.file_type === "google_drive_folder" ? "📁" :
                       doc.file_type === "google_drive_file" ? "📄" :
                       doc.file_type === "xlsx" || doc.file_type === "xls" ? "📊" :
                       doc.file_type === "docx" ? "📝" :
                       doc.document_type === "image" ? "🖼️" : "📄"}
                    </span>
                    <div>
                      <div className="font-medium text-gray-900 truncate max-w-md">
                        {doc.file_type === "pdf_url"
                          ? `External File Link`
                          : doc.file_type === "web_url"
                          ? `Web Page`
                          : doc.file_type === "google_drive_file"
                          ? `Google Drive File`
                          : doc.file_type === "google_drive_folder"
                          ? `Google Drive Folder`
                          : doc.original_filename}
                      </div>
                      <div className="text-sm text-gray-500">
                        {(doc.file_type || "").toUpperCase()}
                        {" • "}
                        {(doc.file_type === "pdf_url" ||
                          doc.file_type === "web_url" ||
                          doc.file_type === "google_drive_file" ||
                          doc.file_type === "google_drive_folder")
                          ? "External"
                          : formatFileSize(doc.file_size)}
                        {" • "}
                        {getStatusIcon(doc.processing_status)}{" "}
                        {doc.processing_status}
                      </div>
                    </div>
                  </div>
                  <button
                    onClick={() =>
                      deleteDocument(doc.id, doc.original_filename)
                    }
                    className="text-red-600 hover:text-red-800 p-2 transition-colors"
                    title="Delete document"
                  >
                    🗑️
                  </button>
                </div>
              ))
            ) : (
              <div className="text-center py-12">
                <span className="text-6xl mb-4 block">📚</span>
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  No documents in your knowledge base
                </h3>
                <p className="text-gray-500 mb-6">
                  Upload your first document to start building your AI-powered
                  knowledge base.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Preview Modal */}
      {previewData && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-2xl max-h-96 overflow-y-auto">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">Content Preview</h3>
              <button
                onClick={() => setPreviewData(null)}
                className="text-gray-500 hover:text-gray-700"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="space-y-3">
              <div className="flex items-center space-x-2">
                {previewData.supported ? (
                  <CheckCircle className="w-5 h-5 text-green-500" />
                ) : (
                  <AlertCircle className="w-5 h-5 text-red-500" />
                )}
                <span className="font-medium">{previewData.type}</span>
              </div>
              <p className="text-sm text-gray-600">{previewData.url}</p>
              <div className="bg-gray-50 p-3 rounded-lg">
                <p className="text-sm">{previewData.preview}</p>
              </div>
              {previewData.word_count && (
                <p className="text-xs text-gray-500">
                  Words: {previewData.word_count} | Characters:{" "}
                  {previewData.character_count}
                </p>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default KnowledgeBase;
