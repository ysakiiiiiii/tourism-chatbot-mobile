import { Menu, Bell } from 'lucide-react'

function Header() {
  return (
    <nav className="bg-white font-poppins p-3 md:p-4 flex justify-between items-center border-b border-gray-200 rounded-t-3xl">
      
      {/* Left Section */}
      <div className='flex items-center gap-2 md:gap-3'>
        <button 
          className='p-2 hover:bg-gray-100 rounded-lg transition-colors'
          aria-label="Open menu"
        >
          <Menu className='text-black' size={20} />
        </button>
        
        <h1 className='text-lg md:text-xl font-extrabold tracking-wide'>
          <span className='text-[#ab1cd8]'>Loca</span>
          <span className='text-[#ff5b6f]'>Tour</span>
        </h1>
      </div>

      {/* Right Section */}
      <button 
        className='p-2 hover:bg-gray-100 rounded-lg transition-colors'
        aria-label="View notifications"
      >
        <Bell className='text-black' size={20} />
      </button>
    </nav>
  )
}

export default Header