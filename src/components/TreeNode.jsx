import { useCallback, useState, useEffect } from 'react';

function TreeNode({ node, expandedNodeIds, onNodeClick, depth }) {
    const isExpanded = expandedNodeIds.has(node.id);
    const hasContent = node.content && node.content.length > 0;
    const hasChildren = node.children && node.children.length > 0;
    const isExpandable = hasContent || hasChildren;

    // State for image modal
    const [modalImage, setModalImage] = useState(null);

    // State for info popover
    const [infoModal, setInfoModal] = useState(null); // { word, info, x, y }

    const handleClick = useCallback(() => {
        if (isExpandable) {
            onNodeClick(node.id);
        }
    }, [isExpandable, onNodeClick, node.id]);

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
        switch (node.nodeType) {
            case 'title1':
                return 'node-title1';
            case 'title2':
                return 'node-title2';
            case 'title3':
                return 'node-title3';
            default:
                return '';
        }
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
                {node.content.map((item, index) => {
                    if (item.type === 'image') {
                        return (
                            <img
                                key={index}
                                src={item.url}
                                alt={node.label}
                                loading="lazy"
                                className="content-image"
                            />
                        );
                    }

                    if (item.type === 'bullet1') {
                        return (
                            <p key={index} className="content-bullet bullet-1">
                                {parseMarkdown(item.text)}
                            </p>
                        );
                    }

                    if (item.type === 'bullet2') {
                        return (
                            <p key={index} className="content-bullet bullet-2">
                                {parseMarkdown(item.text)}
                            </p>
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
                            alt={node.label}
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
                {node.children.map((child) => (
                    <TreeNode
                        key={child.id}
                        node={child}
                        expandedNodeIds={expandedNodeIds}
                        onNodeClick={onNodeClick}
                        depth={depth + 1}
                    />
                ))}
            </div>
        );
    };

    return (
        <div className={`tree-node depth-${depth} ${getNodeTypeClass()}`}>
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
                <span className="node-label">{node.label}</span>
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
