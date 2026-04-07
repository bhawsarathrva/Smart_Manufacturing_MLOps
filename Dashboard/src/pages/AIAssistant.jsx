import React, { useState, useRef, useEffect } from 'react';
import { base44 } from '@/api/base44Client';
import { Send, Loader2, Bot, User, Sparkles } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { cn } from '@/lib/utils';
import ReactMarkdown from 'react-markdown';

const SUGGESTED_PROMPTS = [
  "What's the current OEE across all machines?",
  "Which machines are at risk of failure?",
  "Analyze today's production quality trends",
  "Suggest maintenance schedule optimization",
  "Explain anomaly patterns in sensor data",
  "How can we reduce defect rate by 5%?",
];

export default function AIAssistant() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' });
  }, [messages]);

  const sendMessage = async (text) => {
    if (!text.trim()) return;
    const userMsg = { role: 'user', content: text };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    // Gather context
    let machines = [], alerts = [], batches = [];
    try {
      [machines, alerts, batches] = await Promise.all([
        base44.entities.Machine.list(),
        base44.entities.Alert.list('-created_date', 10),
        base44.entities.ProductionBatch.list('-created_date', 5),
      ]);
    } catch (e) { /* context fetch best effort */ }

    const context = `
CURRENT FACTORY STATUS:
- Machines: ${JSON.stringify(machines.map(m => ({ name: m.name, status: m.status, oee: m.oee_score, temp: m.temperature, vibration: m.vibration, power: m.power_consumption })))}
- Recent Alerts: ${JSON.stringify(alerts.map(a => ({ title: a.title, severity: a.severity, type: a.type, status: a.status })))}
- Recent Batches: ${JSON.stringify(batches.map(b => ({ batch: b.batch_number, product: b.product_name, status: b.status, produced: b.produced_quantity, defects: b.defect_count, yield: b.yield_rate })))}
`;

    const result = await base44.integrations.Core.InvokeLLM({
      prompt: `You are SmartFactory AI, an expert manufacturing intelligence assistant. You have access to real-time factory data.

${context}

Previous conversation: ${JSON.stringify(messages.slice(-6))}

User question: ${text}

Provide actionable, data-driven responses. Use specific numbers from the factory data when available. Be concise but thorough. Use markdown formatting.`,
    });

    setMessages(prev => [...prev, { role: 'assistant', content: result }]);
    setLoading(false);
  };

  return (
    <div className="h-[calc(100vh-7rem)] flex flex-col">
      <div className="mb-4">
        <h1 className="text-2xl font-bold text-foreground">AI Manufacturing Assistant</h1>
        <p className="text-sm text-muted-foreground mt-1">GenAI-powered insights for your production floor</p>
      </div>

      {/* Chat Area */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto bg-card border border-border rounded-xl p-4 space-y-4 mb-4">
        {messages.length === 0 && (
          <div className="h-full flex flex-col items-center justify-center">
            <Sparkles className="w-12 h-12 text-primary/30 mb-4" />
            <p className="text-lg font-semibold text-foreground mb-2">SmartFactory AI</p>
            <p className="text-sm text-muted-foreground mb-6 text-center max-w-md">
              Ask me anything about your production floor — machine health, quality predictions, maintenance scheduling, and more.
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 max-w-lg">
              {SUGGESTED_PROMPTS.map((prompt) => (
                <button
                  key={prompt}
                  onClick={() => sendMessage(prompt)}
                  className="text-left text-xs px-3 py-2.5 rounded-lg bg-secondary border border-border text-muted-foreground hover:text-foreground hover:border-primary/30 transition-all"
                >
                  {prompt}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg, i) => (
          <div key={i} className={cn("flex gap-3", msg.role === 'user' ? "justify-end" : "justify-start")}>
            {msg.role === 'assistant' && (
              <div className="w-8 h-8 rounded-lg bg-primary/10 border border-primary/20 flex items-center justify-center shrink-0 mt-0.5">
                <Bot className="w-4 h-4 text-primary" />
              </div>
            )}
            <div className={cn(
              "max-w-[80%] rounded-xl px-4 py-3",
              msg.role === 'user'
                ? "bg-primary text-primary-foreground"
                : "bg-secondary border border-border"
            )}>
              {msg.role === 'user' ? (
                <p className="text-sm">{msg.content}</p>
              ) : (
                <ReactMarkdown className="text-sm prose prose-sm prose-invert max-w-none [&>*:first-child]:mt-0 [&>*:last-child]:mb-0">
                  {msg.content}
                </ReactMarkdown>
              )}
            </div>
            {msg.role === 'user' && (
              <div className="w-8 h-8 rounded-lg bg-secondary border border-border flex items-center justify-center shrink-0 mt-0.5">
                <User className="w-4 h-4 text-muted-foreground" />
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-primary/10 border border-primary/20 flex items-center justify-center">
              <Bot className="w-4 h-4 text-primary" />
            </div>
            <div className="bg-secondary border border-border rounded-xl px-4 py-3">
              <Loader2 className="w-4 h-4 text-primary animate-spin" />
            </div>
          </div>
        )}
      </div>

      {/* Input */}
      <div className="flex gap-3">
        <Textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault();
              sendMessage(input);
            }
          }}
          placeholder="Ask about machine health, production metrics, quality predictions..."
          className="resize-none h-12 bg-card border-border"
          rows={1}
        />
        <Button
          onClick={() => sendMessage(input)}
          disabled={loading || !input.trim()}
          className="bg-primary text-primary-foreground hover:bg-primary/90 h-12 px-6"
        >
          <Send className="w-4 h-4" />
        </Button>
      </div>
    </div>
  );
}