import React from 'react'
import Link from "next/link";

const RedirectToCreateResumeBlock = () => {
    return (
        <div className='flex flex-col w-64 h-64 rounded-xl shadow-md border'>
            <span className='text-lg px-6 mt-12 text-gray-500'>你还没有简历哦，请创建新简历吧~</span>
            <div className='flex justify-center mt-8'>
                <Link href={"start-resumeserve"}>
                    <button className='border border-alpha-blue py-3 px-8 text-2xl text-alpha-blue rounded-full'>
                        创建新简历
                    </button>
                </Link>
            </div>
        </div >
    )
}

export default RedirectToCreateResumeBlock