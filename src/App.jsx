import { useState } from 'react';
import SubjectView from './components/SubjectView';
import ChapterView from './components/ChapterView';
import TopicView from './components/TopicView';
import './App.css';

function App() {
  const [selectedSubject, setSelectedSubject] = useState(null);
  const [selectedChapter, setSelectedChapter] = useState(null);
  const [viewMode, setViewMode] = useState('teaching'); // 'teaching', 'book-qa', 'board-qa'

  const handleSubjectSelect = (standard, subject) => {
    setSelectedSubject({ standard, subject });
    setViewMode('teaching'); // Reset to teaching when selecting a new subject
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
    setViewMode('teaching'); // Reset to teaching when going back to subjects
  };

  return (
    <div className="app">
      {selectedChapter ? (
        <TopicView
          standard={selectedSubject.standard}
          subject={selectedSubject.subject}
          chapter={selectedChapter}
          viewMode={viewMode}
          onViewModeChange={setViewMode}
          onBack={handleBackToChapters}
          onHome={handleBackToSubjects}
        />
      ) : selectedSubject ? (
        <ChapterView
          standard={selectedSubject.standard}
          subject={selectedSubject.subject}
          viewMode={viewMode}
          onViewModeChange={setViewMode}
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
