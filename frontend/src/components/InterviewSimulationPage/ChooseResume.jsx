import { useState, useEffect } from 'react'
import ResumeBlock from './ResumeBlock'
import RedirectToCreateResumeBlock from './RedirectToCreateResumeBlock';

const ChooseResume = ({ resumeIdList, userPhoneNumber, onSelectedResumeChange }) => {
    const itemsPerPage = 3;
    const [cards, setCards] = useState([]);
    const [page, setPage] = useState(1);
    const [idsToShow, setIdsToShow] = useState([]);

    useEffect(() => {
        console.log("resumeIdList changed");
        setCards(resumeIdList);
    }, [resumeIdList]);

    useEffect(() => {
        const start = (page - 1) * itemsPerPage;
        const end = start + itemsPerPage;
        const idsToLoad = cards
            .slice(start, end)
            .filter((id) => !idsToShow.includes(id));
        setIdsToShow((prevIds) => [...prevIds, ...idsToLoad]);
    }, [page, cards]);

    const loadMore = () => {
        setPage((prevPage) => prevPage + 1);
    };

    const handleDelete = (id) => {
        setIdsToShow((prevIds) => prevIds.filter((cardId) => cardId !== id));
        setCards((prevCards) => prevCards.filter((cardId) => cardId !== id));
    };

    const [selectedId, setSelectedId] = useState();
    const handleResumeIdChange = (id) => {
        onSelectedResumeChange(id);
        setSelectedId(id);
    }

    return (
        <>
            <div className='text-2xl ml-16 my-8 font-semibold text-alpha-blue'>选择简历</div>
            {
                cards.length ?
                    <>
                        <div className='grid grid-cols-3 gap-y-12'>
                            {idsToShow.map((id) => (
                                <div className='flex justify-center'>
                                    <ResumeBlock
                                        key={id}
                                        resumeId={id}
                                        userPhoneNumber={userPhoneNumber}
                                        deletefromCards={handleDelete}
                                        onResumeIdChange={handleResumeIdChange}
                                        selectedId={selectedId}
                                    />
                                </div>
                            ))}
                        </div>
                        <div className='flex justify-center mt-3'>
                            {idsToShow.length < cards.length && (
                                <button className='text-lg' onClick={loadMore}>
                                    加载更多
                                </button>
                            )}
                        </div>
                    </>
                    :
                    <div className='pl-16'>
                        <RedirectToCreateResumeBlock />
                    </div>
            }

        </>
    )
}

export default ChooseResume