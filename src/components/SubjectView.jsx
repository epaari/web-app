import { useState, useEffect } from 'react';
import BottomNav from './BottomNav';
import './SubjectView.css';

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

function SubjectView({ onSubjectSelect }) {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const checkSubjectAvailability = async (standard, subject) => {
            try {
                const subjectSlug = subject.toLowerCase().replace(/\s+/g, '-');
                const dbPath = `/db/${standard}-${subjectSlug}/concept.json`;
                const res = await fetch(dbPath);
                if (!res.ok) return false;
                const data = await res.json();
                return data.chapters && data.chapters.length > 0;
            } catch (e) {
                return false;
            }
        };

        fetch('/db/subjects.json')
            .then((response) => {
                if (!response.ok) {
                    throw new Error('Failed to fetch data');
                }
                return response.json();
            })
            .then(async (data) => {
                if (data && data.publishers && data.publishers[0] && data.publishers[0].standards) {
                    const standards = data.publishers[0].standards;

                    // Process standards concurrently
                    await Promise.all(standards.map(async (std) => {
                        const validSubjects = [];
                        // Process subjects concurrently
                        await Promise.all(std.subjects.map(async (sub) => {
                            const isValid = await checkSubjectAvailability(std.standardName, sub.subjectName);
                            if (isValid) {
                                validSubjects.push(sub);
                            }
                        }));
                        // Replace subjects with filtered list
                        std.subjects = validSubjects;
                    }));
                }
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
                    .map((standard, index) => {
                        if (standard.subjects.length === 0) return null;
                        return (
                            <div key={standard.id} className="standard-group">
                                <h2 className="standard-label">
                                    <span>{standard.standardName}<sup>th</sup> Standard</span>
                                </h2 >
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
                            </div >
                        );
                    })}
            </div>

            <BottomNav />
        </div>
    );
}

export default SubjectView;
