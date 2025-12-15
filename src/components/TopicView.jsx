import { useState, useEffect, useMemo, useCallback } from 'react';
import ContentView from './ContentView';
import BottomNav from './BottomNav';
import './TopicView.css';
import api from '../services/api';

function TopicView({ standard, subject, chapter, viewMode, onViewModeChange, onBack, onHome }) {
    const [chapterData, setChapterData] = useState(null);
    const [expandedNodeIds, setExpandedNodeIds] = useState(new Set());
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        setLoading(true);
        setError(null);

        const loadData = async () => {
            try {
                // Load different data based on viewMode
                if (viewMode === 'book-qa' || viewMode === 'board-qa' || viewMode === 'bonus-qa' || viewMode === 'pop-quiz' || viewMode === 'deep-quiz') {
                    // Load Q&A data
                    const data = await api.getQA(standard, subject);

                    // Find the matching chapter
                    const qaChapter = data.chapters.find(ch => ch.chapterNo === String(chapter.chapterNo));

                    if (!qaChapter || !qaChapter.qa) {
                        throw new Error('No Q&A available for this chapter');
                    }

                    // Transform Q&A data into hierarchical structure
                    const transformedData = transformQAToTopics(qaChapter, viewMode);
                    setChapterData(transformedData);
                    setLoading(false);
                } else {
                    // Load teaching content (concept.json)
                    await api.getConcept(standard, subject);
                    setChapterData(chapter);
                    setLoading(false);
                }
            } catch (err) {
                setError(err.message || 'Failed to load data');
                setLoading(false);
            }
        };

        loadData();
    }, [chapter, viewMode, standard, subject]);

    // Transform Q&A data into topic-like structure
    const transformQAToTopics = (qaChapter, viewMode) => {
        // Helper function to extract first line of question text
        const getQuestionPreview = (questionContent) => {
            if (!questionContent || questionContent.length === 0) return '';

            // Find the first text content
            for (let item of questionContent) {
                if (item.type === 'body' && item.text) {
                    // Remove markdown formatting and get first line
                    return item.text.replace(/\*\*/g, '').split('\n')[0];
                } else if (item.type === 'paragraph' && item.items) {
                    // For paragraph type, extract text from items
                    for (let subItem of item.items) {
                        if (subItem.type === 'body' && subItem.text) {
                            return subItem.text.replace(/\*\*/g, '').split('\n')[0];
                        }
                    }
                }
            }
            return '';
        };

        // Handle Pop Quiz mode separately
        if (viewMode === 'pop-quiz') {
            // Filter for very-short questions only
            const veryShortQuestions = qaChapter.qa.filter(qa => qa.questionType === 'very-short');

            // Randomly select up to 5 questions
            const shuffled = [...veryShortQuestions].sort(() => Math.random() - 0.5);
            const selectedQuestions = shuffled.slice(0, Math.min(5, shuffled.length));

            // Create a single topic with all selected questions
            const subTopics = [];
            selectedQuestions.forEach((qa, index) => {
                // For Pop Quiz, just show Q1, Q2, etc. without preview
                subTopics.push({
                    id: `pop-quiz-qa-${index}-q`,
                    title: `Q${index + 1}`,
                    content: qa.question
                });

                subTopics.push({
                    id: `pop-quiz-qa-${index}-answer`,
                    title: 'Answer',
                    content: qa.answer
                });
            });

            return {
                ...qaChapter,
                topics: [{
                    id: 'topic-pop-quiz',
                    title: 'Pop Quiz',
                    subTopics: subTopics
                }]
            };
        }

        // Handle Deep Quiz mode separately
        if (viewMode === 'deep-quiz') {
            // Filter for short questions only
            const shortQuestions = qaChapter.qa.filter(qa => qa.questionType === 'short');

            // Randomly select up to 5 questions
            const shuffled = [...shortQuestions].sort(() => Math.random() - 0.5);
            const selectedQuestions = shuffled.slice(0, Math.min(5, shuffled.length));

            // Create a single topic with all selected questions
            const subTopics = [];
            selectedQuestions.forEach((qa, index) => {
                // For Deep Quiz, just show Q1, Q2, etc. without preview
                subTopics.push({
                    id: `deep-quiz-qa-${index}-q`,
                    title: `Q${index + 1}`,
                    content: qa.question
                });

                subTopics.push({
                    id: `deep-quiz-qa-${index}-answer`,
                    title: 'Answer',
                    content: qa.answer
                });
            });

            return {
                ...qaChapter,
                topics: [{
                    id: 'topic-deep-quiz',
                    title: 'Deep Quiz',
                    subTopics: subTopics
                }]
            };
        }
        // Filter Q&A by source/isBoardExam based on viewMode
        let filteredQA = qaChapter.qa;

        if (viewMode === 'book-qa') {
            filteredQA = qaChapter.qa.filter(qa => qa.source === 'book');
        } else if (viewMode === 'board-qa') {
            filteredQA = qaChapter.qa.filter(qa => qa.isBoardExam === true);
        } else if (viewMode === 'bonus-qa') {
            filteredQA = qaChapter.qa.filter(qa => qa.source === 'extra' && qa.isBoardExam === false);
        }

        // Group Q&A by questionType
        const grouped = {
            'very-short': [],
            'short': [],
            'long': [],
            'very-long': []
        };

        filteredQA.forEach(qa => {
            if (grouped[qa.questionType]) {
                grouped[qa.questionType].push(qa);
            }
        });

        // Create topic-like structure
        const topics = [];

        const typeLabels = {
            'very-short': 'Very Short',
            'short': 'Short',
            'long': 'Long',
            'very-long': 'Very Long'
        };

        Object.keys(grouped).forEach(questionType => {
            if (grouped[questionType].length > 0) {
                const subTopics = [];

                grouped[questionType].forEach((qa, index) => {
                    const questionPreview = getQuestionPreview(qa.question);

                    // Truncate at first space after 20 characters
                    let truncatedPreview = questionPreview;
                    if (questionPreview.length > 20) {
                        const afterTwenty = questionPreview.substring(20);
                        const spaceIndex = afterTwenty.indexOf(' ');

                        if (spaceIndex !== -1) {
                            // Found a space, truncate there
                            truncatedPreview = questionPreview.substring(0, 20 + spaceIndex) + '...';
                        } else {
                            // No space found, truncate at 25 characters
                            truncatedPreview = questionPreview.substring(0, 25) + '...';
                        }
                    }

                    // Build title with reference if available
                    const referenceText = qa.reference ? ` (${qa.reference})` : '';
                    const title = `Q${index + 1}: "${truncatedPreview}"${referenceText}`;

                    // Add Q node with question preview in title
                    subTopics.push({
                        id: `${questionType}-qa-${index}-q`,
                        title: title,
                        content: qa.question
                    });

                    // Add Answer node as sibling
                    subTopics.push({
                        id: `${questionType}-qa-${index}-answer`,
                        title: 'Answer',
                        content: qa.answer
                    });
                });

                topics.push({
                    id: `topic-${questionType}`,
                    title: typeLabels[questionType],
                    subTopics: subTopics
                });
            }
        });

        return {
            ...qaChapter,
            topics: topics
        };
    };

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
                <BottomNav
                    classNum={standard}
                    subject={subject}
                    chapterNo={chapter.chapterNo}
                    chapterTitle={chapter.chapterName}
                    viewMode={viewMode}
                    onViewModeChange={onViewModeChange}
                    onNavigateToChapters={onBack}
                    onHome={onHome}
                />
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
                viewMode={viewMode}
                onViewModeChange={onViewModeChange}
                onNavigateToChapters={onBack}
                onHome={onHome}
            />

        </div>
    );
}

export default TopicView;
