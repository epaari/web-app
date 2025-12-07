import './BottomNav.css';

function BottomNav({ classNum, subject, chapterNo, chapterTitle, onNavigateToChapters, onHome }) {
    return (
        <nav className="bottom-nav">
            <div className="nav-breadcrumbs">
                {onHome ? (
                    <button className="nav-btn nav-btn-clickable" onClick={onHome}>Home</button>
                ) : (
                    <button className="nav-btn">Home</button>
                )}
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
                ) : classNum && subject ? (
                    <button className="nav-btn">{classNum}. {subject}</button>
                ) : null}
            </div>
        </nav>
    );
}

export default BottomNav;
