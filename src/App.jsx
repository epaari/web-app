import { useState } from 'react';
import Subjects from './components/Subjects';
import Chapters from './components/Chapters';
import TopicsView from './components/TopicsView';
import './App.css';

function App() {
  const [selectedSubject, setSelectedSubject] = useState(null);
  const [selectedChapter, setSelectedChapter] = useState(null);

  const handleSubjectSelect = (standard, subject) => {
    setSelectedSubject({ standard, subject });
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
        <TopicsView
          standard={selectedSubject.standard}
          subject={selectedSubject.subject}
          chapter={selectedChapter}
          onBack={handleBackToChapters}
          onHome={handleBackToSubjects}
        />
      ) : selectedSubject ? (
        <Chapters
          standard={selectedSubject.standard}
          subject={selectedSubject.subject}
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
