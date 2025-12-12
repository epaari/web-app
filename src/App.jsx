import { useState } from 'react';
import SubjectView from './components/SubjectView';
import ChapterView from './components/ChapterView';
import TopicView from './components/TopicView';
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
        <TopicView
          standard={selectedSubject.standard}
          subject={selectedSubject.subject}
          chapter={selectedChapter}
          onBack={handleBackToChapters}
          onHome={handleBackToSubjects}
        />
      ) : selectedSubject ? (
        <ChapterView
          standard={selectedSubject.standard}
          subject={selectedSubject.subject}
          onChapterSelect={handleChapterSelect}
          onHome={handleBackToSubjects}
        />
      ) : (
        <SubjectView onSubjectSelect={handleSubjectSelect} />
      )}
    </div>
  );
}

export default App;
