import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { base44 } from '@/api/base44Client';
import { Camera, Eye, AlertTriangle, CheckCircle, Loader2, Upload, Scan } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

const statusConfig = {
  online: { color: 'bg-accent text-accent-foreground', dot: 'bg-accent' },
  offline: { color: 'bg-muted text-muted-foreground', dot: 'bg-muted-foreground' },
  processing: { color: 'bg-primary/20 text-primary', dot: 'bg-primary' },
  error: { color: 'bg-destructive/20 text-destructive', dot: 'bg-destructive' },
};

export default function VisionModule() {
  const [selectedFeed, setSelectedFeed] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);

  const { data: feeds = [] } = useQuery({
    queryKey: ['camera-feeds'],
    queryFn: () => base44.entities.CameraFeed.list(),
    initialData: [],
  });

  const analyzeImage = async (file) => {
    setAnalyzing(true);
    setAnalysisResult(null);
    const { file_url } = await base44.integrations.Core.UploadFile({ file });
    const result = await base44.integrations.Core.InvokeLLM({
      prompt: `You are an expert manufacturing quality inspector AI. Analyze this production line image for:
1. Defects or anomalies visible
2. Safety compliance issues
3. Equipment condition assessment
4. Overall quality rating (1-10)
Provide specific, actionable findings.`,
      file_urls: [file_url],
      response_json_schema: {
        type: "object",
        properties: {
          defects_found: { type: "array", items: { type: "object", properties: { type: { type: "string" }, severity: { type: "string" }, description: { type: "string" } } } },
          safety_issues: { type: "array", items: { type: "string" } },
          equipment_condition: { type: "string" },
          quality_rating: { type: "number" },
          recommendations: { type: "array", items: { type: "string" } },
        }
      }
    });
    setAnalysisResult(result);
    setAnalyzing(false);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground">Vision Module</h1>
          <p className="text-sm text-muted-foreground mt-1">AI-powered visual inspection & defect detection</p>
        </div>
        <label className="cursor-pointer">
          <Button className="bg-primary text-primary-foreground hover:bg-primary/90">
            <Upload className="w-4 h-4 mr-2" />
            Analyze Image
          </Button>
          <input
            type="file"
            accept="image/*"
            className="hidden"
            onChange={(e) => {
              if (e.target.files?.[0]) analyzeImage(e.target.files[0]);
            }}
          />
        </label>
      </div>

      {/* Camera Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {feeds.map((feed) => {
          const status = statusConfig[feed.status] || statusConfig.offline;
          return (
            <Card
              key={feed.id}
              className={cn(
                "bg-card border-border cursor-pointer transition-all hover:border-primary/30",
                selectedFeed?.id === feed.id && "border-primary/30"
              )}
              onClick={() => setSelectedFeed(feed)}
            >
              <CardContent className="p-4">
                {/* Simulated camera view */}
                <div className="aspect-video rounded-lg bg-secondary mb-3 flex items-center justify-center relative overflow-hidden">
                  {feed.stream_url ? (
                    <img src={feed.stream_url} alt={feed.name} className="w-full h-full object-cover" />
                  ) : (
                    <Camera className="w-8 h-8 text-muted-foreground/30" />
                  )}
                  <div className="absolute top-2 left-2 flex items-center gap-1.5 px-2 py-1 bg-black/60 rounded-full">
                    <div className={cn("w-1.5 h-1.5 rounded-full", status.dot, feed.status === 'online' && "animate-pulse-glow")} />
                    <span className="text-[10px] font-medium text-white">{feed.status}</span>
                  </div>
                  {feed.fps && (
                    <div className="absolute top-2 right-2 px-2 py-1 bg-black/60 rounded-full text-[10px] text-white font-mono">
                      {feed.fps} FPS
                    </div>
                  )}
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-semibold text-sm text-foreground">{feed.name}</p>
                    <p className="text-xs text-muted-foreground">{feed.location}</p>
                  </div>
                  <Badge variant="outline" className="text-[10px]">{feed.type?.replace(/_/g, ' ')}</Badge>
                </div>
                <div className="mt-3 grid grid-cols-3 gap-2">
                  <div className="text-center">
                    <p className="text-lg font-bold text-foreground">{feed.detections_today || 0}</p>
                    <p className="text-[10px] text-muted-foreground">Detections</p>
                  </div>
                  <div className="text-center">
                    <p className="text-lg font-bold text-destructive">{feed.defects_today || 0}</p>
                    <p className="text-[10px] text-muted-foreground">Defects</p>
                  </div>
                  <div className="text-center">
                    <p className="text-lg font-bold text-accent">{feed.accuracy || '--'}%</p>
                    <p className="text-[10px] text-muted-foreground">Accuracy</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          );
        })}
        {feeds.length === 0 && (
          <div className="col-span-full bg-card border border-border rounded-xl p-12 text-center text-muted-foreground">
            <Camera className="w-12 h-12 mx-auto mb-3 opacity-30" />
            <p>No camera feeds configured</p>
          </div>
        )}
      </div>

      {/* AI Analysis Results */}
      {analyzing && (
        <Card className="bg-card border-primary/20">
          <CardContent className="flex items-center justify-center py-12">
            <Loader2 className="w-8 h-8 text-primary animate-spin mr-3" />
            <span className="text-muted-foreground">Analyzing image with AI vision model...</span>
          </CardContent>
        </Card>
      )}

      {analysisResult && (
        <Card className="bg-card border-primary/20">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-primary">
              <Scan className="w-5 h-5" />
              AI Vision Analysis
              <span className="ml-auto text-2xl font-bold">{analysisResult.quality_rating}/10</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {analysisResult.defects_found?.length > 0 && (
              <div>
                <h4 className="text-sm font-semibold text-foreground mb-2 flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4 text-destructive" /> Defects Found
                </h4>
                <div className="space-y-2">
                  {analysisResult.defects_found.map((d, i) => (
                    <div key={i} className="bg-destructive/5 border border-destructive/20 rounded-lg p-3">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-semibold text-sm text-foreground">{d.type}</span>
                        <Badge className="bg-destructive/20 text-destructive text-[10px]">{d.severity}</Badge>
                      </div>
                      <p className="text-xs text-muted-foreground">{d.description}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {analysisResult.recommendations?.length > 0 && (
              <div>
                <h4 className="text-sm font-semibold text-foreground mb-2 flex items-center gap-2">
                  <CheckCircle className="w-4 h-4 text-accent" /> Recommendations
                </h4>
                <ul className="space-y-1">
                  {analysisResult.recommendations.map((r, i) => (
                    <li key={i} className="text-sm text-muted-foreground flex items-start gap-2">
                      <span className="text-accent mt-0.5">•</span>{r}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            <p className="text-sm text-muted-foreground">
              <strong className="text-foreground">Equipment:</strong> {analysisResult.equipment_condition}
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}