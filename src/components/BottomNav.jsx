import './BottomNav.css';
import homeIcon from '../assets/home_icon.png';

function BottomNav({ classNum, subject, chapterNo, chapterTitle, onNavigateToChapters }) {
    return (
        <nav className="bottom-nav">
            <div className="nav-home">
                <img src={homeIcon} alt="Home" className="home-icon" />
            </div>
            <div className="nav-breadcrumbs">
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
