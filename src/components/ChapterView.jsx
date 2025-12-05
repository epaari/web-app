import { useState, useEffect, useMemo, useCallback } from 'react';
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

    // Build a map of nodeId -> { parentId, siblings (including self), depth }
    const nodeInfoMap = useMemo(() => {
        if (!chapterData || !chapterData.nodes) return new Map();

        const map = new Map();

        const processNodes = (nodes, parentId, depth) => {
            const siblingIds = nodes.map(n => n.id);
            nodes.forEach(node => {
                map.set(node.id, {
                    parentId,
                    siblingIds,
                    depth,
                    node
                });
                if (node.children && node.children.length > 0) {
                    processNodes(node.children, node.id, depth + 1);
                }
            });
        };

        processNodes(chapterData.nodes, null, 0);
        return map;
    }, [chapterData]);

    // Get all descendant IDs of a node (for collapsing entire subtrees)
    const getDescendantIds = useCallback((nodeId) => {
        const nodeInfo = nodeInfoMap.get(nodeId);
        if (!nodeInfo || !nodeInfo.node) return [];

        const descendants = [];
        const collectDescendants = (node) => {
            if (node.children) {
                node.children.forEach(child => {
                    descendants.push(child.id);
                    collectDescendants(child);
                });
            }
        };
        collectDescendants(nodeInfo.node);
        return descendants;
    }, [nodeInfoMap]);

    const handleNodeClick = useCallback((nodeId) => {
        setExpandedNodeIds((prev) => {
            const newSet = new Set(prev);
            const nodeInfo = nodeInfoMap.get(nodeId);

            if (newSet.has(nodeId)) {
                // Collapsing: remove this node and all its descendants
                newSet.delete(nodeId);
                const descendants = getDescendantIds(nodeId);
                descendants.forEach(id => newSet.delete(id));
            } else {
                // Expanding: collapse all siblings and their descendants first
                if (nodeInfo) {
                    nodeInfo.siblingIds.forEach(siblingId => {
                        if (siblingId !== nodeId) {
                            newSet.delete(siblingId);
                            const siblingDescendants = getDescendantIds(siblingId);
                            siblingDescendants.forEach(id => newSet.delete(id));
                        }
                    });
                }
                // Then expand this node
                newSet.add(nodeId);
            }
            return newSet;
        });
    }, [nodeInfoMap, getDescendantIds]);

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
