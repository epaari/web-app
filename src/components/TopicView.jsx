import { useState, useEffect, useMemo, useCallback } from 'react';
import ContentView from './ContentView';
import BottomNav from './BottomNav';
import './TopicView.css';
import api from '../services/api';

function TopicView({ standard, subject, chapter, viewMode, onViewModeChange, onBack, onHome }) {
    const [chapterData, setChapterData] = useState(null);
    const [expandedNodeIds, setExpandedNodeIds] = useState(new Set());
    const [selectedQuestions, setSelectedQuestions] = useState(new Set());
    const [hasTextBook, setHasTextBook] = useState(false);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        setLoading(true);
        setError(null);

        const loadData = async () => {
            try {
                // Load different data based on viewMode
                if (viewMode === 'text-book') {
                    // No specific data loading needed for text-book, we just render iframe.
                    // But we need chapterData to be present for title etc.
                    // Reuse concept loading or just set basics if already loaded.
                    // The effect runs when viewMode changes. If we switch from 'teaching' we have data.
                    // But if we refresh on 'text-book', we might need to load something.
                    // Let's assume we load concept data as fallback/context.
                    await api.getConcept(standard, subject);
                    setChapterData(chapter); // Or the full concept data if structure needed
                    setLoading(false);
                } else if (viewMode === 'book-qa' || viewMode === 'board-qa' || viewMode === 'bonus-qa' || viewMode === 'pop-quiz' || viewMode === 'deep-quiz' || viewMode === 'q-gen') {
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
        loadData();
    }, [chapter, viewMode, standard, subject]);

    // Check for Text Book PDF availability
    useEffect(() => {
        const checkTextBookCallback = async () => {
            if (chapter && chapter.chapterNo) {
                const subjectSlug = subject.toLowerCase().replace(/\s+/g, '-');
                // Path format: 10-science/pdfs/1.pdf
                // Note: 'chapter.chapterNo' might be '1' or '01', assume it matches file name.
                // Ideally we should try both or ensure consistency.
                // Let's assume exact match with what's in JSON for now. 
                // If chapterNo in JSON is "1", file is "1.pdf".
                const pdfPath = `${standard}-${subjectSlug}/pdfs/${chapter.chapterNo}.pdf`;
                const exists = await api.checkFileExists(pdfPath);
                setHasTextBook(exists);
            } else {
                setHasTextBook(false);
            }
        };
        checkTextBookCallback();
    }, [standard, subject, chapter]);

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
                    title: `Pop Quiz (${selectedQuestions.length})`,
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
                    title: `Deep Quiz (${selectedQuestions.length})`,
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
            filteredQA = qaChapter.qa.filter(qa => qa.source === 'extra');
        } else if (viewMode === 'q-gen') {
            // For Q-Gen, include both book and extra
            filteredQA = qaChapter.qa.filter(qa => qa.source === 'book' || qa.source === 'extra');
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
                // Special handling for Q-Gen: Flatten structure
                if (viewMode === 'q-gen') {
                    const combinedContent = [];
                    grouped[questionType].forEach((qa, index) => {
                        const label = `**Q${index + 1}.** `;
                        let questionContent = [];

                        // Inject Checkbox for Q-Gen
                        combinedContent.push({
                            type: 'q-gen-checkbox',
                            id: `${questionType}-qa-${index}`, // Unique ID for selection
                            questionText: label, // Store label to print later if needed (handled in content though)
                            fullQuestion: qa // Store full QA object for export
                        });

                        if (qa.question && Array.isArray(qa.question) && qa.question.length > 0) {
                            // Deep clone to avoid mutating original data
                            questionContent = JSON.parse(JSON.stringify(qa.question));

                            const firstItem = questionContent[0];
                            if (firstItem.type === 'body') {
                                firstItem.text = label + (firstItem.text || '');
                            } else if (firstItem.type === 'paragraph' && firstItem.items && firstItem.items.length > 0) {
                                // Try to find the first text-containing item in the paragraph to prepend
                                const firstTextItem = firstItem.items[0];
                                if (firstTextItem.text !== undefined) {
                                    firstTextItem.text = label + firstTextItem.text;
                                } else {
                                    // Fallback: insert a body item at the start of paragraph items
                                    firstItem.items.unshift({ type: 'body', text: label });
                                }
                            } else {
                                // Fallback: Prepend a new body item if first item is image/equation etc
                                questionContent.unshift({ type: 'body', text: label });
                            }
                        } else {
                            questionContent.push({ type: 'body', text: label });
                        }

                        combinedContent.push(...questionContent);
                    });

                    topics.push({
                        id: `topic-${questionType}`,
                        title: `${typeLabels[questionType]} (${grouped[questionType].length})`,
                        subTopics: [], // No subtopics for Q-Gen
                        content: combinedContent
                    });

                    return; // Continue to next questionType
                }

                // Standard logic for other modes (Book QA, Board QA, etc.)
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

                    // Add Answer node as sibling (Logic for q-gen removed from here as it's handled above)
                    subTopics.push({
                        id: `${questionType}-qa-${index}-answer`,
                        title: 'Answer',
                        content: qa.answer
                    });
                });

                topics.push({
                    id: `topic-${questionType}`,
                    title: `${typeLabels[questionType]} (${grouped[questionType].length})`,
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

    const handleSelectionChange = useCallback((id, fullQuestion) => {
        setSelectedQuestions(prev => {
            const newSet = new Set(prev);
            // We store the ID to track selection state
            // For export, we might need the data.
            // Actually, let's store the ID, and we can look up the data or pass it.
            // Better: Store the whole object if the set supports it, or just ID.
            // Let's store ID. To export, we need to map IDs back to content.
            // Alternative: The checkbox item in JSON already has the data.
            // But 'selectedQuestions' is just a set of IDs.
            // We need a way to retrieve the content for export.
            // We can iterate the 'chapterData' again to find selected IDs.
            if (newSet.has(id)) {
                newSet.delete(id);
            } else {
                newSet.add(id);
            }
            return newSet;
        });
    }, []);

    const handleExportPDF = () => {
        const printWindow = window.open('', '_blank');
        if (!printWindow) return;

        // Collect selected content
        // We need to traverse the current 'chapterData' to find the selected items
        // Since structure is flattened in Q-Gen, we can iterate 'chapterData.topics'
        const selectedItems = [];

        if (chapterData && chapterData.topics) {
            chapterData.topics.forEach(topic => {
                if (topic.content) {
                    // In Q-Gen flattened mode, 'content' has 'q-gen-checkbox' items mixed with content
                    // We need to associate content with the checkbox.
                    // The structure we built: [Checkbox, Part1, Part2, Spacer, Checkbox, ...]
                    // This is tricky to parse back.

                    // Better approach: In 'transformQAToTopics', we assigned IDs like 'very-short-qa-0'.
                    // We can re-fetch the raw QA list stored in 'chapterData'? No, 'chapterData' is the transformed one.

                    // Let's rely on api cache or just re-request since it's local/fast?
                    // Or better: Let's look at the 'content' array.
                    // Iterate content, when we see a checkbox with ID in selected set, capture subsequent items until next checkbox/end.

                    let capturing = false;
                    let currentQuestionBlock = [];

                    topic.content.forEach(item => {
                        if (item.type === 'q-gen-checkbox') {
                            if (capturing) {
                                // Push previous block
                                selectedItems.push([...currentQuestionBlock]);
                                currentQuestionBlock = [];
                            }

                            if (selectedQuestions.has(item.id)) {
                                capturing = true;
                                // We don't push the checkbox itself to PDF, but we might want the number.
                                // The number was prepended to the next text item.
                                // So we just continue.
                            } else {
                                capturing = false;
                            }
                        } else {
                            if (capturing) {
                                currentQuestionBlock.push(item);
                            }
                        }
                    });
                    // Push last block
                    if (capturing && currentQuestionBlock.length > 0) {
                        selectedItems.push([...currentQuestionBlock]);
                    }
                }
            });
        }

        const htmlContent = `
            <!DOCTYPE html>
            <html>
            <head>
                <title>Q-Gen Export - ${chapterData.chapterName}</title>
                <style>
                    body { font-family: sans-serif; padding: 20px; line-height: 1.5; color: #000; }
                    .question-block { margin-bottom: 20px; }
                    .content-image { max-width: 100%; height: auto; display: block; margin: 10px 0; }
                    .content-equation { margin: 10px 0; }
                    /* Add more print styles as needed */
                    @media print {
                        .no-print { display: none; }
                    }
                </style>
                <script type="text/javascript" id="MathJax-script" async
                    src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js">
                </script>
            </head>
            <body>
                <h1>${chapterData.Standard} - ${chapterData.Subject}</h1>
                <h2>${chapterData.chapterName}</h2>
                <hr/>
                <div class="questions-container">
                    ${selectedItems.map(block => {
            return '<div class="question-block">' +
                block.map(item => {
                    if (item.type === 'body') return '<p>' + item.text.replace(/\\*\\*/g, '') + '</p>'; // Simple markdown strip
                    if (item.type === 'image') return '<img src="' + item.url + '" class="content-image"/>';
                    if (item.type === 'equation') return '<div>$$' + item.equation + '$$</div>';
                    if (item.type === 'paragraph' && item.items) {
                        return '<p>' + item.items.map(sub => {
                            if (sub.type === 'text' || sub.type === 'body') return sub.text;
                            if (sub.type === 'equation') return '$' + sub.equation + '$';
                            return '';
                        }).join('') + '</p>';
                    }
                    return '';
                }).join('') +
                '</div>';
        }).join('')}
                </div>
                <script>
                    window.onload = function() {
                        setTimeout(() => {
                             window.print();
                             // window.close(); // Optional: close after print
                        }, 1000); // Wait for MathJax
                    }
                </script>
            </body>
            </html>
        `;

        printWindow.document.write(htmlContent);
        printWindow.document.close();
    };

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

    if (viewMode === 'text-book') {
        const subjectSlug = subject.toLowerCase().replace(/\s+/g, '-');
        const pdfPath = `/db/${standard}-${subjectSlug}/pdfs/${chapter.chapterNo}.pdf`;

        return (
            <div className="topics-view" style={{ height: '100vh', paddingBottom: '0', display: 'flex', flexDirection: 'column' }}>
                <div style={{ flex: 1, position: 'relative' }}>
                    <iframe
                        src={pdfPath}
                        style={{ width: '100%', height: '100%', border: 'none' }}
                        title="Text Book"
                    />
                </div>
                <BottomNav
                    classNum={standard}
                    subject={subject}
                    chapterNo={chapterData.chapterNo}
                    chapterTitle={chapterData.chapterName}
                    viewMode={viewMode}
                    hasTextBook={hasTextBook}
                    onViewModeChange={onViewModeChange}
                    onNavigateToChapters={onBack}
                    onHome={onHome}
                />
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
                        selectedQuestions={selectedQuestions}
                        onSelectionChange={handleSelectionChange}
                        depth={0}
                    />
                ))}
            </div>

            {/* Q-Gen PDF Floating Action Panel */}
            {viewMode === 'q-gen' && selectedQuestions.size > 0 && (
                <div className="pdf-action-panel">
                    <div className="pdf-panel-header">
                        <button
                            className="pdf-btn clear"
                            onClick={() => setSelectedQuestions(new Set())}
                        >
                            Clear
                        </button>
                        <button
                            className="pdf-btn export"
                            onClick={handleExportPDF}
                        >
                            Export PDF
                        </button>
                    </div>

                    <div className="pdf-panel-stats">
                        {['very-short', 'short', 'long', 'very-long'].map(type => {
                            const count = Array.from(selectedQuestions).filter(id => id.startsWith(type)).length;
                            const labelMap = {
                                'very-short': 'VS',
                                'short': 'S',
                                'long': 'L',
                                'very-long': 'VL'
                            };
                            return (
                                <div key={type} className="stat-box">
                                    <div className="stat-label">{labelMap[type]}</div>
                                    <div className="stat-value">{count}</div>
                                </div>
                            );
                        })}
                    </div>
                </div>
            )}

            <BottomNav
                classNum={standard}
                subject={subject}
                chapterNo={chapterData.chapterNo}
                chapterTitle={chapterData.chapterName}
                viewMode={viewMode}
                hasTextBook={hasTextBook}
                onViewModeChange={onViewModeChange}
                onNavigateToChapters={onBack}
                onHome={onHome}
            />

        </div>
    );
}

export default TopicView;
