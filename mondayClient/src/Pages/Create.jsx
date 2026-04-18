import { useState, useCallback, useEffect } from "react";
import { Form, useNavigate } from "react-router-dom";
import { useDropzone } from "react-dropzone";
import { toast } from "react-hot-toast";
import axios from "axios"

function Create() {
    const navigate = useNavigate();

    const [name, setName] = useState("");
    const [description, setDescription] = useState("");
    const [model, setModel] = useState({});
    const [models, setModels] = useState([]);
    const [files, setFiles] = useState([]);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        const fetchModels = async () => {
            try {
                const res = await fetch("http://localhost:11434/api/tags");
                const data = await res.json();

                const LLM_FAMILIES = ["llama", "mistral", "qwen", "gemma", "phi"];
                // const LLM_FAMILIES = []

                const filtered = data.models
                    .filter((m) => {
                        const family = m.details?.family?.toLowerCase();
                        return LLM_FAMILIES.includes(family);
                    })
                    .map((m) => m.name);

                const formatted = filtered.map(m => ({
                    name: m,
                    provider: "ollama"
                }));

                setModels(formatted);

                if (formatted.length > 0) {
                    setModel(formatted[0]);
                }

            } catch (err) {
                console.error(err);
            }
        };

        fetchModels();
    }, []);

    // Drag & Drop handler
    const onDrop = useCallback((acceptedFiles) => {
        const pdfFiles = acceptedFiles.filter(
            (file) => file.type === "application/pdf"
        );

        if (pdfFiles.length !== acceptedFiles.length) {
            toast.error("Only PDF files are allowed");
        }

        setFiles((prev) => [...prev, ...pdfFiles]);
    }, []);

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        multiple: true,
    });

    // Remove file
    const removeFile = (index) => {
        const updated = [...files];
        updated.splice(index, 1);
        setFiles(updated);
    };

    // Submit
    const handleSubmit = async () => {
        if (!name || files.length === 0) {
            toast.error("Name and at least one PDF are required");
            return;
        }

        setLoading(true);

        try {
            const formData = new FormData();
            formData.append("name", name);
            formData.append("description", description);
            formData.append("model", model.name);
            formData.append("provider", model.provider)

            files.forEach((file) => {
                formData.append("files", file)
            });

            await axios.post("http://0.0.0.0:8000/api/v1/rag/createrag", formData)
            toast.success("RAG model created successfully!",{
                duration: 5000
            });

            navigate("/");
        } catch (err) {
            console.error(err);
            toast.error("Failed to create RAG model");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gray-50 flex items-center justify-center p-6">
            <div className="w-full max-w-2xl bg-white p-8 rounded-2xl border border-gray-200 shadow-sm">

                <h2 className="text-2xl font-semibold mb-6">
                    Create RAG Model
                </h2>

                {/* Name */}
                <div className="mb-4">
                    <label className="block text-sm mb-1">Name *</label>
                    <input
                        type="text"
                        className="w-full border border-gray-300 rounded-lg p-2 focus:outline-none focus:ring-2 focus:ring-gray-400"
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                    />
                </div>

                {/* Description */}
                <div className="mb-4">
                    <label className="block text-sm mb-1">Description</label>
                    <textarea
                        rows="3"
                        className="w-full border border-gray-300 rounded-lg p-2 focus:outline-none focus:ring-2 focus:ring-gray-400"
                        value={description}
                        onChange={(e) => setDescription(e.target.value)}
                    />
                </div>

                {/* Model */}
                <div className="mb-4">
                    <label className="block text-sm mb-1">Model *</label>

                    {models.length === 0 && (
                        <p className="text-sm text-gray-500 mt-2">
                            No LLM models found. Install one using:
                            <br />
                            <span className="font-mono">ollama pull llama3</span>
                        </p>
                    )}

                    {models.length !== 0 && (<select
                        className="w-full border border-gray-300 rounded-lg p-2"
                        value={model.name}
                        onChange={(e) => setModel(e.target.value)}
                    >
                        {models.map((m, index) => (
                            <option key={index} value={m.name}>
                                {m.name}
                            </option>
                        ))}
                    </select>)}
                </div>

                {/* Drag & Drop Upload */}
                <div className="mb-6">
                    <label className="block text-sm mb-2">
                        Upload PDFs *
                    </label>

                    <div
                        {...getRootProps()}
                        className={`border-2 border-dashed rounded-xl p-6 text-center cursor-pointer transition
                        ${isDragActive ? "bg-gray-100 border-gray-400" : "border-gray-300"}`}
                    >
                        <input {...getInputProps()} />
                        <p className="text-gray-600">
                            {isDragActive
                                ? "Drop files here..."
                                : "Drag & drop PDFs here, or click to select"}
                        </p>
                    </div>

                    {/* File list */}
                    <div className="mt-3 space-y-2">
                        {files.map((file, index) => (
                            <div
                                key={index}
                                className="flex justify-between items-center bg-gray-100 p-2 rounded-lg"
                            >
                                <span className="text-sm truncate">
                                    {file.name}
                                </span>
                                <button
                                    onClick={() => removeFile(index)}
                                    className="text-red-500 text-sm"
                                >
                                    Remove
                                </button>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Submit */}
                <button
                    onClick={handleSubmit}
                    disabled={loading}
                    className={`w-full py-2 rounded-lg transition
                        ${loading
                            ? "bg-gray-400 cursor-not-allowed"
                            : "bg-gray-900 text-white hover:bg-gray-800"
                        }`}
                >
                    {loading ? "Creating..." : "Create"}
                </button>
            </div>
        </div>
    );
}

export default Create;