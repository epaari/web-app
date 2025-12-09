import { useState, useEffect } from 'react';
import BottomNav from './BottomNav';
import './Subjects.css';

// Import subject icons
import tamilIcon from '../assets/subject_icons/Tamil.svg';
import englishIcon from '../assets/subject_icons/English.svg';
import mathsIcon from '../assets/subject_icons/Maths.svg';
import scienceIcon from '../assets/subject_icons/Science.svg';
import socialIcon from '../assets/subject_icons/Social Science.svg';

// Map subject names to their icons
const subjectIcons = {
    'Tamil': tamilIcon,
    'English': englishIcon,
    'Maths': mathsIcon,
    'Science': scienceIcon,
    'Social Science': socialIcon
};

function Subjects({ onSubjectSelect }) {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetch('/db/subjects.json')
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

    if (!data || !data.publishers || !data.publishers[0] || !data.publishers[0].standards) {
        return (
            <div className="subjects-view">
                <div className="error-message">No subjects available</div>
            </div>
        );
    }

    return (
        <div className="subjects-view">
            <div className="subjects-container">
                {data.publishers[0].standards
                    .sort((a, b) => parseInt(a.standardName) - parseInt(b.standardName))
                    .map((standard, index) => (
                        <div key={standard.id} className="standard-group">
                            <h2 className="standard-label">
                                <span>{standard.standardName}<sup>th</sup> Standard</span>
                            </h2>
                            <div className="subjects-grid">
                                {standard.subjects.map((subjectObj) => (
                                    <div
                                        key={subjectObj.id}
                                        className="subject-card"
                                        onClick={() => onSubjectSelect(standard.standardName, subjectObj.subjectName)}
                                    >
                                        <div className="subject-icon-container">
                                            <img
                                                src={subjectIcons[subjectObj.subjectName]}
                                                alt={subjectObj.subjectName}
                                                className="subject-icon"
                                            />
                                        </div>
                                        <div className="subject-name">
                                            {subjectObj.subjectName}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    ))}
            </div>

            <BottomNav />
        </div>
    );
}

export default Subjects;
