import { useApp } from '../../store/AppContext';
import { CheckCircle, Info, AlertTriangle, ArrowDown, ArrowUp, Zap } from 'lucide-react';

const iconMap = {
  success: CheckCircle,
  info: Info,
  warning: AlertTriangle,
  download: ArrowDown,
  upload: ArrowUp,
};

export default function ActivityPanel() {
  const { state } = useApp();
  const recent = state.activities.slice(0, 6);

  return (
    <div className="activity-panel">
      <div className="activity-panel-item info">
        <Zap size={13} />
        <span>Live</span>
      </div>
      {recent.map((activity) => {
        const Icon = iconMap[activity.type] || Info;
        return (
          <div key={activity.id} className={`activity-panel-item ${activity.type}`}>
            <Icon />
            <span>{activity.message}</span>
          </div>
        );
      })}
      {recent.length === 0 && (
        <div className="activity-panel-item">
          <span>No recent activity</span>
        </div>
      )}
    </div>
  );
}
