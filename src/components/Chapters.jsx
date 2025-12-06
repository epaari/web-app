import { useState, useEffect } from 'react';
import BottomNav from './BottomNav';
import './Chapters.css';

function Chapters({ onChapterSelect }) {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetch('/db/db.json')
            .then((response) => {
                if (!response.ok) {
                    throw new Error('Failed to fetch data');
                }
                return response.json();
            })
            .then((data) => {
                setData(data);
                setLoading(false);
            })
            .catch((err) => {
                setError(err.message);
                setLoading(false);
            });
    }, []);

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
                <div className="error-message">Error: {error}</div>
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
            <div className="chapters-header">
                <h1 className="chapters-title">Chapters</h1>
                <p className="chapters-subtitle">Class {data.class} - {data.subject}</p>
            </div>

            <div className="chapters-list">
                {data.chapters.map((chapter) => (
                    <div
                        key={chapter.chapterNo}
                        className="chapter-card"
                        onClick={() => onChapterSelect(chapter)}
                    >
                        <div className="chapter-number">{chapter.chapterNo}</div>
                        <div className="chapter-info">
                            <h2 className="chapter-title">{chapter.chapterTitle}</h2>
                            <p className="chapter-meta">
                                {chapter.nodes.length} topic{chapter.nodes.length !== 1 ? 's' : ''}
                            </p>
                        </div>
                        <div className="chapter-arrow">›</div>
                    </div>
                ))}
            </div>

            <BottomNav
                classNum={data.class}
                subject={data.subject}
            />
        </div>
    );
}

export default Chapters;
