import React, { useState, useEffect, useRef } from "react";
import { useRouter } from "next/router";
import Image from "next/image";
import Link from "next/link";
import ResumeBlockLoading from "./ResumeBlockLoading";
import { formatDateToLocalTime } from "@/utils/timeRelated";

const fetchRecordById = async (id) => {
    const response = await fetch(
        process.env.NEXT_PUBLIC_API_URL + `/api/improved-users/${id}/meta-data`,
        {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
            },
        }
    );
    const rawData = await response.json();
    return {
        _id: rawData._id,
        resumeHistoryId: rawData.resumeId,
        page: rawData.page,
        title: rawData.title,
        updateTime: rawData.updatedAt,
    };
};

const ResumeBlock = ({ resumeId, userPhoneNumber, deletefromCards, onResumeIdChange, selectedId }) => {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const router = useRouter();
    const [showConfirm, setShowConfirm] = useState(false);
    const [menuVisible, setMenuVisible] = useState(false);
    const menuRef = useRef();

    useEffect(() => {
        const loadRecord = async () => {
            const record = await fetchRecordById(resumeId);
            setData(record);
            setLoading(false);
        };

        loadRecord();
    }, [resumeId]);

    const confirmDelete = () => {
        setShowConfirm(true);
    };

    const toggleMenu = () => {
        setMenuVisible(!menuVisible);
    };

    const handleClickOutside = (event) => {
        if (menuRef.current && !menuRef.current.contains(event.target)) {
            setMenuVisible(false);
        }
    };

    useEffect(() => {
        document.addEventListener("mousedown", handleClickOutside);
        return () => {
            document.removeEventListener("mousedown", handleClickOutside);
        };
    }, []);

    const handleClick = () => {
        // 使用写死的 ID 进行路由跳转
        router.push(`/resume/fill-info-step1?id=${resumeId}`);
    };

    const handleDelete = () => {
        fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/improved-users`, {
            method: "DELETE",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                phoneNumber: userPhoneNumber,
                improvedUserId: resumeId,
            }),
        })
            .then((response) => {
                if (!response.ok) {
                    throw new Error("Network response was not ok");
                }
                setShowConfirm(false); // 关闭确认框
                return response.json();
            })
            .then((data) => {
                console.log("Delete successful:", data);
                deletefromCards(resumeId);
            })
            .catch((error) => {
                console.error("Delete error:", error);
            });
    };

    const handleResumeSelect = () => {
        onResumeIdChange(resumeId);
    }

    if (loading) return <ResumeBlockLoading />;

    return (
        <div className='flex flex-col w-64 h-64 rounded-xl shadow-md border'>

            <div className='absolute self-end pt-5 pr-5'>
                <button onClick={toggleMenu}>
                    <Image src="/img/more.svg" alt="更多" width={20} height={20} />
                </button>
                {menuVisible && (
                    <div
                        className="flex flex-col rounded-lg shadow-md absolute bg-white border border-alpha-blue z-50"
                        ref={menuRef}
                    >
                        <ul>
                            <li key="edit">
                                <button
                                    className="px-8 py-2 border-b border-alpha-blue whitespace-nowrap text-base text-black font-normal"
                                    onClick={handleClick}
                                >
                                    编辑
                                </button>
                            </li>
                            <li key="view">
                                {" "}
                                <button
                                    className="px-8 py-2 border-b border-alpha-blue whitespace-nowrap text-base text-black font-normal"
                                    onClick={() =>
                                        handleClick("f0c086b6-1c3b-4e87-b39e-39e7d4392b1b")
                                    }
                                >
                                    预览
                                </button>
                            </li>
                            <li key="delete">
                                <button
                                    className="px-8 py-2 whitespace-nowrap text-base text-black font-normal"
                                    onClick={confirmDelete}
                                >
                                    删除
                                </button>
                            </li>
                        </ul>
                    </div>
                )}
            </div>

            <div className='flex-grow'>
                <div className='text-2xl px-6 pt-12'>{data.title ? data.title : "测试简历"}</div>
                <div className='text-md text-center pt-8 text-gray-500'>上次修改：{formatDateToLocalTime(data.updateTime)}</div>
            </div>
            <div className='flex flex-row justify-center pb-4 gap-x-8 items-center align-bottom'>
                <Link href={`/resume/fill-info-step${data.page}?id=${resumeId}`}>
                    <button className='text-lg font-semibold bg-alpha-blue text-white py-1.5 px-8 rounded-full'>
                        编辑
                    </button>
                </Link>
                {selectedId == resumeId ?
                    <button className='text-lg font-semibold bg-green-500 text-white py-1.5 px-8 rounded-full' onClick={handleResumeSelect} disabled={data.resumeHistoryId === ""}>
                        选择
                    </button>
                    :
                    <button className='text-lg font-semibold bg-alpha-blue text-white py-1.5 px-8 rounded-full' onClick={handleResumeSelect} disabled={data.resumeHistoryId === ""}>
                        选择
                    </button>
                }
            </div>

            {showConfirm && (
                <div className="fixed top-0 left-0 w-full h-full bg-black/40 flex justify-center items-center z-50">
                    <div className="w-[300px] p-5 bg-white rounded-lg flex flex-col items-center gap-y-5">
                        <p className="font-semibold text-lg text-black text-center w-full">
                            是否确认删除简历？
                        </p>
                        <div className="flex flex-row justify-center items-center gap-x-2">
                            <button
                                className="px-8 py-2 rounded-lg bg-red-500 text-white font-normal text-base"
                                onClick={handleDelete}
                            >
                                删除
                            </button>
                            <button
                                className="px-8 py-2 rounded-lg bg-gray-500 text-white font-normal text-base"
                                onClick={() => setShowConfirm(false)}
                            >
                                取消
                            </button>
                        </div>
                    </div>
                </div>
            )}

        </div>

    )
}

export default ResumeBlock