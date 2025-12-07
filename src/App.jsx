import { useState } from 'react';
import Subjects from './components/Subjects';
import Chapters from './components/Chapters';
import Topics from './components/Topics';
import './App.css';

function App() {
  const [selectedSubject, setSelectedSubject] = useState(null);
  const [selectedChapter, setSelectedChapter] = useState(null);

  const handleSubjectSelect = (standard, subjectName) => {
    setSelectedSubject({ standard, subjectName });
  };

  const handleChapterSelect = (chapter) => {
    setSelectedChapter(chapter);
  };

  const handleBackToChapters = () => {
    setSelectedChapter(null);
  };

  const handleBackToSubjects = () => {
    setSelectedSubject(null);
    setSelectedChapter(null);
  };

  return (
    <div className="app">
      {selectedChapter ? (
        <Topics
          chapter={selectedChapter}
          onBack={handleBackToChapters}
          onHome={handleBackToSubjects}
        />
      ) : selectedSubject ? (
        <Chapters
          onChapterSelect={handleChapterSelect}
          onHome={handleBackToSubjects}
        />
      ) : (
        <Subjects onSubjectSelect={handleSubjectSelect} />
      )}
    </div>
  );
}

export default App;
