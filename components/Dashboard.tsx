import React from 'react';

import { ReviewCard } from './ReviewCard';
import { Badge, Button, Card, CardContent, CardHeader, CardTitle } from './ui';

type ReviewItem = {
  task_id: string;
  platform: string;
  confidence_score: number;
  reasoning_trace: string;
  generated_content: string | { type: string; url: string };
};

const demo: ReviewItem[] = [
  {
    task_id: 'task_8b2f1a',
    platform: 'twitter',
    confidence_score: 0.93,
    reasoning_trace:
      'High confidence. Includes AI disclosure. No sensitive-topic claims. Tone is professional and engaging.',
    generated_content:
      'AI agents are moving from “cool demos” to real workflows.\n\nIf you’re building with them, start with a narrow loop: one task, clear guardrails, tight feedback. Then scale.',
  },
  {
    task_id: 'task_2c91dd',
    platform: 'instagram',
    confidence_score: 0.76,
    reasoning_trace:
      'Medium confidence. Copy is fine, but add clearer AI disclosure and remove any implication of financial advice.',
    generated_content:
      'Quick note: Automation is changing how teams ship. Try: define one repetitive step, automate it, measure the win, repeat.\n\n(Disclosure: AI-assisted draft.)',
  },
];

export function Dashboard(props: {
  items?: ReviewItem[];
  onApprove?: (taskId: string, editedContent?: string) => void;
  onReject?: (taskId: string, reason: string) => void;
}) {
  const items = props.items ?? demo;
  const onApprove =
    props.onApprove ??
    ((taskId: string) => {
      // placeholder for integration with Judge/HITL API
      console.log('Approved', taskId);
    });
  const onReject =
    props.onReject ??
    ((taskId: string, reason: string) => {
      console.log('Rejected', taskId, reason);
    });

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 via-white to-slate-50">
      <div className="mx-auto w-full max-w-6xl px-4 py-6 sm:px-6 sm:py-10">
        <header className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
          <div className="min-w-0">
            <div className="flex flex-wrap items-center gap-2">
              <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-slate-900">
                HITL Review Dashboard
              </h1>
              <Badge variant="outline" className="bg-white">
                Live queue
              </Badge>
            </div>
            <p className="mt-2 text-sm text-slate-600">
              Review generated content, request edits, or escalate before publishing.
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            <Button variant="outline">Refresh</Button>
            <Button>Queue Settings</Button>
          </div>
        </header>

        <section className="mt-6 grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <Card className="border-slate-200">
            <CardHeader>
              <CardTitle className="text-sm">Pending reviews</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-slate-900">{items.length}</div>
              <div className="mt-1 text-xs text-slate-500">Across platforms</div>
            </CardContent>
          </Card>
          <Card className="border-slate-200">
            <CardHeader>
              <CardTitle className="text-sm">High attention</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-slate-900">
                {items.filter((i) => i.confidence_score < 0.8).length}
              </div>
              <div className="mt-1 text-xs text-slate-500">Below 0.80 confidence</div>
            </CardContent>
          </Card>
          <Card className="border-slate-200">
            <CardHeader>
              <CardTitle className="text-sm">Auto-approvable</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-slate-900">
                {items.filter((i) => i.confidence_score >= 0.9).length}
              </div>
              <div className="mt-1 text-xs text-slate-500">At or above 0.90</div>
            </CardContent>
          </Card>
          <Card className="border-slate-200">
            <CardHeader>
              <CardTitle className="text-sm">SLA</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-slate-900">5m</div>
              <div className="mt-1 text-xs text-slate-500">Target time-to-review</div>
            </CardContent>
          </Card>
        </section>

        <main className="mt-6 grid grid-cols-1 gap-4 lg:grid-cols-2">
          {items.map((item) => (
            <ReviewCard
              key={item.task_id}
              generated_content={item.generated_content}
              confidence_score={item.confidence_score}
              reasoning_trace={item.reasoning_trace}
              task_id={item.task_id}
              platform={item.platform}
              onApprove={onApprove}
              onReject={onReject}
            />
          ))}
        </main>
      </div>
    </div>
  );
}

export default Dashboard;

