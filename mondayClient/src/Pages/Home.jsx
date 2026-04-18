import { useNavigate } from "react-router-dom";

function Home() {
    const navigate = useNavigate();

    return (
        <div className="h-screen bg-gray-50 text-gray-900 flex flex-col items-center justify-center">
            
            {/* Title */}
            <h1 className="text-4xl font-bold mb-12 tracking-tight">
                Monday
            </h1>

            {/* Options */}
            <div className="flex gap-8">
                
                {/* Create RAG */}
                <div
                    onClick={() => navigate("/create")}
                    className="w-72 h-44 bg-white rounded-2xl p-6 cursor-pointer 
                               border border-gray-200
                               hover:shadow-xl hover:-translate-y-1
                               transition-all duration-300 
                               flex flex-col justify-center items-center text-center"
                >
                    <h2 className="text-xl font-semibold mb-2">
                        Build Custom RAG
                    </h2>
                    <p className="text-sm text-gray-500">
                        Create and train your own retrieval-augmented model
                    </p>
                </div>

                {/* Chat */}
                <div
                    onClick={() => navigate("/chat")}
                    className="w-72 h-44 bg-white rounded-2xl p-6 cursor-pointer 
                               border border-gray-200
                               hover:shadow-xl hover:-translate-y-1
                               transition-all duration-300 
                               flex flex-col justify-center items-center text-center"
                >
                    <h2 className="text-xl font-semibold mb-2">
                        Chat with Models
                    </h2>
                    <p className="text-sm text-gray-500">
                        Interact with your existing RAG models
                    </p>
                </div>

            </div>
        </div>
    );
}

export default Home;