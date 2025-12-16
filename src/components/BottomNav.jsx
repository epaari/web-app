import './BottomNav.css';

function BottomNav({ classNum, subject, chapterNo, chapterTitle, viewMode, hasTextBook, onViewModeChange, onNavigateToChapters, onHome }) {
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

            {viewMode && onViewModeChange && (
                <div className="view-mode-toggles">
                    <button
                        className={`toggle-btn ${viewMode === 'teaching' ? 'active' : ''}`}
                        onClick={() => onViewModeChange('teaching')}
                    >
                        Teaching
                    </button>
                    <button
                        className={`toggle-btn ${viewMode === 'book-qa' ? 'active' : ''}`}
                        onClick={() => onViewModeChange('book-qa')}
                    >
                        Book QA
                    </button>
                    <button
                        className={`toggle-btn ${viewMode === 'board-qa' ? 'active' : ''}`}
                        onClick={() => onViewModeChange('board-qa')}
                    >
                        Board QA
                    </button>
                    <button
                        className={`toggle-btn ${viewMode === 'bonus-qa' ? 'active' : ''}`}
                        onClick={() => onViewModeChange('bonus-qa')}
                    >
                        Bonus QA
                    </button>
                    <button
                        className={`toggle-btn ${viewMode === 'pop-quiz' ? 'active' : ''}`}
                        onClick={() => onViewModeChange('pop-quiz')}
                    >
                        Pop Quiz
                    </button>
                    <button
                        className={`toggle-btn ${viewMode === 'deep-quiz' ? 'active' : ''}`}
                        onClick={() => onViewModeChange('deep-quiz')}
                    >
                        Deep Quiz
                    </button>
                    <button
                        className={`toggle-btn ${viewMode === 'q-gen' ? 'active' : ''}`}
                        onClick={() => onViewModeChange('q-gen')}
                    >
                        Q-Gen
                    </button>
                    {/* Text Book Button - Only if hasTextBook is true */}
                    {hasTextBook && (
                        <button
                            className={`toggle-btn ${viewMode === 'text-book' ? 'active' : ''}`}
                            onClick={() => onViewModeChange('text-book')}
                        >
                            Text Book
                        </button>
                    )}
                </div>
            )}
        </nav>
    );
}

export default BottomNav;
