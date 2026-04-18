import { useState } from "react";

function Chat() {
    const [models, setModels] = useState([
        { name: "llama3", provider: "ollama" },
        { name: "mistral", provider: "ollama" },
    ]); // TODO: fetch from API

    const [selectedModel, setSelectedModel] = useState(null);
    const [search, setSearch] = useState("");
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState("");
    const [showHistory, setShowHistory] = useState(true);

    // Filter models
    const filteredModels = models.filter((m) =>
        m.name.toLowerCase().includes(search.toLowerCase())
    );

    // Send message
    const handleSend = async () => {
        if (!input || !selectedModel) return;

        const userMessage = { role: "user", content: input };

        setMessages((prev) => [...prev, userMessage]);
        setInput("");

        try {
            // 🚀 API CALL HERE (RAG Chat)
            // const res = await fetch("/api/chat", {...})

            const fakeResponse = {
                role: "assistant",
                content: "This is a mock response from the model.",
            };

            setMessages((prev) => [...prev, fakeResponse]);
        } catch (err) {
            console.error(err);
        }
    };

    return (
        <div className="w-screen h-screen flex bg-gray-50 text-gray-900 m-0 p-0">
            {/* LEFT SIDEBAR */}
            <div className="w-64 border-r bg-white p-4 flex flex-col">
                <h2 className="font-semibold mb-4">Models</h2>

                {/* Search */}
                <input
                    type="text"
                    placeholder="Search models..."
                    className="border border-gray-300 rounded-lg p-2 mb-4"
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                />

                {/* Model list */}
                <div className="flex-1 overflow-y-auto space-y-2">
                    {filteredModels.map((m, index) => (
                        <div
                            key={index}
                            onClick={() => {
                                setSelectedModel(m);
                                setMessages([]); // reset chat
                            }}
                            className={`p-2 rounded-lg cursor-pointer ${selectedModel?.name === m.name
                                    ? "bg-gray-200"
                                    : "hover:bg-gray-100"
                                }`}
                        >
                            {m.name}
                        </div>
                    ))}
                </div>
            </div>

            {/* CENTER CHAT */}
            <div className="flex-1 flex flex-col">

                {/* Header */}
                <div className="border-b bg-white p-4 flex justify-between items-center">
                    <h2 className="font-semibold">
                        {selectedModel
                            ? `Chat - ${selectedModel.name}`
                            : "Select a model"}
                    </h2>

                    <button
                        onClick={() => setShowHistory((prev) => !prev)}
                        className="text-sm text-gray-600 hover:text-gray-900"
                    >
                        {showHistory ? "Hide History" : "Show History"}
                    </button>
                </div>

                {/* Messages */}
                <div className="flex-1 overflow-y-auto p-4 space-y-4">
                    {messages.map((msg, index) => (
                        <div
                            key={index}
                            className={`max-w-xl p-3 rounded-lg ${msg.role === "user"
                                    ? "bg-gray-900 text-white ml-auto"
                                    : "bg-gray-200"
                                }`}
                        >
                            {msg.content}
                        </div>
                    ))}
                </div>

                {/* Input */}
                <div className="border-t bg-white p-4 flex gap-2">
                    <input
                        type="text"
                        className="flex-1 border border-gray-300 rounded-lg p-2"
                        placeholder="Type your message..."
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={(e) => {
                            if (e.key === "Enter") handleSend();
                        }}
                    />

                    <button
                        onClick={handleSend}
                        className="bg-gray-900 text-white px-4 rounded-lg hover:bg-gray-800"
                    >
                        Send
                    </button>
                </div>
            </div>

            {/* RIGHT SIDEBAR (HISTORY) */}
            {showHistory && (
                <div className="w-64 border-l bg-white p-4">
                    <h2 className="font-semibold mb-4">Chat History</h2>

                    {/* TODO: Fetch history based on selected model */}

                    <div className="space-y-2 text-sm text-gray-600">
                        <div className="p-2 bg-gray-100 rounded">
                            Previous chat 1
                        </div>
                        <div className="p-2 bg-gray-100 rounded">
                            Previous chat 2
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

export default Chat;