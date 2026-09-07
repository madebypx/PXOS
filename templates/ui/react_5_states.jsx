import React, { useState, useCallback } from 'react';

/**
 * Universal 5-State React Blueprint (PXOS T-12 Specification)
 * 
 * Enforces resilient handling across all 5 universal states:
 * 1. initial_idle: Populated data view adhering to design system.
 * 2. loading_pending: Skeleton loaders or debounced buttons during async fetch.
 * 3. empty_data: Helpful zero-state card with primary CTA.
 * 4. error_recovery: Human-readable error banner with retry trigger.
 * 5. destructive_action_guard: Dialog confirming irreversible deletion.
 */

export function Universal5StateList({
  title = "Active Workspaces",
  initialData = [],
  onFetch,
  onDelete,
  onCreate,
}) {
  // Finite State Machine Status:
  // 'initial_idle' | 'loading_pending' | 'empty_data' | 'error_recovery' | 'destructive_action_guard'
  const [status, setStatus] = useState(
    initialData && initialData.length > 0 ? 'initial_idle' : 'empty_data'
  );
  const [items, setItems] = useState(initialData || []);
  const [errorMessage, setErrorMessage] = useState('');
  const [pendingDeleteId, setPendingDeleteId] = useState(null);

  // Trigger async refresh / reload
  const handleReload = useCallback(async () => {
    setStatus('loading_pending');
    setErrorMessage('');
    try {
      if (onFetch) {
        const data = await onFetch();
        setItems(data);
        setStatus(data && data.length > 0 ? 'initial_idle' : 'empty_data');
      } else {
        // Fallback simulation
        setTimeout(() => {
          setStatus('initial_idle');
        }, 600);
      }
    } catch (err) {
      setErrorMessage(err.message || 'Failed to fetch items from server.');
      setStatus('error_recovery');
    }
  }, [onFetch]);

  // Request deletion (opens guard modal)
  const handleRequestDelete = useCallback((id) => {
    setPendingDeleteId(id);
    setStatus('destructive_action_guard');
  }, []);

  // Confirm deletion
  const handleConfirmDelete = useCallback(async () => {
    if (!pendingDeleteId) return;
    setStatus('loading_pending');
    try {
      if (onDelete) {
        await onDelete(pendingDeleteId);
      }
      const updated = items.filter((item) => item.id !== pendingDeleteId);
      setItems(updated);
      setPendingDeleteId(null);
      setStatus(updated.length > 0 ? 'initial_idle' : 'empty_data');
    } catch (err) {
      setErrorMessage(err.message || 'Failed to delete target record.');
      setStatus('error_recovery');
    }
  }, [pendingDeleteId, items, onDelete]);

  // Cancel deletion guard
  const handleCancelDelete = useCallback(() => {
    setPendingDeleteId(null);
    setStatus('initial_idle');
  }, []);

  return (
    <div className="pxos-5state-container" style={styles.container}>
      <header style={styles.header}>
        <h2 style={styles.title}>{title}</h2>
        <span style={styles.badge}>State: {status}</span>
      </header>

      {/* State 2: loading_pending */}
      {status === 'loading_pending' && (
        <div style={styles.skeletonContainer} aria-busy="true" aria-live="polite">
          <div style={styles.skeletonItem} />
          <div style={styles.skeletonItem} />
          <div style={styles.skeletonItem} />
        </div>
      )}

      {/* State 3: empty_data */}
      {status === 'empty_data' && (
        <div style={styles.emptyContainer}>
          <div style={styles.emptyIcon}>📂</div>
          <h3 style={styles.emptyTitle}>No records available</h3>
          <p style={styles.emptyText}>Get started by initializing your first resource.</p>
          <button
            style={{ ...styles.button, ...styles.buttonPrimary }}
            onClick={onCreate ? onCreate : () => handleReload()}
          >
            + Create New Item
          </button>
        </div>
      )}

      {/* State 4: error_recovery */}
      {status === 'error_recovery' && (
        <div style={styles.errorContainer} role="alert">
          <div style={styles.errorIcon}>⚠️</div>
          <h3 style={styles.errorTitle}>An unexpected error occurred</h3>
          <p style={styles.errorText}>{errorMessage || 'Network request failed.'}</p>
          <button
            style={{ ...styles.button, ...styles.buttonPrimary }}
            onClick={handleReload}
          >
            ↻ Retry Operation
          </button>
        </div>
      )}

      {/* State 5: destructive_action_guard modal */}
      {status === 'destructive_action_guard' && (
        <div style={styles.modalOverlay} role="dialog" aria-modal="true">
          <div style={styles.modalBox}>
            <span style={styles.modalBadge}>Irreversible Action</span>
            <h3 style={styles.modalTitle}>Delete Record?</h3>
            <p style={styles.modalText}>
              Are you sure you want to permanently delete item <strong>#{pendingDeleteId}</strong>?
              This action cannot be undone.
            </p>
            <div style={styles.modalActions}>
              <button
                style={{ ...styles.button, ...styles.buttonNeutral }}
                onClick={handleCancelDelete}
              >
                Cancel
              </button>
              <button
                style={{ ...styles.button, ...styles.buttonDanger }}
                onClick={handleConfirmDelete}
              >
                Confirm Delete
              </button>
            </div>
          </div>
        </div>
      )}

      {/* State 1: initial_idle */}
      {status === 'initial_idle' && (
        <ul style={styles.list}>
          {items.map((item) => (
            <li key={item.id} style={styles.listItem}>
              <div>
                <h4 style={styles.itemTitle}>{item.title || item.name || `Item ${item.id}`}</h4>
                <p style={styles.itemSubtitle}>ID: {item.id}</p>
              </div>
              <button
                style={{ ...styles.button, ...styles.buttonDangerSmall }}
                onClick={() => handleRequestDelete(item.id)}
              >
                Delete
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

const styles = {
  container: {
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
    background: 'rgba(22, 27, 46, 0.7)',
    border: '1px solid rgba(255, 255, 255, 0.08)',
    borderRadius: '12px',
    padding: '24px',
    maxWidth: '680px',
    margin: '0 auto',
    color: '#f1f5f9',
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '20px',
  },
  title: {
    fontSize: '20px',
    margin: 0,
    fontWeight: 600,
  },
  badge: {
    fontSize: '11px',
    padding: '4px 10px',
    background: 'rgba(56, 189, 248, 0.1)',
    color: '#38bdf8',
    borderRadius: '999px',
    border: '1px solid rgba(56, 189, 248, 0.2)',
  },
  list: {
    listStyle: 'none',
    padding: 0,
    margin: 0,
    display: 'flex',
    flexDirection: 'column',
    gap: '10px',
  },
  listItem: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '14px 18px',
    background: 'rgba(255, 255, 255, 0.03)',
    border: '1px solid rgba(255, 255, 255, 0.08)',
    borderRadius: '8px',
  },
  itemTitle: {
    fontSize: '15px',
    margin: '0 0 4px 0',
  },
  itemSubtitle: {
    fontSize: '12px',
    color: '#94a3b8',
    margin: 0,
  },
  skeletonContainer: {
    display: 'flex',
    flexDirection: 'column',
    gap: '10px',
  },
  skeletonItem: {
    height: '60px',
    background: 'rgba(255, 255, 255, 0.05)',
    borderRadius: '8px',
  },
  emptyContainer: {
    textAlign: 'center',
    padding: '36px 16px',
  },
  emptyIcon: {
    fontSize: '36px',
    marginBottom: '12px',
  },
  emptyTitle: {
    fontSize: '17px',
    margin: '0 0 8px 0',
  },
  emptyText: {
    color: '#94a3b8',
    fontSize: '13px',
    marginBottom: '18px',
  },
  errorContainer: {
    textAlign: 'center',
    padding: '24px',
    background: 'rgba(244, 63, 94, 0.08)',
    border: '1px solid rgba(244, 63, 94, 0.3)',
    borderRadius: '8px',
  },
  errorIcon: {
    fontSize: '32px',
    marginBottom: '8px',
  },
  errorTitle: {
    color: '#fecdd3',
    margin: '0 0 6px 0',
  },
  errorText: {
    color: '#94a3b8',
    fontSize: '13px',
    marginBottom: '16px',
  },
  modalOverlay: {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    background: 'rgba(0, 0, 0, 0.75)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 1000,
  },
  modalBox: {
    background: '#161b2e',
    border: '1px solid rgba(244, 63, 94, 0.4)',
    borderRadius: '12px',
    padding: '24px',
    maxWidth: '440px',
    width: '90%',
    textAlign: 'center',
  },
  modalBadge: {
    fontSize: '10px',
    fontWeight: 700,
    textTransform: 'uppercase',
    color: '#f43f5e',
    background: 'rgba(244, 63, 94, 0.15)',
    padding: '3px 8px',
    borderRadius: '999px',
  },
  modalTitle: {
    fontSize: '18px',
    margin: '12px 0 8px 0',
  },
  modalText: {
    fontSize: '13px',
    color: '#94a3b8',
    lineHeight: 1.5,
    marginBottom: '20px',
  },
  modalActions: {
    display: 'flex',
    justifyContent: 'center',
    gap: '12px',
  },
  button: {
    padding: '8px 16px',
    borderRadius: '6px',
    fontSize: '13px',
    fontWeight: 600,
    cursor: 'pointer',
    border: 'none',
    transition: 'all 0.15s ease',
  },
  buttonPrimary: {
    background: '#38bdf8',
    color: '#041324',
  },
  buttonDanger: {
    background: '#f43f5e',
    color: '#ffffff',
  },
  buttonDangerSmall: {
    background: 'rgba(244, 63, 94, 0.12)',
    color: '#f43f5e',
    border: '1px solid rgba(244, 63, 94, 0.3)',
    fontSize: '12px',
    padding: '6px 12px',
  },
  buttonNeutral: {
    background: 'rgba(255, 255, 255, 0.08)',
    color: '#f1f5f9',
  },
};
