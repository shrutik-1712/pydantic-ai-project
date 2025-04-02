import React from 'react'
import { BrowserRouter, Route, Routes } from 'react-router-dom'
import UrlInputPage from './Pages/UrlInputPage'
import ChatPage from './Pages/ChatPage'

const Home = () => {
  return (
    <>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<UrlInputPage />} />
        <Route path="/chat" element={<ChatPage />} />
      </Routes>
    </BrowserRouter>
    </>
  )
}

export default Home