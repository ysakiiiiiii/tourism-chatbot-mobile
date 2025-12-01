import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Landingpage from './pages/LandingPage'
import ChatPage from './pages/ChatPage'
import './App.css'

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Landingpage />} />
        <Route path="/chat" element={<ChatPage />} />
      </Routes>
    </Router>
  )
}

export default App