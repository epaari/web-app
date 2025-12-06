import { useState } from 'react';
import Chapters from './components/Chapters';
import ChapterView from './components/ChapterView';
import './App.css';

function App() {
  const [selectedChapter, setSelectedChapter] = useState(null);

  const handleChapterSelect = (chapter) => {
    setSelectedChapter(chapter);
  };

  const handleBackToChapters = () => {
    setSelectedChapter(null);
  };

  return (
    <div className="app">
      {selectedChapter ? (
        <ChapterView
          chapter={selectedChapter}
          onBack={handleBackToChapters}
        />
      ) : (
        <Chapters onChapterSelect={handleChapterSelect} />
      )}
    </div>
  );
}

export default App;
