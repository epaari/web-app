import './BottomNav.css';
import homeIcon from '../assets/home_icon.png';

function BottomNav({ classNum, subject, chapterNo, chapterTitle }) {
    return (
        <nav className="bottom-nav">
            <div className="nav-home">
                <img src={homeIcon} alt="Home" className="home-icon" />
            </div>
            <div className="nav-breadcrumbs">
                <button className="nav-btn">Class {classNum}</button>
                <button className="nav-btn">{subject}</button>
                <button className="nav-btn">{chapterNo}. {chapterTitle}</button>
            </div>
        </nav>
    );
}

export default BottomNav;
