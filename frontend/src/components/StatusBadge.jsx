import React from 'react';

function StatusBadge({ type = 'severity', value }) {
    const className = `status-badge ${type}-${value}`;
    const label = value?.replace(/_/g, ' ') || 'unknown';

    return (
        <span className={className}>
            <span className="badge-dot"></span>
            {label}
        </span>
    );
}

export default StatusBadge;
