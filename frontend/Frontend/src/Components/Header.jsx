import { Menu, Bell } from 'lucide-react'

function Header() {
  return (
    <nav className="bg-white font-serif p-4 flex justify-between items-center shadow-lg">
      {/* Navigation Button Mobile */}
      <div className='flex items-center gap-2'>
        <button 
          className='p-2 hover:bg-gray-100 rounded-lg transition-colors'
          aria-label="Open menu"
        >
          <Menu className='text-black' size={24} />
        </button>
        <h1 className='text-xl font-extrabold'>
          <span className='text-[#A020F0]'>Tanaw</span>
          <span className='text-[#00BFFF]'>I</span>
          <span className='text-[#FF00FF]'>N</span>
        </h1>
      </div>

      {/* Notification */}
      <button 
        className='p-2 hover:bg-gray-100 rounded-lg transition-colors'
        aria-label="View notifications"
      >
        <Bell className='text-black' size={24} />
      </button>
    </nav>
  )
}

export default Header