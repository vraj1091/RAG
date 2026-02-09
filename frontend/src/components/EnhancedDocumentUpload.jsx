import React, { useState, useCallback } from 'react';
import { Upload, FileText, Download, Globe, Link, Plus, X, CheckCircle, AlertCircle } from 'lucide-react';
import axios from 'axios';

const EnhancedDocumentUpload = ({ onUploadSuccess, onError }) => {
  const [activeTab, setActiveTab] = useState('upload');
  const [isProcessing, setIsProcessing] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [pdfUrl, setPdfUrl] = useState('');
  const [webUrls, setWebUrls] = useState(['']);
  const [previewData, setPreviewData] = useState(null);

  const handleFileUpload = async (files) => {
    const formData = new FormData();
    formData.append('file', files[0]);

    try {
      setIsProcessing(true);
      // --- FIX: Changed the endpoint from '/upload-enhanced' to '/upload' to match your documents.py ---
      const response = await axios.post('/api/v1/documents/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        onUploadProgress: (progressEvent) => {
          const progress = (progressEvent.loaded / progressEvent.total) * 100;
          setUploadProgress(progress);
        }
      });

      if (response.data) {
        onUploadSuccess(response.data);
        setUploadProgress(0);
      }
    } catch (error) {
      onError(error.response?.data?.detail || 'Upload failed');
    } finally {
      setIsProcessing(false);
    }
  };

  const handlePdfUrlSubmit = async () => {
    if (!pdfUrl.trim()) return;

    try {
      setIsProcessing(true);
      const response = await axios.post('/api/v1/documents/process-pdf-url',
        new URLSearchParams({ pdf_url: pdfUrl }),
        {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        }
      );

      if (response.data) {
        onUploadSuccess(response.data);
        setPdfUrl('');
      }
    } catch (error) {
      onError(error.response?.data?.detail || 'PDF URL processing failed');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleWebUrlsSubmit = async () => {
    const validUrls = webUrls.filter(url => url.trim());
    if (validUrls.length === 0) return;

    try {
      setIsProcessing(true);
      const sources = validUrls.map(url => ({ url: url.trim(), type: 'web_url' }));

      const response = await axios.post('/api/v1/documents/process-multiple-sources',
        sources,
        {
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        }
      );

      if (response.data) {
        onUploadSuccess(response.data);
        setWebUrls(['']);
      }
    } catch (error) {
      onError(error.response?.data?.detail || 'Web URL processing failed');
    } finally {
      setIsProcessing(false);
    }
  };

  const previewSource = async (url, type) => {
    try {
      const response = await axios.post('/api/v1/documents/preview-source',
        new URLSearchParams({ source_url: url, source_type: type }),
        {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        }
      );
      setPreviewData(response.data);
    } catch (error) {
      console.error('Preview failed:', error);
    }
  };

  const addWebUrlField = () => {
    if (webUrls.length < 5) {
      setWebUrls([...webUrls, '']);
    }
  };

  const removeWebUrlField = (index) => {
    if (webUrls.length > 1) {
      setWebUrls(webUrls.filter((_, i) => i !== index));
    }
  };

  const updateWebUrl = (index, value) => {
    const newUrls = [...webUrls];
    newUrls[index] = value;
    setWebUrls(newUrls);
  };

  const TabButton = ({ id, label, icon: Icon, active }) => (
    <button
      onClick={() => setActiveTab(id)}
      className={`flex items-center px-4 py-2 rounded-lg font-medium transition-all ${
        active
          ? 'bg-blue-500 text-white shadow-md'
          : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
      }`}
    >
      <Icon className="w-4 h-4 mr-2" />
      {label}
    </button>
  );

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 max-w-4xl mx-auto">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">Knowledge Base & Integrations</h2>

      {/* Tab Navigation */}
      <div className="flex space-x-2 mb-6 bg-gray-50 p-1 rounded-lg">
        <TabButton id="upload" label="File Upload" icon={Upload} active={activeTab === 'upload'} />
        <TabButton id="pdf-url" label="PDF Links" icon={FileText} active={activeTab === 'pdf-url'} />
        <TabButton id="web-scraping" label="Web Sources" icon={Globe} active={activeTab === 'web-scraping'} />
        <TabButton id="integrations" label="Integrations" icon={Link} active={activeTab === 'integrations'} />
      </div>

      {/* Tab Content */}
      {activeTab === 'upload' && (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-800">Upload Documents</h3>
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
            <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600 mb-4">
              Drag and drop files or click to browse
            </p>
            <p className="text-sm text-gray-500 mb-4">
              Supported formats: PDF, DOCX, TXT, PNG, JPG, JPEG, <strong>XLSX, XLS</strong>
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
                isProcessing ? 'opacity-50 cursor-not-allowed' : ''
              }`}
            >
              {isProcessing ? 'Processing...' : 'Choose Files'}
            </label>
            {uploadProgress > 0 && uploadProgress < 100 && (
              <div className="mt-4">
                <div className="bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${uploadProgress}%` }}
                  ></div>
                </div>
                <p className="text-sm text-gray-600 mt-2">{Math.round(uploadProgress)}% uploaded</p>
              </div>
            )}
          </div>
        </div>
      )}

      {activeTab === 'pdf-url' && (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-800">Add PDF from URL</h3>
          <p className="text-gray-600 text-sm">
            Paste a direct link to a PDF file or a Google Drive/Dropbox share link
          </p>
          <div className="flex space-x-2">
            <input
              type="url"
              value={pdfUrl}
              onChange={(e) => setPdfUrl(e.target.value)}
              placeholder="https://drive.google.com/file/d/... or https://example.com/document.pdf"
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={isProcessing}
            />
            <button
              onClick={() => previewSource(pdfUrl, 'pdf_url')}
              className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
              disabled={!pdfUrl.trim() || isProcessing}
            >
              Preview
            </button>
            <button
              onClick={handlePdfUrlSubmit}
              className={`px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors ${
                isProcessing || !pdfUrl.trim() ? 'opacity-50 cursor-not-allowed' : ''
              }`}
              disabled={isProcessing || !pdfUrl.trim()}
            >
              {isProcessing ? 'Processing...' : 'Add PDF'}
            </button>
          </div>

          <div className="bg-blue-50 p-4 rounded-lg">
            <h4 className="font-medium text-blue-800 mb-2">Supported Sources:</h4>
            <ul className="text-sm text-blue-700 space-y-1">
              <li>• Google Drive shared links</li>
              <li>• Dropbox shared links</li>
              <li>• Direct PDF URLs</li>
              <li>• Cloud storage public links</li>
            </ul>
          </div>
        </div>
      )}

      {activeTab === 'web-scraping' && (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-800">Web Content Scraping</h3>
          <p className="text-gray-600 text-sm">
            Add web pages to extract and index their content for searching
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
                  onClick={() => previewSource(url, 'web_url')}
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
                isProcessing || webUrls.every(url => !url.trim()) ? 'opacity-50 cursor-not-allowed' : ''
              }`}
              disabled={isProcessing || webUrls.every(url => !url.trim())}
            >
              {isProcessing ? 'Processing...' : 'Process URLs'}
            </button>
          </div>

          <div className="bg-green-50 p-4 rounded-lg">
            <h4 className="font-medium text-green-800 mb-2">Works Best With:</h4>
            <ul className="text-sm text-green-700 space-y-1">
              <li>• Documentation sites</li>
              <li>• Blog articles</li>
              <li>• News articles</li>
              <li>• Knowledge bases</li>
            </ul>
          </div>
        </div>
      )}

      {activeTab === 'integrations' && (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-800">Advanced Integrations</h3>

          <div className="border border-gray-200 rounded-lg p-4">
            <h4 className="font-medium text-gray-800 mb-2">Google Drive Folder</h4>
            <p className="text-sm text-gray-600 mb-3">
              Process all PDFs in a shared Google Drive folder (requires API setup)
            </p>
            <div className="flex space-x-2">
              <input
                type="url"
                placeholder="Google Drive folder share link"
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                disabled
              />
              <button
                className="px-4 py-2 bg-gray-300 text-gray-500 rounded-lg cursor-not-allowed"
                disabled
              >
                Coming Soon
              </button>
            </div>
          </div>

          <div className="border border-gray-200 rounded-lg p-4">
            <h4 className="font-medium text-gray-800 mb-2">Confluence Spaces</h4>
            <p className="text-sm text-gray-600 mb-3">
              Connect to Confluence and index documentation spaces
            </p>
            <div className="flex space-x-2">
              <input
                type="text"
                placeholder="Confluence space URL or API endpoint"
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                disabled
              />
              <button
                className="px-4 py-2 bg-gray-300 text-gray-500 rounded-lg cursor-not-allowed"
                disabled
              >
                Coming Soon
              </button>
            </div>
          </div>

          <div className="border border-gray-200 rounded-lg p-4">
            <h4 className="font-medium text-gray-800 mb-2">GitHub Repository</h4>
            <p className="text-sm text-gray-600 mb-3">
              Index documentation and README files from GitHub repos
            </p>
            <div className="flex space-x-2">
              <input
                type="text"
                placeholder="GitHub repository URL"
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                disabled
              />
              <button
                className="px-4 py-2 bg-gray-300 text-gray-500 rounded-lg cursor-not-allowed"
                disabled
              >
                Coming Soon
              </button>
            </div>
          </div>
        </div>
      )}

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
                  Words: {previewData.word_count} | Characters: {previewData.character_count}
                </p>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default EnhancedDocumentUpload;
