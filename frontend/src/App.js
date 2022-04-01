
import  { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Instructions from './Pages/Instructions';
import Registration from './Pages/Registration';
import ErrorPage from './Pages/ErrorPage';
import Challenge from './Pages/Challenge';
import Footer from './Footer';


const App = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Registration />} />
        <Route path="/about" element={<Instructions />} />
        <Route path="/challenge" element={<Challenge />} />
        <Route path="*" element={<ErrorPage />} />
      </Routes>
      <Footer className="copyright"/>
    </Router>
  )
}

export default App;