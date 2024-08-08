import React from 'react'

const ProgressSidebar = () => {
  return (
    <div className='flex flex-col w-1/4 bg-alpha-blue items-center'>
      <div className='text-white text-2xl tracking-wider font-bold pt-10'>模拟面试</div>
      <div className='text-white text-xl tracking-wider font-bold pt-10'>1. 完善信息</div>
      <div className='text-white text-xl tracking-wider font-bold pt-10'>2. 面试中</div>
      <div className='text-white text-xl tracking-wider font-bold pt-10'>3. 综合评估</div>
      <div className='text-white text-xl tracking-wider font-bold pt-10'>4. 分区详细评估</div>
    </div>
  )
}

export default ProgressSidebar