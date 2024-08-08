import React from 'react'

const ResumeBlockLoading = () => {
    return (
        <div className="bg-white p-4 rounded-xl shadow-md w-64 h-64 col-span-1">
            <div className="flex flex-col justify-evenly items-center gap-y-6 w-full h-full">
                <div className="rounded-lg w-4/5 h-12 bg-gray-300 animate-pulse self-start" />
                <div className="bg-gray-300 animate-pulse rounded-lg h-8 w-3/5" />
                <div className="flex flex-row justify-center items-center gap-x-12 w-full h-12">
                    <div className="w-2/5 h-full bg-gray-300 rounded-full animate-pulse" />
                    <div className="w-2/5 h-full bg-gray-300 rounded-full animate-pulse" />
                </div>
            </div>
        </div>
    )
}

export default ResumeBlockLoading