import React, { useMemo, useState } from 'react';

import {
  Badge,
  Button,
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  Input,
  Separator,
  Textarea,
} from './ui';

export type CampaignTaskNode = {
  id: string;
  title: string;
  type: 'analyze_trends' | 'generate_content' | 'post_content' | 'reply_comment' | 'execute_transaction';
  priority: 'high' | 'medium' | 'low';
  children?: CampaignTaskNode[];
};

function typeBadge(type: CampaignTaskNode['type']): { label: string; className: string } {
  switch (type) {
    case 'analyze_trends':
      return { label: 'Analyze', className: 'bg-indigo-600 text-white' };
    case 'generate_content':
      return { label: 'Generate', className: 'bg-sky-600 text-white' };
    case 'post_content':
      return { label: 'Post', className: 'bg-emerald-600 text-white' };
    case 'reply_comment':
      return { label: 'Engage', className: 'bg-amber-500 text-white' };
    case 'execute_transaction':
      return { label: 'Commerce', className: 'bg-rose-600 text-white' };
    default:
      return { label: 'Task', className: 'bg-slate-900 text-white' };
  }
}

function priorityBadge(p: CampaignTaskNode['priority']): { label: string; className: string } {
  switch (p) {
    case 'high':
      return { label: 'High', className: 'bg-slate-900 text-white' };
    case 'medium':
      return { label: 'Medium', className: 'bg-slate-200 text-slate-900' };
    case 'low':
    default:
      return { label: 'Low', className: 'bg-slate-100 text-slate-700' };
  }
}

function mockDecomposeGoal(goal: string): CampaignTaskNode[] {
  const g = goal.trim() || 'New campaign';
  return [
    {
      id: 't1',
      title: `Research trends for: ${g}`,
      type: 'analyze_trends',
      priority: 'high',
      children: [
        {
          id: 't1.1',
          title: 'Fetch trending topics (news)',
          type: 'analyze_trends',
          priority: 'high',
        },
        {
          id: 't1.2',
          title: 'Score relevance vs campaign persona',
          type: 'analyze_trends',
          priority: 'medium',
        },
      ],
    },
    {
      id: 't2',
      title: 'Draft platform copy',
      type: 'generate_content',
      priority: 'medium',
      children: [
        {
          id: 't2.1',
          title: 'Write post with AI disclosure',
          type: 'generate_content',
          priority: 'medium',
        },
        {
          id: 't2.2',
          title: 'Create asset (image or text-only)',
          type: 'generate_content',
          priority: 'low',
        },
      ],
    },
    {
      id: 't3',
      title: 'Publish and monitor engagement',
      type: 'post_content',
      priority: 'medium',
      children: [
        {
          id: 't3.1',
          title: 'Publish to Twitter / Instagram',
          type: 'post_content',
          priority: 'medium',
        },
        {
          id: 't3.2',
          title: 'Reply to mentions and comments',
          type: 'reply_comment',
          priority: 'low',
        },
      ],
    },
  ];
}

function TreeNode(props: { node: CampaignTaskNode; depth?: number }) {
  const depth = props.depth ?? 0;
  const tb = typeBadge(props.node.type);
  const pb = priorityBadge(props.node.priority);

  return (
    <div className="min-w-0">
      <div
        className={[
          'flex min-w-0 flex-col gap-2 rounded-xl border border-slate-200 bg-white p-3',
          depth === 0 ? 'shadow-sm' : '',
        ].join(' ')}
        style={{ marginLeft: depth * 12 }}
      >
        <div className="flex flex-wrap items-start justify-between gap-2">
          <div className="min-w-0">
            <div className="truncate text-sm font-semibold text-slate-900">{props.node.title}</div>
            <div className="mt-1 text-xs text-slate-500">Task ID: {props.node.id}</div>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <Badge className={tb.className}>{tb.label}</Badge>
            <Badge className={pb.className}>{pb.label}</Badge>
          </div>
        </div>
      </div>

      {props.node.children && props.node.children.length > 0 ? (
        <div className="mt-2 space-y-2">
          {props.node.children.map((c) => (
            <TreeNode key={c.id} node={c} depth={depth + 1} />
          ))}
        </div>
      ) : null}
    </div>
  );
}

