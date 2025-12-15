import { useState, useEffect } from 'react';
import BottomNav from './BottomNav';
import './ChapterView.css';
import api from '../services/api';

function ChapterView({ standard, subject, viewMode, onViewModeChange, onChapterSelect, onHome }) {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const loadData = async () => {
            try {
                const conceptData = await api.getConcept(standard, subject);
                setData(conceptData);
                setLoading(false);
            } catch (err) {
                setError('Selected subject unavailable');
                setLoading(false);
            }
        };

        loadData();
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
                viewMode={viewMode}
                onViewModeChange={onViewModeChange}
                onHome={onHome}
            />
        </div>
    );
}

export default ChapterView;
