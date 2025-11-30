import { useState } from 'react'
import './App.css'
import Chatwindow from './Components/Chatwindow'

function App() {
  return(
    <div className='bg-linear-to-br from-gray-50 to-gray-100 min-h-screen flex items-center justify-center p-4'>
      {/* Chatbot Container - ChatGPT Style */}
      <div className='w-full md:max-w-3xl lg:max-w-4xl rounded-2xl md:rounded-3xl overflow-hidden shadow-2xl bg-white'>
        <Chatwindow />
      </div>
    </div>
  )
}

export default App