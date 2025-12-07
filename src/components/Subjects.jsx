import { useState, useEffect } from 'react';
import BottomNav from './BottomNav';
import './Subjects.css';

function Subjects({ onSubjectSelect }) {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetch('/db/subjects-db.json')
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
            <div className="subjects-view">
                <div className="loading-spinner">Loading...</div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="subjects-view">
                <div className="error-message">Error: {error}</div>
            </div>
        );
    }

    if (!data || !data.standards) {
        return (
            <div className="subjects-view">
                <div className="error-message">No subjects available</div>
            </div>
        );
    }

    return (
        <div className="subjects-view">
            <div className="subjects-list">
                {data.standards.map((standard) => (
                    standard.subjects.map((subject) => (
                        <div
                            key={`${standard.standard}-${subject.subjectName}`}
                            className="subject-item"
                            onClick={() => onSubjectSelect(standard.standard, subject.subjectName)}
                        >
                            <div className="subject-header-item">
                                <span className="subject-expand-icon">›</span>
                                <span className="subject-label">
                                    {standard.standard}. {subject.subjectName}
                                </span>
                            </div>
                        </div>
                    ))
                ))}
            </div>

            <BottomNav />
        </div>
    );
}

export default Subjects;
