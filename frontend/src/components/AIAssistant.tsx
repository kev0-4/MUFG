import type { Dispatch, SetStateAction } from "react";
import type { ChatMessage, QueryData } from "../types";

interface AIAssistantProps {
  userId: string;
  queryText: string;
  setQueryText: Dispatch<SetStateAction<string>>;
  chatMessages: ChatMessage[];
  setChatMessages: Dispatch<SetStateAction<ChatMessage[]>>;
  callEndpoint: (endpoint: string, method: string, data?: any) => Promise<any>;
  callGeminiAPI: (query: string) => Promise<any>;
}

const AIAssistant = ({
  userId,
  queryText,
  setQueryText,
  chatMessages,
  setChatMessages,
  callEndpoint,
  callGeminiAPI,
}: AIAssistantProps) => {
  const handleChatSubmit = async () => {
    if (!queryText) return;
    setChatMessages([...chatMessages, { sender: "user", text: queryText }]);

    const queryData = await callEndpoint("query", "POST", {
      user_id: userId,
      query: queryText,
    });
    if (queryData) {
      setChatMessages((prev) => [
        ...prev,
        {
          sender: "assistant",
          text: `Query analysis: Intent=${queryData.intent}, Sentiment=${queryData.query_sentiment.label} (${queryData.query_sentiment.score})`,
        },
      ]);
    }

    const geminiResponse = await callGeminiAPI(queryText);
    if (geminiResponse) {
      setChatMessages((prev) => [
        ...prev,
        { sender: "assistant", text: geminiResponse.content },
      ]);
    }
    setQueryText("");
  };

  return (
    <div className="bg-gray-800 rounded-xl border border-gray-700 flex flex-col h-full">
      <div className="p-6 border-b border-gray-700">
        <h2 className="text-xl font-bold mb-1">AI Financial Assistant</h2>
        <p className="text-gray-400 text-sm">Ask me anything about finance</p>
      </div>
      <div className="flex-1 p-4 overflow-y-auto flex flex-col space-y-4">
        {chatMessages.map((msg, i) => (
          <div
            key={i}
            className={`flex items-start ${
              msg.sender === "user" ? "justify-end" : ""
            }`}
          >
            <div
              className={`w-8 h-8 rounded-full ${
                msg.sender === "user" ? "bg-gray-700" : "bg-primary-500/20"
              } flex-shrink-0 flex items-center justify-center ${
                msg.sender === "user" ? "ml-2" : "mr-2"
              }`}
            >
              <span
                className={`material-symbols-outlined ${
                  msg.sender === "user" ? "text-gray-400" : "text-primary-400"
                }`}
              >
                {msg.sender === "user" ? "person" : "smart_toy"}
              </span>
            </div>
            <div
              className={`bg-${
                msg.sender === "user" ? "primary-500/20" : "gray-700/50"
              } rounded-lg ${
                msg.sender === "user" ? "rounded-tr-none" : "rounded-tl-none"
              } p-3 text-sm max-w-[70%]`}
            >
              {msg.text}
            </div>
          </div>
        ))}
      </div>
      <div className="p-4 border-t border-gray-700">
        <div className="relative">
          <input
            type="text"
            placeholder="Ask a question..."
            value={queryText}
            onChange={(e) => setQueryText(e.target.value)}
            onKeyPress={(e) => e.key === "Enter" && handleChatSubmit()}
            className="w-full bg-gray-700 rounded-full py-3 pl-4 pr-12 focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
          <button
            onClick={handleChatSubmit}
            className="absolute right-2 top-2 w-8 h-8 bg-primary-500 rounded-full flex items-center justify-center hover:bg-primary-600 transition-colors"
          >
            <span className="material-symbols-outlined text-white">send</span>
          </button>
        </div>
        <div className="flex justify-between mt-2 px-2 text-xs text-gray-400">
          <span>Powered by FinGuard & Gemini API</span>
          <button
            onClick={() =>
              setChatMessages([
                {
                  sender: "assistant",
                  text: "Hello! I'm your financial assistant. How can I help you today?",
                },
              ])
            }
            className="hover:text-gray-300 transition-colors"
          >
            Clear conversation
          </button>
        </div>
      </div>
    </div>
  );
};

export default AIAssistant;