export function CampaignComposer(props: {
  onSubmitGoal?: (goal: string) => void;
  onStartCampaign?: (goal: string) => void;
}) {
  const [campaignName, setCampaignName] = useState('New Campaign');
  const [goal, setGoal] = useState('Promote AI agent workflows to a Gen-Z audience in Ethiopia');
  const [constraints, setConstraints] = useState(
    '- Must include AI disclosure\n- Avoid sensitive topics (politics/health/finance)\n- Keep tone professional + engaging'
  );
  const [generated, setGenerated] = useState<CampaignTaskNode[] | null>(null);

  const count = useMemo(() => {
    function walk(nodes: CampaignTaskNode[] | undefined): number {
      if (!nodes) return 0;
      return nodes.reduce((acc, n) => acc + 1 + walk(n.children), 0);
    }
    return walk(generated ?? undefined);
  }, [generated]);

  return (
    <div className="space-y-4">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h2 className="text-lg sm:text-xl font-bold tracking-tight text-slate-900">
            Campaign Composer
          </h2>
          <p className="mt-1 text-sm text-slate-600">
            Write a high-level goal and preview the Planner’s task tree before execution.
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Badge variant="outline" className="bg-white">
            Spec: UI 1.1
          </Badge>
          {generated ? (
            <Badge className="bg-slate-900 text-white">Tasks: {count}</Badge>
          ) : (
            <Badge variant="outline" className="bg-white">
              No plan generated
            </Badge>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <Card className="border-slate-200">
          <CardHeader>
            <CardTitle className="text-base">Define campaign intent</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="space-y-2">
              <label className="text-sm font-semibold text-slate-900">Campaign name</label>
              <Input value={campaignName} onChange={(e) => setCampaignName(e.target.value)} />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-semibold text-slate-900">Goal</label>
              <Textarea
                value={goal}
                onChange={(e) => setGoal(e.target.value)}
                className="min-h-[120px]"
                placeholder="e.g., Hype up the new sneaker drop to Gen-Z audience"
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-semibold text-slate-900">Constraints / guardrails</label>
              <Textarea
                value={constraints}
                onChange={(e) => setConstraints(e.target.value)}
                className="min-h-[110px]"
              />
              <p className="text-xs text-slate-500">
                These become persona constraints + acceptance criteria for Judge/HITL.
              </p>
            </div>

            <Separator />

            <div className="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
              <Button
                variant="outline"
                onClick={() => setGenerated(null)}
                disabled={!generated}
              >
                Clear
              </Button>
              <Button
                variant="outline"
                onClick={() => {
                  const plan = mockDecomposeGoal(goal);
                  setGenerated(plan);
                  props.onSubmitGoal?.(goal);
                }}
              >
                Generate task tree
              </Button>
              <Button
                onClick={() => {
                  const plan = generated ?? mockDecomposeGoal(goal);
                  setGenerated(plan);
                  props.onStartCampaign?.(goal);
                }}
              >
                Start campaign
              </Button>
            </div>
          </CardContent>
        </Card>

        <Card className="border-slate-200">
          <CardHeader className="gap-2 sm:flex-row sm:items-center sm:justify-between">
            <CardTitle className="text-base">Planner preview</CardTitle>
            <div className="flex flex-wrap gap-2">
              <Badge variant="outline" className="bg-white">
                {campaignName || 'Untitled'}
              </Badge>
              {generated ? (
                <Badge className="bg-emerald-600 text-white">Ready</Badge>
              ) : (
                <Badge className="bg-amber-500 text-white">Draft</Badge>
              )}
            </div>
          </CardHeader>
          <CardContent className="space-y-3">
            {generated ? (
              <div className="space-y-3">
                {generated.map((n) => (
                  <TreeNode key={n.id} node={n} />
                ))}
              </div>
            ) : (
              <div className="rounded-xl border border-dashed border-slate-200 bg-white p-6 text-sm text-slate-600">
                Generate a task tree to preview the Planner’s decomposition. In a full
                implementation this would call the Planner service and display the DAG.
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

export default CampaignComposer;

