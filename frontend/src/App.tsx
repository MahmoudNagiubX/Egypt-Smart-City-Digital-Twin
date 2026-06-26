import { useEffect, useState } from 'react';
import { Dashboard } from './components/Dashboard';
import { WelcomePage } from './components/WelcomePage';

export const APP_TITLE = 'Geo Weather';

const App = () => {
  const [showDashboard, setShowDashboard] = useState(false);

  useEffect(() => {
    document.title = showDashboard ? APP_TITLE : 'Geo Weather — Nasr City Weather Impact & Urban Heat Risk Dashboard';
  }, [showDashboard]);

  if (!showDashboard) {
    return <WelcomePage onOpenDashboard={() => setShowDashboard(true)} />;
  }
  return <Dashboard onGoHome={() => setShowDashboard(false)} />;
};

export default App;
