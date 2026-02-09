import React, { useState, useEffect, useRef } from "react";
import { apiService } from "../services/apiService.js";
import LoadingSpinner from "../components/LoadingSpinner.jsx";
import toast from "react-hot-toast";
import { Bar, Line, Pie } from "react-chartjs-2";
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
} from "chart.js";

// Register Chart.js components
ChartJS.register(
  ArcElement,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement
);

function Chat() {
  const [messages, setMessages] = useState([]);
  const [currentMessage, setCurrentMessage] = useState("");
  const [conversations, setConversations] = useState([]);
  const [currentConversation, setCurrentConversation] = useState(null);
  const [loading, setLoading] = useState(false);
  const [conversationsLoading, setConversationsLoading] = useState(true);
  const [chatMode, setChatMode] = useState("rag");
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const messagesEndRef = useRef(null);

  // Load chat history
  useEffect(() => {
    loadConversations();
  }, []);

  // Always scroll to bottom on new message
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const loadConversations = async () => {
    try {
      setConversationsLoading(true);
      const data = await apiService.getConversations();
      setConversations(data || []);
      if (!data || data.length === 0) setChatMode("general");
    } catch (err) {
      console.error("Conversation load error:", err);
      toast.error("Failed to load chat history");
    } finally {
      setConversationsLoading(false);
    }
  };

  const loadConversation = async (conversationId) => {
    try {
      setLoading(true);
      const msgs = await apiService.getConversationMessages(conversationId);
      setCurrentConversation(conversations.find((c) => c.id === conversationId));
      setMessages(msgs || []);
      setSidebarOpen(false);
    } catch (err) {
      console.error("Conversation fetch error:", err);
      toast.error("Failed to load conversation");
    } finally {
      setLoading(false);
    }
  };

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!currentMessage.trim() || loading) return;

    const userMessage = currentMessage.trim();
    setCurrentMessage("");
    setLoading(true);

    // Temporary UI message
    const tempMessage = {
      id: `temp-${Date.now()}`,
      role: "user",
      content: userMessage,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, tempMessage]);

    try {
      const response = await apiService.sendMessage(
        userMessage,
        currentConversation?.id,
        chatMode
      );

      console.log("📊 API Response:", response); // ✅ Debug log

      // Remove temp message
      setMessages((prev) => prev.filter((msg) => msg.id !== tempMessage.id));

      // ✅ FIXED: Extract charts from response correctly
      let chartData = null;
      
      // Check if charts exist in response (from document upload)
      if (response.charts && typeof response.charts === 'object') {
        chartData = response.charts;
      }
      
      // Check if charts exist in financial_insights (from Excel processing)
      if (response.financial_insights && response.financial_insights.charts) {
        chartData = response.financial_insights.charts;
      }

      console.log("📊 Extracted Charts:", chartData); // ✅ Debug log

      // Create new messages with charts
      const newMessages = [
        {
          id: `user-${Date.now()}`,
          role: "user",
          content: userMessage,
          created_at: new Date().toISOString(),
        },
        {
          id: `assistant-${Date.now()}`,
          role: "assistant",
          content: response.message || "No response from assistant.",
          sources: response.sources || [],
          charts: chartData, // ✅ Pass chart data
          created_at: new Date().toISOString(),
          context_used: response.context_used || false,
        },
      ];

      setMessages((prev) => [...prev, ...newMessages]);

      // Update or reload conversations
      if (!currentConversation || currentConversation.id !== response.conversation_id) {
        setCurrentConversation({
          id: response.conversation_id,
          title:
            userMessage.substring(0, 50) +
            (userMessage.length > 50 ? "..." : ""),
        });
        await loadConversations();
      }
    } catch (err) {
      console.error("Send message error:", err);
      toast.error("Failed to send message");
      setMessages((prev) => prev.filter((msg) => msg.id !== tempMessage.id));
    } finally {
      setLoading(false);
    }
  };

  // ✅ FIXED: Render charts from object format
  const renderChart = (chartKey, chartData) => {
    try {
      console.log("🎨 Rendering chart:", chartKey, chartData); // ✅ Debug log

      const chartType = chartData.type?.toLowerCase() || 'bar';
      const ChartComponent = {
        bar: Bar,
        line: Line,
        pie: Pie,
      }[chartType] || Bar;

      const chartOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: "bottom",
            labels: {
              padding: 15,
              font: { size: 12 },
            },
          },
          title: {
            display: true,
            text: chartData.title || chartKey,
            font: { size: 16, weight: "bold" },
            padding: { top: 10, bottom: 20 },
          },
        },
        scales: chartType !== "pie" ? {
          y: {
            beginAtZero: true,
            ticks: {
              callback: function(value) {
                return '₹' + value.toLocaleString();
              }
            }
          }
        } : undefined,
      };

      return (
        <div key={chartKey} className="h-80 w-full mb-4">
          <ChartComponent data={chartData.data} options={chartOptions} />
        </div>
      );
    } catch (error) {
      console.error("❌ Chart render error:", error, chartData);
      return (
        <div key={chartKey} className="text-red-500 text-sm p-2 bg-red-50 rounded">
          ⚠️ Error rendering chart: {error.message}
        </div>
      );
    }
  };

  const startNewConversation = () => {
    setCurrentConversation(null);
    setMessages([]);
    setSidebarOpen(false);
  };

  const formatDate = (dateString) =>
    new Date(dateString).toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });

  // Sidebar for mobile & desktop
  const Sidebar = (
    <div
      className={`fixed top-0 left-0 z-40 w-11/12 max-w-xs h-full bg-white shadow-lg border-r border-gray-200
      sm:relative sm:block sm:w-80 sm:h-auto sm:shadow-none sm:border-none
      ${sidebarOpen ? "block" : "hidden"} sm:block`}
      style={{ minWidth: 250, maxWidth: 330 }}
    >
      <div className="flex flex-col h-full">
        <div className="flex items-center justify-between p-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">💬 Chat History</h2>
          <button
            className="sm:hidden text-2xl text-gray-500 p-2"
            onClick={() => setSidebarOpen(false)}
            aria-label="Close chat history"
          >
            ×
          </button>
        </div>
        <button
          onClick={startNewConversation}
          className="w-full px-4 py-3 btn-primary border-b border-gray-200 text-base sm:text-lg"
        >
          ➕ New Chat
        </button>
        <div className="flex gap-1 p-3 border-b border-gray-200">
          <button
            className={`flex-1 px-2 py-3 rounded ${
              chatMode === "general"
                ? "bg-primary-600 text-white"
                : "bg-gray-100 text-gray-700"
            }`}
            onClick={() => setChatMode("general")}
          >
            General
          </button>
          <button
            className={`flex-1 px-2 py-3 rounded ${
              chatMode === "rag"
                ? "bg-primary-600 text-white"
                : "bg-gray-100 text-gray-700"
            } ${conversations.length === 0 ? "opacity-50 cursor-not-allowed" : ""}`}
            onClick={() => conversations.length > 0 && setChatMode("rag")}
            disabled={conversations.length === 0}
          >
            Document
          </button>
        </div>

        {/* Scrollable Chat History */}
        <div className="flex-1 overflow-y-auto p-2">
          {conversationsLoading ? (
            <div className="p-4 text-center">
              <LoadingSpinner size="medium" />
              <p className="text-sm text-gray-500 mt-2">Loading...</p>
            </div>
          ) : conversations.length > 0 ? (
            conversations.map((c) => (
              <div
                key={c.id}
                className={`p-3 mb-2 rounded-lg cursor-pointer ${
                  currentConversation?.id === c.id
                    ? "bg-primary-50 border-l-4 border-primary-500"
                    : "hover:bg-gray-50"
                }`}
                onClick={() => loadConversation(c.id)}
              >
                <p className="text-sm font-medium text-gray-900 truncate">{c.title}</p>
                <p className="text-xs text-gray-500">{formatDate(c.created_at)}</p>
              </div>
            ))
          ) : (
            <div className="flex flex-col items-center justify-center h-full p-4 text-center">
              <span className="text-4xl mb-3">💬</span>
              <p className="text-gray-500 text-sm">No chat history yet</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 h-[calc(100vh-8rem)] flex flex-col sm:flex-row relative">
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-30 bg-black bg-opacity-30 block sm:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}
      {Sidebar}

      {/* Chat Area */}
      <div className="flex-1 flex flex-col overflow-x-hidden">
        {/* Header */}
        <div className="p-4 border-b border-gray-200 bg-gray-50 flex items-center">
          <button
            className="sm:hidden px-2 py-2 text-primary-600"
            onClick={() => setSidebarOpen(true)}
          >
            ☰
          </button>
          <h3 className="text-lg font-semibold text-gray-900 ml-2 truncate">
            {currentConversation ? currentConversation.title : "AI RAG Chat"}
          </h3>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-4 py-3">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center">
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                {chatMode === "rag" ? "Start a RAG chat" : "Start chatting"}
              </h3>
              <p className="text-gray-500 max-w-sm">
                {chatMode === "rag"
                  ? "Ask about your uploaded documents or request charts from Excel data."
                  : "Chat freely with AI."}
              </p>
            </div>
          ) : (
            <>
              {messages.map((m) => (
                <div
                  key={m.id}
                  className={`flex mb-3 ${
                    m.role === "user" ? "justify-end" : "justify-start"
                  }`}
                >
                  <div
                    className={`rounded-2xl px-4 py-3 max-w-[80vw] sm:max-w-2xl ${
                      m.role === "user"
                        ? "bg-primary-600 text-white"
                        : "bg-gray-100 text-gray-900"
                    }`}
                  >
                    {/* Message Content */}
                    {m.content && (
                      <p className="whitespace-pre-wrap">{m.content}</p>
                    )}

                    {/* ✅ FIXED: Render Charts from object */}
                    {m.charts && typeof m.charts === 'object' && Object.keys(m.charts).length > 0 && (
                      <div className="mt-4 space-y-4 bg-white p-4 rounded-lg border border-gray-200">
                        <div className="flex items-center text-sm font-medium text-gray-700 mb-2">
                          📊 Data Visualization
                        </div>
                        {Object.entries(m.charts).map(([key, chartData]) => (
                          <div key={key} className="bg-gray-50 p-4 rounded-lg">
                            {renderChart(key, chartData)}
                          </div>
                        ))}
                      </div>
                    )}

                    {m.role === "assistant" && m.context_used && (
                      <p className="mt-1 text-xs text-primary-600">
                        ✨ Used knowledge base
                      </p>
                    )}
                    {m.role === "assistant" &&
                      m.sources &&
                      m.sources.length > 0 && (
                        <div className="mt-3 border-t border-gray-200 pt-2 text-xs">
                          <p className="text-gray-600 mb-1">📄 Sources:</p>
                          {m.sources.slice(0, 2).map((src, i) => (
                            <div
                              key={i}
                              className="text-gray-500 bg-gray-50 p-2 rounded mb-1"
                            >
                              <div className="font-medium">{src.filename}</div>
                              {src.similarity_score && (
                                <div className="text-primary-600">
                                  {Math.round(src.similarity_score * 100)}% match
                                </div>
                              )}
                            </div>
                          ))}
                        </div>
                      )}
                  </div>
                </div>
              ))}
              {loading && (
                <div className="flex justify-start">
                  <div className="bg-gray-100 px-4 py-3 rounded-2xl">
                    <LoadingSpinner size="small" />
                  </div>
                </div>
              )}
            </>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <form onSubmit={sendMessage} className="border-t border-gray-200 p-3 bg-gray-50 flex gap-2">
          <input
            type="text"
            value={currentMessage}
            onChange={(e) => setCurrentMessage(e.target.value)}
            placeholder={
              chatMode === "rag"
                ? "Ask about your documents or request charts..."
                : "Type your message..."
            }
            className="flex-1 input-field bg-white rounded-lg px-4 py-2"
            disabled={loading}
            autoFocus
          />
          <button
            type="submit"
            disabled={loading || !currentMessage.trim()}
            className="btn-primary px-4 rounded-lg"
          >
            {loading ? <LoadingSpinner size="small" color="white" /> : "🚀"}
          </button>
        </form>
      </div>
    </div>
  );
}

export default Chat;
