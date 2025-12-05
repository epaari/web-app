import { useState, useEffect } from 'react';
import TreeNode from './TreeNode';
import './ChapterView.css';

function ChapterView() {
    const [chapterData, setChapterData] = useState(null);
    const [expandedNodeIds, setExpandedNodeIds] = useState(new Set());
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetch('/db/db.json')
            .then((response) => {
                if (!response.ok) {
                    throw new Error('Failed to fetch chapter data');
                }
                return response.json();
            })
            .then((data) => {
                setChapterData(data);
                setLoading(false);
            })
            .catch((err) => {
                setError(err.message);
                setLoading(false);
            });
    }, []);

    const handleNodeClick = (nodeId) => {
        // Toggle: if node is expanded, collapse it; otherwise expand it
        // This allows multiple nodes to be expanded at different levels
        setExpandedNodeIds((prev) => {
            const newSet = new Set(prev);
            if (newSet.has(nodeId)) {
                newSet.delete(nodeId);
            } else {
                newSet.add(nodeId);
            }
            return newSet;
        });
    };

    if (loading) {
        return (
            <div className="chapter-view">
                <div className="loading-spinner">Loading...</div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="chapter-view">
                <div className="error-message">Error: {error}</div>
            </div>
        );
    }

    if (!chapterData) {
        return (
            <div className="chapter-view">
                <div className="error-message">No data available</div>
            </div>
        );
    }

    return (
        <div className="chapter-view">
            <header className="chapter-header">
                <span className="chapter-number">Chapter {chapterData.chapterNo}</span>
                <h1 className="chapter-title">{chapterData.chapterTitle}</h1>
            </header>

            <div className="nodes-container">
                {chapterData.nodes.map((node) => (
                    <TreeNode
                        key={node.id}
                        node={node}
                        expandedNodeIds={expandedNodeIds}
                        onNodeClick={handleNodeClick}
                        depth={0}
                    />
                ))}
            </div>
        </div>
    );
}

export default ChapterView;
