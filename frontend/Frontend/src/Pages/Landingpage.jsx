import { motion } from "motion/react"
import { FaRobot, FaMap, FaUtensils, FaClock, FaArrowRight } from "react-icons/fa"
import { useState } from "react"
import { useNavigate } from "react-router-dom"

function Landingpage(){
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const navigate = useNavigate()

  const handleStartChat = () => {
    navigate('/chat')
  }

  return(
    <>
      <div className="flex flex-col flex-1 bg-[#f7f7f7] w-full min-h-screen">
        
        {/* NAVBAR */}
        <header className="font-poppins w-full h-auto bg-white shadow-sm sticky top-0 z-50">
          <div className="flex items-center justify-between px-6 py-4">
            <h1 className="font-bold text-2xl">
              <span className="text-[#AB1CD8]">LOCA</span>
              <span className="text-[#FF5B6F]">TOUR</span>
            </h1>

            <motion.button 
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={handleStartChat}
              className="bg-gradient-to-r from-[#AB1CD8] to-[#FF5B6F] text-white px-6 py-2 rounded-full font-semibold hidden md:block cursor-pointer transition-all duration-500"
            >
              Start Chat
            </motion.button>

            {/* MOBILE MENU BUTTON */}
            <button 
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="md:hidden text-2xl text-[#AB1CD8]"
            >
              ☰
            </button>
          </div>

          {/* MOBILE MENU */}
          {isMenuOpen && (
            <motion.div 
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              className="md:hidden bg-white border-t p-4 space-y-3"
            >
              <motion.button 
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={handleStartChat}
                className="w-full bg-gradient-to-r from-[#AB1CD8] to-[#FF5B6F] text-white py-2 rounded-full font-semibold cursor-pointer transition-all duration-500"
              >
                Start Chat
              </motion.button>
            </motion.div>
          )}
        </header>

        {/* HERO SECTION */}
        <motion.section 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 1.2, ease: "easeInOut" }}
          className="flex-1 flex flex-col items-center justify-center px-6 py-20 text-center"
        >
          <motion.div
            initial={{ y: 40, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.3, duration: 1, ease: "easeInOut" }}
          >
            <h2 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6">
              Discover <span className="bg-gradient-to-r from-[#AB1CD8] to-[#FF5B6F] bg-clip-text text-transparent">Ilocos</span>
            </h2>
            <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
              Your AI-powered travel companion exploring the rich history, culture, and beauty of Ilocos Region
            </p>
          </motion.div>

          <motion.div 
            initial={{ y: 40, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.6, duration: 1, ease: "easeInOut" }}
            className="flex flex-col md:flex-row gap-4"
          >
            <motion.button 
              whileHover={{ scale: 1.08 }}
              whileTap={{ scale: 0.92 }}
              onClick={handleStartChat}
              className="bg-gradient-to-r from-[#AB1CD8] to-[#FF5B6F] text-white px-8 py-3 rounded-full font-semibold flex items-center gap-2 justify-center cursor-pointer transition-all duration-500"
            >
              Start Exploring <FaArrowRight />
            </motion.button>
          </motion.div>

        </motion.section>

        {/* FEATURES SECTION */}
        <section id="features" className="bg-white py-20 px-6">
          <div className="max-w-6xl mx-auto">
            <motion.h2 
              initial={{ y: 30, opacity: 0 }}
              whileInView={{ y: 0, opacity: 1 }}
              transition={{ duration: 0.8, ease: "easeInOut" }}
              viewport={{ once: true, amount: 0.3 }}
              className="text-4xl font-bold text-center mb-12 text-gray-900"
            >
              Why Choose <span className="text-[#AB1CD8]">LOCA</span><span className="text-[#FF5B6F]">TOUR</span>
            </motion.h2>

            <div className="grid md:grid-cols-4 gap-8">
              {[
                { icon: FaRobot, title: "AI Chatbot", desc: "Smart recommendations powered by advanced AI" },
                { icon: FaMap, title: "Route Planning", desc: "Optimal travel routes and directions" },
                { icon: FaUtensils, title: "Local Cuisine", desc: "Discover authentic Ilocos delicacies" },
                { icon: FaClock, title: "24/7 Support", desc: "Always available when you need help" }
              ].map((feature, i) => (
                <motion.div
                  key={i}
                  initial={{ y: 40, opacity: 0 }}
                  whileInView={{ y: 0, opacity: 1 }}
                  transition={{ delay: i * 0.2, duration: 0.8, ease: "easeInOut" }}
                  viewport={{ once: true, amount: 0.3 }}
                  className="bg-gradient-to-br from-[#f7f7f7] to-white p-8 rounded-xl shadow-sm hover:shadow-lg transition-all duration-500 text-center"
                >
                  <feature.icon className="text-5xl text-[#AB1CD8] mx-auto mb-4" />
                  <h3 className="font-bold text-lg mb-2 text-gray-900">{feature.title}</h3>
                  <p className="text-gray-600">{feature.desc}</p>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        {/* CTA SECTION */}
        <section className="bg-gradient-to-r from-[#AB1CD8] to-[#FF5B6F] py-16 px-6 text-white text-center">
          <motion.div
            initial={{ y: 30, opacity: 0 }}
            whileInView={{ y: 0, opacity: 1 }}
            transition={{ duration: 0.8, ease: "easeInOut" }}
            viewport={{ once: true, amount: 0.3 }}
          >
            <h2 className="text-4xl font-bold mb-4">Ready to Explore Ilocos?</h2>
            <p className="text-lg mb-8 opacity-90">Chat with our AI assistant now and start your journey</p>
            <motion.button 
              whileHover={{ scale: 1.08 }}
              whileTap={{ scale: 0.92 }}
              onClick={handleStartChat}
              className="bg-white text-[#AB1CD8] px-8 py-3 rounded-full font-bold text-lg hover:bg-gray-100 transition-all duration-500 cursor-pointer"
            >
              Start Chatting Now →
            </motion.button>
          </motion.div>
        </section>

        {/* FOOTER */}
        <footer className="bg-gray-900 text-white py-8 px-6">
          <div className="max-w-6xl mx-auto text-center">
            <h3 className="text-2xl font-bold mb-4">
              <span className="text-[#AB1CD8]">LOCA</span>
              <span className="text-[#FF5B6F]">TOUR</span>
            </h3>
            <p className="mb-4 opacity-75">Discover Ilocos with AI-powered travel guidance</p>
            <div className="flex gap-6 justify-center text-sm mb-6">
              <a href="#" className="hover:text-[#AB1CD8] transition duration-500">Privacy Policy</a>
              <a href="#" className="hover:text-[#FF5B6F] transition duration-500">Terms of Service</a>
              <a href="#" className="hover:text-[#AB1CD8] transition duration-500">Contact Us</a>
            </div>
            <p className="opacity-50">&copy; 2025 LOCATOUR. All rights reserved.</p>
          </div>
        </footer>

      </div>
    </>
  )
}

export default Landingpage