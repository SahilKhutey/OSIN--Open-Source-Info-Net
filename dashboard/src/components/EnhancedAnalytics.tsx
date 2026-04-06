import React, { useState, useEffect } from 'react';
import { useStore } from '../store/useStore';

interface AnalyticsData {
  totalEvents: number;
  eventDistribution: Record<string, number>;
  confidenceLevels: {
    high: number;
    medium: number;
    low: number;
  };
  geographicSpread: {
    northAmerica: number;
    europe: number;
    asia: number;
    other: number;
  };
  trendingTopics: string[];
  threatAssessment: {
    level: 'low' | 'medium' | 'high' | 'critical';
    factors: string[];
  };
}

export const EnhancedAnalytics: React.FC = () => {
  const { events } = useStore();
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  
  useEffect(() => {
    if (events.length > 0) {
      calculateAnalytics();
    }
  }, [events]);
  
  const calculateAnalytics = () => {
    // Event distribution by platform
    const platformDistribution: Record<string, number> = {};
    events.forEach(event => {
      const platform = event.platform || event.source || 'Unknown';
      platformDistribution[platform] = (platformDistribution[platform] || 0) + 1;
    });
    
    // Confidence level distribution
    const confidenceLevels = {
      high: events.filter(e => (e.confidence || 0) >= 0.7).length,
      medium: events.filter(e => (e.confidence || 0) >= 0.4 && (e.confidence || 0) < 0.7).length,
      low: events.filter(e => (e.confidence || 0) < 0.4).length
    };
    
    // Geographic spread
    const geographicSpread = {
      northAmerica: events.filter(e => 
        e.location && e.location.lat > 25 && e.location.lat < 50 && 
        (e.location.lng || e.location.lon || 0) > -125 && (e.location.lng || e.location.lon || 0) < -65
      ).length,
      europe: events.filter(e => 
        e.location && e.location.lat > 35 && e.location.lat < 70 && 
        (e.location.lng || e.location.lon || 0) > -10 && (e.location.lng || e.location.lon || 0) < 40
      ).length,
      asia: events.filter(e => 
        e.location && e.location.lat > 0 && e.location.lat < 50 && 
        (e.location.lng || e.location.lon || 0) > 60 && (e.location.lng || e.location.lon || 0) < 150
      ).length,
      other: 0
    };
    
    geographicSpread.other = events.filter(e => 
      e.location && !(
        (e.location.lat > 25 && e.location.lat < 50 && (e.location.lng || e.location.lon || 0) > -125 && (e.location.lng || e.location.lon || 0) < -65) ||
        (e.location.lat > 35 && e.location.lat < 70 && (e.location.lng || e.location.lon || 0) > -10 && (e.location.lng || e.location.lon || 0) < 40) ||
        (e.location.lat > 0 && e.location.lat < 50 && (e.location.lng || e.location.lon || 0) > 60 && (e.location.lng || e.location.lon || 0) < 150)
      )
    ).length;
    
    // Trending topics (simple keyword extraction)
    const allText = events.map(e => e.text || e.content || '').join(' ');
    const words = allText.toLowerCase().split(/\W+/);
    const wordFreq: Record<string, number> = {};
    
    words.forEach(word => {
      if (word.length > 3 && !['http', 'https', 'www'].includes(word)) {
        wordFreq[word] = (wordFreq[word] || 0) + 1;
      }
    });
    
    const trendingTopics = Object.entries(wordFreq)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 10)
      .map(([word]) => word);
    
    // Threat assessment (simplified)
    const highConfidenceEvents = events.filter(e => (e.confidence || 0) > 0.8);
    const threatLevel = highConfidenceEvents.length > 10 ? 'high' as const : 
                       highConfidenceEvents.length > 5 ? 'medium' as const : 
                       'low' as const;
    
    const threatFactors = [];
    const allEventText = highConfidenceEvents.map(e => (e.text || e.content || '').toLowerCase()).join(' ');
    
    if (allEventText.includes('violence') || allEventText.includes('attack')) {
      threatFactors.push('Violence reports');
    }
    if (allEventText.includes('protest') || allEventText.includes('demonstration')) {
      threatFactors.push('Protest activity');
    }
    if (allEventText.includes('emergency') || allEventText.includes('crisis')) {
      threatFactors.push('Emergency situations');
    }
    if (allEventText.includes('critical') || allEventText.includes('severe')) {
      threatFactors.push('Critical incidents');
    }
    
    setAnalytics({
      totalEvents: events.length,
      eventDistribution: platformDistribution,
      confidenceLevels,
      geographicSpread,
      trendingTopics,
      threatAssessment: {
        level: threatLevel,
        factors: threatFactors.length > 0 ? threatFactors : ['No significant threats detected']
      }
    });
  };
  
  if (!analytics) {
    return (
      <div className="bg-gray-900 rounded-lg p-4 border border-green-500">
        <div className="text-center py-8">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-green-500 mb-4"></div>
          <p>Calculating analytics...</p>
        </div>
      </div>
    );
  }
  
  const getThreatColor = (level: string) => {
    switch (level) {
      case 'critical': return 'text-red-500';
      case 'high': return 'text-orange-500';
      case 'medium': return 'text-yellow-500';
      default: return 'text-green-500';
    }
  };
  
  const getThreatBgColor = (level: string) => {
    switch (level) {
      case 'critical': return 'bg-red-900';
      case 'high': return 'bg-orange-900';
      case 'medium': return 'bg-yellow-900';
      default: return 'bg-green-900';
    }
  };
  
  return (
    <div className="space-y-6">
      <div className="bg-gray-900 rounded-lg p-4 border border-green-500">
        <h2 className="text-xl font-bold text-blue-400 mb-4">SYSTEM OVERVIEW</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="p-3 bg-gray-800 rounded border border-green-700">
            <div className="text-2xl font-bold text-green-400">{analytics.totalEvents}</div>
            <div className="text-sm text-gray-400">Total Events</div>
          </div>
          <div className="p-3 bg-gray-800 rounded border border-green-700">
            <div className={`text-2xl font-bold ${getThreatColor(analytics.threatAssessment.level)}`}>
              {analytics.threatAssessment.level.toUpperCase()}
            </div>
            <div className="text-sm text-gray-400">Threat Level</div>
          </div>
          <div className="p-3 bg-gray-800 rounded border border-green-700">
            <div className="text-2xl font-bold text-blue-400">
              {Object.keys(analytics.eventDistribution).length}
            </div>
            <div className="text-sm text-gray-400">Platforms</div>
          </div>
          <div className="p-3 bg-gray-800 rounded border border-green-700">
            <div className="text-2xl font-bold text-orange-400">
              {analytics.trendingTopics.length}
            </div>
            <div className="text-sm text-gray-400">Trending Topics</div>
          </div>
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-gray-900 rounded-lg p-4 border border-green-500">
          <h3 className="text-lg font-bold text-blue-400 mb-3">EVENT DISTRIBUTION</h3>
          <div className="space-y-2">
            {Object.entries(analytics.eventDistribution).map(([platform, count]) => (
              <div key={platform} className="flex items-center">
                <div className="w-32 text-sm capitalize">{platform}</div>
                <div className="flex-1 ml-2">
                  <div className="h-4 bg-gray-700 rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-green-500 rounded-full"
                      style={{ width: `${(count / analytics.totalEvents) * 100}%` }}
                    ></div>
                  </div>
                </div>
                <div className="w-12 text-right text-sm">{count}</div>
              </div>
            ))}
          </div>
        </div>
        
        <div className="bg-gray-900 rounded-lg p-4 border border-green-500">
          <h3 className="text-lg font-bold text-blue-400 mb-3">CONFIDENCE LEVELS</h3>
          <div className="space-y-3">
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span>High (&gt;70%)</span>
                <span>{analytics.confidenceLevels.high}</span>
              </div>
              <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-red-500 rounded-full"
                  style={{ width: `${analytics.totalEvents > 0 ? (analytics.confidenceLevels.high / analytics.totalEvents) * 100 : 0}%` }}
                ></div>
              </div>
            </div>
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span>Medium (40-70%)</span>
                <span>{analytics.confidenceLevels.medium}</span>
              </div>
              <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-yellow-500 rounded-full"
                  style={{ width: `${analytics.totalEvents > 0 ? (analytics.confidenceLevels.medium / analytics.totalEvents) * 100 : 0}%` }}
                ></div>
              </div>
            </div>
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span>Low (&lt;40%)</span>
                <span>{analytics.confidenceLevels.low}</span>
              </div>
              <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-green-500 rounded-full"
                  style={{ width: `${analytics.totalEvents > 0 ? (analytics.confidenceLevels.low / analytics.totalEvents) * 100 : 0}%` }}
                ></div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-gray-900 rounded-lg p-4 border border-green-500">
          <h3 className="text-lg font-bold text-blue-400 mb-3">GEOGRAPHIC SPREAD</h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span>North America</span>
              <span>{analytics.geographicSpread.northAmerica} events</span>
            </div>
            <div className="w-full bg-gray-700 rounded-full h-2">
              <div 
                className="bg-blue-500 h-2 rounded-full" 
                style={{ width: `${analytics.totalEvents > 0 ? (analytics.geographicSpread.northAmerica / analytics.totalEvents) * 100 : 0}%` }}
              ></div>
            </div>
            
            <div className="flex justify-between">
              <span>Europe</span>
              <span>{analytics.geographicSpread.europe} events</span>
            </div>
            <div className="w-full bg-gray-700 rounded-full h-2">
              <div 
                className="bg-green-500 h-2 rounded-full" 
                style={{ width: `${analytics.totalEvents > 0 ? (analytics.geographicSpread.europe / analytics.totalEvents) * 100 : 0}%` }}
              ></div>
            </div>
            
            <div className="flex justify-between">
              <span>Asia</span>
              <span>{analytics.geographicSpread.asia} events</span>
            </div>
            <div className="w-full bg-gray-700 rounded-full h-2">
              <div 
                className="bg-orange-500 h-2 rounded-full" 
                style={{ width: `${analytics.totalEvents > 0 ? (analytics.geographicSpread.asia / analytics.totalEvents) * 100 : 0}%` }}
              ></div>
            </div>
            
            <div className="flex justify-between">
              <span>Other Regions</span>
              <span>{analytics.geographicSpread.other} events</span>
            </div>
            <div className="w-full bg-gray-700 rounded-full h-2">
              <div 
                className="bg-purple-500 h-2 rounded-full" 
                style={{ width: `${analytics.totalEvents > 0 ? (analytics.geographicSpread.other / analytics.totalEvents) * 100 : 0}%` }}
              ></div>
            </div>
          </div>
        </div>
        
        <div className="bg-gray-900 rounded-lg p-4 border border-green-500">
          <h3 className="text-lg font-bold text-blue-400 mb-3">TRENDING TOPICS</h3>
          <div className="flex flex-wrap gap-2 mb-6">
            {analytics.trendingTopics.map((topic, index) => (
              <span 
                key={index} 
                className="px-3 py-1 bg-gray-800 border border-green-700 rounded-full text-sm"
              >
                {topic}
              </span>
            ))}
          </div>
          
          <h3 className="text-lg font-bold text-blue-400 mb-3">THREAT ASSESSMENT</h3>
          <div className={`p-3 rounded border border-${analytics.threatAssessment.level === 'high' ? 'orange' : 'green'}-500 ${getThreatBgColor(analytics.threatAssessment.level)}`}>
            <div className="font-bold mb-2">Level: {analytics.threatAssessment.level.toUpperCase()}</div>
            <div className="text-sm">
              {analytics.threatAssessment.factors.length > 0 ? (
                <ul className="list-disc pl-5">
                  {analytics.threatAssessment.factors.map((factor, index) => (
                    <li key={index}>{factor}</li>
                  ))}
                </ul>
              ) : (
                <p>No significant threats detected</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
