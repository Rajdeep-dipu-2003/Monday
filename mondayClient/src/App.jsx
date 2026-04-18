import { HashRouter, Routes, Route } from "react-router-dom";
import { Toaster } from "react-hot-toast";
import Layout from "./Layouts/Layout";

import Home from "./Pages/Home"
import Create from "./Pages/Create"
import Chat from "./Pages/Chat"

import './App.css'

function App() {
  return (
    <>
      <HashRouter>
        <Toaster position="top-right" />
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<Home />} />
            <Route path="create" element={<Create />} />
            <Route path="chat" element={<Chat />} />
          </Route>
        </Routes>
      </HashRouter>
    </>
  )
}

export default App
