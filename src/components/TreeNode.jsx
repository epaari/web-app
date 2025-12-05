import { useCallback, useState } from 'react';

function TreeNode({ node, expandedNodeIds, onNodeClick, depth }) {
    const isExpanded = expandedNodeIds.has(node.id);
    const hasContent = node.content && node.content.length > 0;
    const hasChildren = node.children && node.children.length > 0;
    const isExpandable = hasContent || hasChildren;

    // State for image modal
    const [modalImage, setModalImage] = useState(null);

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

    const renderContent = () => {
        if (!hasContent) return null;

        return (
            <div className="node-content">
                {node.content.map((item, index) => {
                    if (item.type === 'image') {
                        return (
                            <div
                                key={index}
                                className="content-thumbnail-wrapper"
                                onClick={() => handleThumbnailClick(item.url)}
                                role="button"
                                tabIndex={0}
                                onKeyDown={(e) => {
                                    if (e.key === 'Enter' || e.key === ' ') {
                                        e.preventDefault();
                                        handleThumbnailClick(item.url);
                                    }
                                }}
                                aria-label={`View full image: ${node.label}`}
                            >
                                <img
                                    src={item.url}
                                    alt={node.label}
                                    loading="lazy"
                                    className="content-thumbnail"
                                />
                                <span className="thumbnail-zoom-icon">🔍</span>
                            </div>
                        );
                    }

                    if (item.type === 'bullet1') {
                        return (
                            <p key={index} className="content-bullet bullet-1">
                                {item.text}
                            </p>
                        );
                    }

                    if (item.type === 'bullet2') {
                        return (
                            <p key={index} className="content-bullet bullet-2">
                                {item.text}
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
