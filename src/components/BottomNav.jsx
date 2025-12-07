import './BottomNav.css';

function BottomNav({ classNum, subject, chapterNo, chapterTitle, onNavigateToChapters }) {
    return (
        <nav className="bottom-nav">
            <div className="nav-breadcrumbs">
                <button className="nav-btn">Home</button>
                {chapterNo && chapterTitle ? (
                    <>
                        <button
                            className="nav-btn nav-btn-clickable"
                            onClick={onNavigateToChapters}
                        >
                            {classNum}. {subject}
                        </button>
                        <button className="nav-btn">{chapterNo}. {chapterTitle}</button>
                    </>
                ) : (
                    <button className="nav-btn">{classNum}. {subject}</button>
                )}
            </div>
        </nav>
    );
}

export default BottomNav;
