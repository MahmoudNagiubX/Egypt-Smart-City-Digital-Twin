import { useEffect } from "react";
import { Dashboard } from "./components/Dashboard";

export const APP_TITLE = "Egypt Smart City Digital Twin";

const App = () => {
  useEffect(() => {
    document.title = APP_TITLE;
  }, []);

  return <Dashboard />;
};

export default App;
