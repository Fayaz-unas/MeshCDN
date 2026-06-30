import { useApp } from '../../store/AppContext';
import { CheckCircle, AlertTriangle, XCircle, Info, X } from 'lucide-react';

const iconMap = {
  success: CheckCircle,
  error: XCircle,
  warning: AlertTriangle,
  info: Info,
};

export default function NotificationContainer() {
  const { state, removeNotification } = useApp();

  return (
    <div className="notification-container">
      {state.notifications.map((notif) => {
        const Icon = iconMap[notif.type] || Info;
        return (
          <div key={notif.id} className={`notification ${notif.type}`}>
            <Icon className="notification-icon" />
            <div className="notification-content">
              <div className="notification-title">{notif.title}</div>
              {notif.message && (
                <div className="notification-message">{notif.message}</div>
              )}
            </div>
            <button
              className="notification-close"
              onClick={() => removeNotification(notif.id)}
            >
              <X size={14} />
            </button>
          </div>
        );
      })}
    </div>
  );
}
