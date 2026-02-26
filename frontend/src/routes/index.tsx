import { Routes, Route } from 'react-router-dom'
import HomePage from '../pages/HomePage'
import VisualizationPage from '../pages/VisualizationPage'
import CodeGenerationPage from '../pages/CodeGenerationPage'

const AppRoutes = () => {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/visualization" element={<VisualizationPage />} />
      <Route path="/code-generation" element={<CodeGenerationPage />} />
    </Routes>
  )
}

export default AppRoutes