import { BrowserRouter } from "react-router-dom";
import { AnalysisSessionProvider } from "./context/AnalysisSessionContext";
import AppRouter from "./routes/AppRouter";

function App() {
  return (
    <BrowserRouter>
      <AnalysisSessionProvider>
        <AppRouter />
      </AnalysisSessionProvider>
    </BrowserRouter>
  );
}

export default App;
