import { useState, useEffect } from 'react';
import BottomNav from './BottomNav';
import './Chapters.css';

function Chapters({ standard, subject, onChapterSelect, onHome }) {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        // Construct the database filename based on standard and subject
        // Convert subject name to lowercase and replace spaces with hyphens
        const subjectSlug = subject.toLowerCase().replace(/\s+/g, '-');
        const dbFileName = `/db/${standard}-${subjectSlug}/concept.json`;

        fetch(dbFileName)
            .then((response) => {
                if (!response.ok) {
                    throw new Error('Selected subject unavailable');
                }
                return response.json();
            })
            .then((data) => {
                setData(data);
                setLoading(false);
            })
            .catch((err) => {
                // Show user-friendly message for any error (404, JSON parse error, etc.)
                setError('Selected subject unavailable');
                setLoading(false);
            });
    }, [standard, subject]);

    if (loading) {
        return (
            <div className="chapters-view">
                <div className="loading-spinner">Loading...</div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="chapters-view">
                <div className="error-modal-overlay" onClick={onHome}>
                    <div className="error-modal" onClick={(e) => e.stopPropagation()}>
                        <h2 className="error-modal-title">Error</h2>
                        <p className="error-modal-message">{error}</p>
                        <button className="error-modal-button" onClick={onHome}>
                            OK
                        </button>
                    </div>
                </div>
            </div>
        );
    }

    if (!data || !data.chapters) {
        return (
            <div className="chapters-view">
                <div className="error-message">No chapters available</div>
            </div>
        );
    }

    return (
        <div className="chapters-view">
            <div className="chapters-list">
                {data.chapters.map((chapter) => (
                    <div
                        key={chapter.chapterNo}
                        className="chapter-item"
                        onClick={() => onChapterSelect(chapter)}
                    >
                        <div className="chapter-header-item">
                            <span className="chapter-label">
                                {chapter.chapterNo}. {chapter.chapterName}
                            </span>
                        </div>
                    </div>
                ))}
            </div>

            <BottomNav
                classNum={standard}
                subject={subject}
                onHome={onHome}
            />
        </div>
    );
}

export default Chapters;
