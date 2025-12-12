import { useState, useEffect, useMemo, useCallback } from 'react';
import ContentView from './ContentView';
import BottomNav from './BottomNav';
import './TopicView.css';

function TopicView({ standard, subject, chapter, onBack, onHome }) {
    const [chapterData, setChapterData] = useState(null);
    const [expandedNodeIds, setExpandedNodeIds] = useState(new Set());
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        // Construct database path based on standard and subject
        const subjectSlug = subject.toLowerCase().replace(/\s+/g, '-');
        const dbPath = `/db/${standard}-${subjectSlug}/concept.json`;

        // Fetch the full data to get class and subject info
        fetch(dbPath)
            .then((response) => {
                if (!response.ok) {
                    throw new Error('Failed to fetch chapter data');
                }
                return response.json();
            })
            .then((data) => {
                // Just use the chapter data directly
                setChapterData(chapter);
                setLoading(false);
            })
            .catch((err) => {
                setError(err.message);
                setLoading(false);
            });
    }, [chapter]);

    // Build a map of itemId -> { parentId, siblings (including self), depth }
    const nodeInfoMap = useMemo(() => {
        if (!chapterData || !chapterData.topics) return new Map();

        const map = new Map();

        const processTopics = (topics, parentId, depth) => {
            const siblingIds = topics.map(t => t.id);
            topics.forEach(topic => {
                map.set(topic.id, {
                    parentId,
                    siblingIds,
                    depth,
                    item: topic
                });
                if (topic.subTopics && topic.subTopics.length > 0) {
                    processTopics(topic.subTopics, topic.id, depth + 1);
                }
            });
        };

        processTopics(chapterData.topics, null, 0);
        return map;
    }, [chapterData]);

    // Get all descendant IDs of an item (for collapsing entire subtrees)
    const getDescendantIds = useCallback((itemId) => {
        const itemInfo = nodeInfoMap.get(itemId);
        if (!itemInfo || !itemInfo.item) return [];

        const descendants = [];
        const collectDescendants = (item) => {
            if (item.subTopics) {
                item.subTopics.forEach(subTopic => {
                    descendants.push(subTopic.id);
                    collectDescendants(subTopic);
                });
            }
        };
        collectDescendants(itemInfo.item);
        return descendants;
    }, [nodeInfoMap]);

    const handleNodeClick = useCallback((itemId) => {
        setExpandedNodeIds((prev) => {
            const newSet = new Set(prev);
            const itemInfo = nodeInfoMap.get(itemId);

            if (newSet.has(itemId)) {
                // Collapsing: remove this item and all its descendants
                newSet.delete(itemId);
                const descendants = getDescendantIds(itemId);
                descendants.forEach(id => newSet.delete(id));
            } else {
                // Expanding: collapse all siblings and their descendants first
                if (itemInfo) {
                    itemInfo.siblingIds.forEach(siblingId => {
                        if (siblingId !== itemId) {
                            newSet.delete(siblingId);
                            const siblingDescendants = getDescendantIds(siblingId);
                            siblingDescendants.forEach(id => newSet.delete(id));
                        }
                    });
                }
                // Then expand this item
                newSet.add(itemId);
            }
            return newSet;
        });
    }, [nodeInfoMap, getDescendantIds]);

    if (loading) {
        return (
            <div className="topics-view">
                <div className="loading-spinner">Loading...</div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="topics-view">
                <div className="error-message">Error: {error}</div>
            </div>
        );
    }

    if (!chapterData) {
        return (
            <div className="topics-view">
                <div className="error-message">No data available</div>
            </div>
        );
    }

    return (
        <div className="topics-view">
            <div className="nodes-container">
                {chapterData.topics.map((topic) => (
                    <ContentView
                        key={topic.id}
                        item={topic}
                        expandedNodeIds={expandedNodeIds}
                        onNodeClick={handleNodeClick}
                        depth={0}
                    />
                ))}
            </div>

            <BottomNav
                classNum={standard}
                subject={subject}
                chapterNo={chapterData.chapterNo}
                chapterTitle={chapterData.chapterName}
                onNavigateToChapters={onBack}
                onHome={onHome}
            />

        </div>
    );
}

export default TopicView;
