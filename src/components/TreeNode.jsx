import { useCallback, useState, useEffect, useRef } from 'react';

function TreeNode({ item, expandedNodeIds, onNodeClick, depth }) {
    const isExpanded = expandedNodeIds.has(item.id);
    const hasContent = item.content && item.content.length > 0;
    const hasChildren = item.subTopics && item.subTopics.length > 0;
    const isExpandable = hasContent || hasChildren;
    const nodeRef = useRef(null);

    // State for image modal
    const [modalImage, setModalImage] = useState(null);

    // State for info popover
    const [infoModal, setInfoModal] = useState(null); // { word, info, x, y }

    // Scroll to align bottom of item with bottom of screen when expanded
    useEffect(() => {
        if (isExpanded && nodeRef.current && (depth === 0 || depth === 1)) {
            // Wait for content to render and animations to complete
            setTimeout(() => {
                if (nodeRef.current) {
                    const element = nodeRef.current;
                    const rect = element.getBoundingClientRect();
                    const viewportHeight = window.innerHeight;

                    // Get BottomNav height
                    const bottomNav = document.querySelector('.bottom-nav');
                    const bottomNavHeight = bottomNav ? bottomNav.offsetHeight : 0;

                    // Calculate the target scroll position
                    // We want the bottom of the element to align with the bottom of the viewport (minus BottomNav)
                    const elementBottom = rect.bottom;
                    const targetBottom = viewportHeight - bottomNavHeight;
                    const scrollNeeded = elementBottom - targetBottom;

                    // Scroll to position
                    window.scrollBy({
                        top: scrollNeeded,
                        behavior: 'smooth'
                    });
                }
            }, 350); // Delay to ensure content is fully rendered
        }
    }, [isExpanded, depth]);

    const handleClick = useCallback(() => {
        if (isExpandable) {
            onNodeClick(item.id);
        }
    }, [isExpandable, onNodeClick, item.id]);

    const handleKeyDown = useCallback(
        (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                handleClick();
            }
        },
        [handleClick]
    );

    const getNodeTypeClass = () => {
        if (depth === 0) return 'node-title1';  // Topic
        if (depth === 1) return 'node-title2';  // SubTopic
        return '';
    };

    const handleThumbnailClick = useCallback((url) => {
        setModalImage(url);
    }, []);

    const handleModalClose = useCallback(() => {
        setModalImage(null);
    }, []);

    // Info popover handlers
    const handleInfoWordClick = useCallback((e, word, info) => {
        const rect = e.target.getBoundingClientRect();
        setInfoModal({ word, info, x: rect.left + rect.width / 2, y: rect.top });
    }, []);

    const handleInfoModalClose = useCallback(() => {
        setInfoModal(null);
    }, []);

    // Handle Escape key to close info modal
    useEffect(() => {
        const handleEscape = (e) => {
            if (e.key === 'Escape' && infoModal) {
                handleInfoModalClose();
            }
        };
        document.addEventListener('keydown', handleEscape);
        return () => document.removeEventListener('keydown', handleEscape);
    }, [infoModal, handleInfoModalClose]);

    // Trigger MathJax typesetting when content is shown
    useEffect(() => {
        if (isExpanded && hasContent && window.MathJax) {
            window.MathJax.typesetPromise?.();
        }
    }, [isExpanded, hasContent]);

    const parseMarkdown = (text) => {
        if (!text) return null;

        // First, split by [[word||info]] pattern to handle info words
        // Then handle bold text within each segment
        const infoPattern = /(\[\[.*?\|\|.*?\]\])/g;
        const segments = text.split(infoPattern);

        return segments.map((segment, segIndex) => {
            // Check if this segment is an info word [[word||info]]
            const infoMatch = segment.match(/^\[\[(.*?)\|\|(.*?)\]\]$/);
            if (infoMatch) {
                const word = infoMatch[1];
                const info = infoMatch[2];
                return (
                    <span
                        key={`info-${segIndex}`}
                        className="info-word"
                        onClick={(e) => {
                            e.stopPropagation();
                            handleInfoWordClick(e, word, info);
                        }}
                        onKeyDown={(e) => {
                            if (e.key === 'Enter' || e.key === ' ') {
                                e.preventDefault();
                                e.stopPropagation();
                                handleInfoWordClick(e, word, info);
                            }
                        }}
                        tabIndex={0}
                        role="button"
                        aria-label={`Learn more about ${word}`}
                    >
                        {word}
                    </span>
                );
            }

            // Handle bold text within regular segments
            const boldParts = segment.split(/(\*\*.*?\*\*)/g);
            return boldParts.map((part, partIndex) => {
                if (part.startsWith('**') && part.endsWith('**')) {
                    return <strong key={`${segIndex}-bold-${partIndex}`} className="markdown-bold">{part.slice(2, -2)}</strong>;
                }
                return part ? <span key={`${segIndex}-text-${partIndex}`}>{part}</span> : null;
            });
        });
    };

    const renderContent = () => {
        if (!hasContent) return null;

        return (
            <div className="node-content">
                {item.content.map((contentItem, index) => {
                    if (contentItem.type === 'image') {
                        return (
                            <img
                                key={index}
                                src={contentItem.url}
                                alt={item.title}
                                loading="lazy"
                                className="content-image"
                            />
                        );
                    }

                    if (contentItem.type === 'body') {
                        return (
                            <p key={index} className="content-body">
                                {parseMarkdown(contentItem.text)}
                            </p>
                        );
                    }

                    if (contentItem.type === 'bullet1') {
                        return (
                            <p key={index} className="content-bullet bullet-1">
                                {parseMarkdown(contentItem.text)}
                            </p>
                        );
                    }

                    if (contentItem.type === 'bullet2') {
                        return (
                            <p key={index} className="content-bullet bullet-2">
                                {parseMarkdown(contentItem.text)}
                            </p>
                        );
                    }

                    if (contentItem.type === 'equation') {
                        return (
                            <div key={index} className="content-equation">
                                {`$$${contentItem.equation}$$`}
                            </div>
                        );
                    }

                    return null;
                })}

                {/* Image Modal */}
                {modalImage && (
                    <div
                        className="image-modal-overlay"
                        onClick={handleModalClose}
                        role="dialog"
                        aria-modal="true"
                        aria-label="Full size image"
                    >
                        <img
                            src={modalImage}
                            alt={item.title}
                            className="image-modal-content"
                        />
                    </div>
                )}

                {/* Info Popover */}
                {infoModal && (
                    <div
                        className="info-popover-backdrop"
                        onClick={handleInfoModalClose}
                    >
                        <div
                            className="info-popover"
                            style={{
                                position: 'fixed',
                                left: infoModal.x,
                                top: infoModal.y,
                                transform: 'translate(-50%, -100%)',
                            }}
                            onClick={(e) => e.stopPropagation()}
                        >
                            {infoModal.info}
                        </div>
                    </div>
                )}
            </div>
        );
    };

    const renderChildren = () => {
        if (!hasChildren) return null;

        return (
            <div className="node-children">
                {item.subTopics.map((subTopic) => (
                    <TreeNode
                        key={subTopic.id}
                        item={subTopic}
                        expandedNodeIds={expandedNodeIds}
                        onNodeClick={onNodeClick}
                        depth={depth + 1}
                    />
                ))}
            </div>
        );
    };

    return (
        <div ref={nodeRef} className={`tree-node depth-${depth} ${getNodeTypeClass()}`}>
            <div
                className={`node-header ${isExpandable ? 'expandable' : ''} ${isExpanded ? 'expanded' : ''}`}
                onClick={handleClick}
                onKeyDown={handleKeyDown}
                tabIndex={isExpandable ? 0 : -1}
                role={isExpandable ? 'button' : undefined}
                aria-expanded={isExpandable ? isExpanded : undefined}
            >
                {isExpandable && (
                    <span className="expand-icon" aria-hidden="true">
                        {isExpanded ? '▼' : '▶'}
                    </span>
                )}
                <span className="node-label">{item.title}</span>
            </div>

            {isExpanded && (
                <div className="node-expanded-content">
                    {renderContent()}
                    {renderChildren()}
                </div>
            )}
        </div>
    );
}

export default TreeNode;
