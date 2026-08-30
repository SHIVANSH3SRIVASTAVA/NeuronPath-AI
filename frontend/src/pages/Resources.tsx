import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useAppStore } from '../store/useAppStore';
import { getRecommendations } from '../api/resources';
import { Card, CardContent } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Skeleton } from '../components/ui/Skeleton';
import { BookOpen, Video, Code, ExternalLink, Sparkles, Search, Filter, X, Tag } from 'lucide-react';

export default function Resources() {
  const { currentLearner, activeGoalVersion, activeGoal } = useAppStore();
  const [searchParams, setSearchParams] = useSearchParams();
  const skillParam = searchParams.get('skill');
  const skillIdParam = searchParams.get('skillId');
  const resourceIdParam = searchParams.get('id') || searchParams.get('resourceId');
  const searchParam = searchParams.get('search') || searchParams.get('q');

  const [loading, setLoading] = useState(true);
  const [recommendations, setRecommendations] = useState<any[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState(searchParam || '');
  const [selectedType, setSelectedType] = useState<string>('all');
  const [selectedDifficulty, setSelectedDifficulty] = useState<string>('all');

  useEffect(() => {
    if (!currentLearner) return;
    setLoading(true);
    setError(null);
    getRecommendations(currentLearner.id)
      .then(setRecommendations)
      .catch(err => {
        console.error('Recommendations load error:', err);
        setError('Failed to load personalized recommendations.');
      })
      .finally(() => setLoading(false));
  }, [currentLearner, activeGoalVersion, activeGoal?.id]);

  useEffect(() => {
    const q = searchParams.get('search') || searchParams.get('q');
    if (q) {
      setSearchTerm(q);
    }
  }, [searchParams]);

  const clearAllFilters = () => {
    const newParams = new URLSearchParams(searchParams);
    newParams.delete('skill');
    newParams.delete('skillId');
    newParams.delete('id');
    newParams.delete('resourceId');
    newParams.delete('search');
    newParams.delete('q');
    setSearchParams(newParams);
    setSearchTerm('');
    setSelectedType('all');
    setSelectedDifficulty('all');
  };

  const getIcon = (type: string) => {
    const t = (type || '').toLowerCase();
    if (t === 'video') return <Video className="w-3.5 h-3.5" />;
    if (t === 'project' || t === 'practice' || t === 'code') return <Code className="w-3.5 h-3.5" />;
    return <BookOpen className="w-3.5 h-3.5" />;
  };

  if (!currentLearner) {
    return <div className="p-8 text-center text-slate-600 dark:text-slate-300 font-medium">Please complete onboarding to view recommendations.</div>;
  }

  if (loading) {
    return (
      <div className="space-y-6 pb-12 max-w-6xl mx-auto">
        <Skeleton className="h-10 w-1/3" />
        <Skeleton className="h-6 w-1/2" />
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-4">
          <Skeleton className="h-64 rounded-xl" />
          <Skeleton className="h-64 rounded-xl" />
          <Skeleton className="h-64 rounded-xl" />
        </div>
      </div>
    );
  }

  const selectedSkillId = skillIdParam ? parseInt(skillIdParam, 10) : null;
  const selectedSkillName = skillParam ? skillParam.toLowerCase().trim() : '';
  const selectedResourceId = resourceIdParam ? parseInt(resourceIdParam, 10) : null;

  const filteredRecs = recommendations.filter(item => {
    const res = item.resource || item;
    
    // Exact ID match if specified
    if (selectedResourceId && res.id === selectedResourceId) {
      return true;
    }

    // 1. Skill filter from query params
    let matchesSkill = true;
    if (selectedSkillId || selectedSkillName) {
      const resSkillIds = Array.isArray(res.skill_ids) ? res.skill_ids : [];
      const hasSkillId = selectedSkillId ? resSkillIds.includes(selectedSkillId) : false;
      const hasSkillInTitle = selectedSkillName ? res.title.toLowerCase().includes(selectedSkillName) : false;
      const hasSkillInDesc = selectedSkillName ? (res.description || '').toLowerCase().includes(selectedSkillName) : false;
      
      const skillKeywords = selectedSkillName.split(' ').filter(k => k.length > 2);
      const hasKeywordMatch = skillKeywords.some(k => 
        res.title.toLowerCase().includes(k) || (res.description || '').toLowerCase().includes(k)
      );

      matchesSkill = hasSkillId || hasSkillInTitle || hasSkillInDesc || hasKeywordMatch;
    }

    // 2. Search term filter
    const matchesSearch = searchTerm === '' || 
      res.title.toLowerCase().includes(searchTerm.toLowerCase()) || 
      (res.description || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
      (res.provider || '').toLowerCase().includes(searchTerm.toLowerCase());
      
    // 3. Format & Difficulty filters
    const resType = (res.type || '').toLowerCase();
    const matchesType = selectedType === 'all' || 
      (selectedType === 'practice' ? (resType === 'practice' || resType === 'project') : 
       (selectedType === 'article' || selectedType === 'book') ? (resType === 'article' || resType === 'book') :
       resType === selectedType.toLowerCase());
    const matchesDiff = selectedDifficulty === 'all' || (res.difficulty || '').toLowerCase() === selectedDifficulty.toLowerCase();
    
    return matchesSkill && matchesSearch && matchesType && matchesDiff;
  });

  return (
    <div className="space-y-6 pb-12 max-w-6xl mx-auto text-slate-900 dark:text-slate-100">
      <div className="border-b border-slate-200 dark:border-slate-800 pb-5">
        <h1 className="text-3xl font-black text-slate-900 dark:text-white flex items-center gap-2.5 tracking-tight">
          <Sparkles className="w-7 h-7 text-primary-600 dark:text-primary-400" /> Recommended Learning Resources
        </h1>
        <p className="text-slate-600 dark:text-slate-300 mt-1.5 text-sm">
          Algorithmic recommendations ranked by relevance to your skill gaps and learning pace.
        </p>
      </div>

      {/* Active Filter Banner */}
      {(skillParam || resourceIdParam || (searchParam && searchTerm)) && (
        <div className="bg-primary-50 dark:bg-primary-950/70 border border-primary-200 dark:border-primary-800 rounded-xl p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 shadow-2xs">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-primary-100 dark:bg-primary-900 text-primary-700 dark:text-primary-300 shrink-0">
              <Tag className="w-4 h-4" />
            </div>
            <div>
              <span className="text-xs font-bold text-primary-800 dark:text-primary-300 uppercase tracking-wider block">
                {skillParam ? 'Filtered for Skill' : 'Filtered for Resource'}
              </span>
              <p className="text-sm font-bold text-primary-950 dark:text-white">
                {skillParam || searchParam || `Resource #${resourceIdParam}`} <span className="text-xs font-medium text-primary-700 dark:text-primary-300">({filteredRecs.length} matching {filteredRecs.length === 1 ? 'resource' : 'resources'})</span>
              </p>
            </div>
          </div>
          
          <Button 
            variant="outline" 
            size="sm" 
            onClick={clearAllFilters}
            className="border-primary-300 dark:border-primary-700 text-primary-800 dark:text-primary-200 hover:bg-primary-100 dark:hover:bg-primary-900 shrink-0 font-semibold"
          >
            <X className="w-3.5 h-3.5 mr-1.5" /> Clear Filter / Show All
          </Button>
        </div>
      )}

      {/* Filter and Search Bar */}
      <div className="flex flex-col md:flex-row gap-3 items-center justify-between bg-white dark:bg-slate-900 p-4 rounded-xl border border-slate-200 dark:border-slate-800 shadow-2xs">
        <div className="relative w-full md:w-80">
          <Search className="w-4 h-4 text-slate-400 dark:text-slate-400 absolute left-3 top-3" />
          <Input 
            value={searchTerm} 
            onChange={e => setSearchTerm(e.target.value)} 
            placeholder="Search by topic, library or author..."
            className="pl-9 text-sm bg-white dark:bg-slate-800 border-slate-300 dark:border-slate-700 text-slate-900 dark:text-white placeholder:text-slate-400 dark:placeholder:text-slate-400"
          />
        </div>

        <div className="flex flex-wrap gap-2 w-full md:w-auto">
          <div className="flex items-center gap-1.5 text-xs text-slate-600 dark:text-slate-300 font-semibold mr-1">
            <Filter className="w-3.5 h-3.5 text-slate-500 dark:text-slate-400" /> Filter:
          </div>
          <select 
            value={selectedType}
            onChange={e => setSelectedType(e.target.value)}
            className="p-2 text-xs font-medium border border-slate-300 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="all">All Formats</option>
            <option value="course">Courses</option>
            <option value="documentation">Documentation</option>
            <option value="article">Articles & Books</option>
            <option value="video">Videos</option>
            <option value="practice">Hands-on Practice</option>
          </select>

          <select 
            value={selectedDifficulty}
            onChange={e => setSelectedDifficulty(e.target.value)}
            className="p-2 text-xs font-medium border border-slate-300 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="all">All Difficulties</option>
            <option value="beginner">Beginner</option>
            <option value="intermediate">Intermediate</option>
            <option value="advanced">Advanced</option>
          </select>
        </div>
      </div>
      
      {error && <div className="text-red-600 dark:text-red-300 bg-red-50 dark:bg-red-950/50 p-4 rounded-lg border border-red-200 dark:border-red-900 text-sm">{error}</div>}

      {filteredRecs.length === 0 && !error ? (
        <div className="bg-white dark:bg-slate-900 p-12 rounded-xl border border-slate-200 dark:border-slate-800 text-center space-y-3">
          <BookOpen className="w-12 h-12 text-slate-300 dark:text-slate-500 mx-auto" />
          <h3 className="font-bold text-slate-900 dark:text-white text-lg">No matching resources found</h3>
          <p className="text-slate-500 dark:text-slate-400 text-sm max-w-md mx-auto">
            {skillParam 
              ? `We couldn't find resources matching "${skillParam}" with your current filters.`
              : 'Try adjusting your search query or format/difficulty filter settings.'}
          </p>
          {(skillParam || resourceIdParam || searchParam) && (
            <div className="pt-2">
              <Button onClick={clearAllFilters} variant="outline" size="sm">
                View All Recommendations
              </Button>
            </div>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredRecs.map((item, index) => {
            const res = item.resource || item;
            const explanation = item.explanation;
            const score = item.score;
            const duration = res.duration_hours || res.estimated_hours || 2;
            const url = res.url || 'https://docs.python.org/3/';

            return (
              <Card key={res.id || index} className="flex flex-col bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800 hover:border-primary-400 dark:hover:border-primary-500 transition-all shadow-xs hover:shadow-md">
                <CardContent className="p-5 flex-1 flex flex-col">
                  <div className="flex justify-between items-start mb-2.5">
                    <Badge className="capitalize flex items-center gap-1.5 bg-primary-50 dark:bg-primary-950/80 text-primary-800 dark:text-primary-300 border-primary-200 dark:border-primary-700">
                      {getIcon(res.type)} {res.type || 'resource'}
                    </Badge>
                    <div className="flex items-center gap-2">
                      {score !== undefined && (
                        <span className="text-[11px] font-bold text-emerald-800 dark:text-emerald-300 bg-emerald-50 dark:bg-emerald-950/80 border border-emerald-200 dark:border-emerald-700 px-2.5 py-0.5 rounded-full">
                          {Math.round(score)}% match
                        </span>
                      )}
                      <span className="text-xs text-slate-500 dark:text-slate-400 font-semibold">{duration}h</span>
                    </div>
                  </div>

                  <h3 className="font-bold text-base text-slate-900 dark:text-white mb-1 line-clamp-2 leading-snug">{res.title}</h3>
                  <p className="text-xs text-slate-500 dark:text-slate-400 mb-2.5 font-medium">
                    <span className="text-slate-700 dark:text-slate-300 font-semibold">{res.provider}</span> • <span className="capitalize">{res.difficulty || 'All levels'}</span>
                  </p>
                  
                  <p className="text-xs text-slate-700 dark:text-slate-300 mb-3.5 line-clamp-3 leading-relaxed font-normal">
                    {res.description}
                  </p>

                  {explanation && (
                    <div className="text-[11px] text-slate-700 dark:text-slate-300 bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 p-2.5 rounded-lg mb-4 italic leading-tight">
                      💡 {explanation}
                    </div>
                  )}
                  
                  <div className="mt-auto pt-3 border-t border-slate-100 dark:border-slate-800">
                    <a
                      href={url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center justify-center w-full px-4 py-2.5 text-xs font-bold text-primary-700 dark:text-primary-300 bg-primary-50 dark:bg-primary-950/80 hover:bg-primary-100 dark:hover:bg-primary-900 rounded-lg transition-colors border border-primary-200 dark:border-primary-800 shadow-2xs"
                    >
                      <ExternalLink className="w-3.5 h-3.5 mr-1.5" /> Start Learning Resource
                    </a>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}
