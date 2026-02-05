/**
 * HITL Dashboard Component
 * ReviewCard - Human-in-the-Loop review interface
 * 
 * From SRS 5.1: UI Integration for HITL
 */

import React, { useState } from 'react';
import { 
  Card, 
  CardHeader, 
  CardTitle, 
  CardContent,
  Badge,
  Button,
  Textarea
} from './ui';

interface ReviewCardProps {
  /** Generated content to review */
  generated_content: string | { type: string; url: string };
  /** Confidence score (0.0 - 1.0) */
  confidence_score: number;
  /** Reasoning trace from Judge */
  reasoning_trace: string;
  /** Task ID */
  task_id: string;
  /** Platform */
  platform?: string;
  /** Callback when approved */
  onApprove: (taskId: string, editedContent?: string) => void;
  /** Callback when rejected */
  onReject: (taskId: string, reason: string) => void;
}

export function ReviewCard({
  generated_content,
  confidence_score,
  reasoning_trace,
  task_id,
  platform = 'twitter',
  onApprove,
  onReject
}: ReviewCardProps) {
  const [editedContent, setEditedContent] = useState('');
  const [rejectReason, setRejectReason] = useState('');
  const [showRejectForm, setShowRejectForm] = useState(false);

  // Get confidence badge color
  const getConfidenceColor = (score: number): string => {
    if (score >= 0.9) return 'bg-emerald-600';
    if (score >= 0.7) return 'bg-amber-500';
    return 'bg-rose-600';
  };

  // Get confidence label
  const getConfidenceLabel = (score: number): string => {
    if (score >= 0.90) return 'High';
    if (score >= 0.70) return 'Medium';
    return 'Low';
  };

  // Determine if high attention needed
  const highAttentionNeeded = confidence_score < 0.80;

  return (
    <Card
      className={[
        'w-full min-w-0',
        highAttentionNeeded ? 'border-rose-300 ring-2 ring-rose-200/60' : 'border-slate-200',
      ].join(' ')}
    >
      <CardHeader className="gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="min-w-0">
          <CardTitle className="text-base sm:text-lg">Content Review</CardTitle>
          <p className="mt-1 text-xs sm:text-sm text-slate-500">
            Verify policy compliance, tone, and AI disclosure before publishing.
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-xs sm:text-sm text-slate-500">Confidence</span>
          <Badge className={`${getConfidenceColor(confidence_score)} text-white`}>
            {getConfidenceLabel(confidence_score)} · {confidence_score.toFixed(2)}
          </Badge>
          {platform && <Badge variant="outline" className="capitalize">{platform}</Badge>}
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-2 text-xs text-slate-500">
          <span className="truncate">Task ID: {task_id}</span>
          {highAttentionNeeded ? (
            <span className="inline-flex items-center gap-2 rounded-full bg-rose-50 px-2.5 py-1 text-rose-700 ring-1 ring-rose-200">
              High attention required
            </span>
          ) : (
            <span className="inline-flex items-center gap-2 rounded-full bg-emerald-50 px-2.5 py-1 text-emerald-700 ring-1 ring-emerald-200">
              Ready for approval
            </span>
          )}
        </div>

        {/* Generated Content Display */}
        <div className="rounded-xl border border-slate-200 bg-white/70 p-4 shadow-sm">
          <h4 className="text-sm font-semibold text-slate-900 mb-2">Generated Content</h4>
          {typeof generated_content === 'string' ? (
            <p className="text-slate-800 whitespace-pre-wrap break-words leading-relaxed">
              {generated_content}
            </p>
          ) : (
            <div className="space-y-2">
              <p className="text-sm text-slate-600">Type: {generated_content.type}</p>
              {generated_content.url && (
                <a 
                  href={generated_content.url} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-2 text-sm font-medium text-indigo-700 hover:text-indigo-800 underline-offset-4 hover:underline"
                >
                  View Media
                </a>
              )}
            </div>
          )}
        </div>

        {/* Reasoning Trace */}
        <div className="rounded-xl bg-gradient-to-br from-indigo-50 to-sky-50 p-4 ring-1 ring-indigo-100">
          <h4 className="text-sm font-semibold mb-2 text-indigo-900">Reasoning Trace</h4>
          <p className="text-sm text-indigo-900/80 leading-relaxed break-words">
            {reasoning_trace}
          </p>
        </div>

        {/* Edit Option */}
        <div className="space-y-2">
          <label className="text-sm font-semibold text-slate-900">Edit Content (optional)</label>
          <Textarea
            value={editedContent}
            onChange={(e) => setEditedContent(e.target.value)}
            placeholder="Enter edited content if changes are needed..."
            className="min-h-[96px]"
          />
          <p className="text-xs text-slate-500">
            Tip: Keep disclosure intact and avoid sensitive-topic claims without review.
          </p>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-col-reverse sm:flex-row sm:justify-end gap-2 sm:gap-3 pt-4 border-t border-slate-200">
          <Button
            variant="outline"
            onClick={() => setShowRejectForm(true)}
            className="border-rose-200 text-rose-700 hover:bg-rose-50"
          >
            Reject
          </Button>
          <Button
            variant="outline"
            onClick={() => onApprove(task_id, editedContent || undefined)}
            className="border-amber-200 text-amber-900 hover:bg-amber-50"
          >
            Request Changes
          </Button>
          <Button
            onClick={() => onApprove(task_id, editedContent || undefined)}
            className="bg-emerald-600 hover:bg-emerald-700 text-white"
          >
            Approve & Publish
          </Button>
        </div>

        {/* Reject Form */}
        {showRejectForm && (
          <div className="rounded-xl border border-rose-200 bg-rose-50 p-4 space-y-3">
            <h4 className="text-sm font-semibold text-rose-900">Reject Content</h4>
            <Textarea
              value={rejectReason}
              onChange={(e) => setRejectReason(e.target.value)}
              placeholder="Reason for rejection..."
              className="min-h-[80px]"
            />
            <div className="flex justify-end gap-2">
              <Button
                variant="ghost"
                onClick={() => {
                  setShowRejectForm(false);
                  setRejectReason('');
                }}
              >
                Cancel
              </Button>
              <Button
                variant="destructive"
                onClick={() => {
                  onReject(task_id, rejectReason);
                  setShowRejectForm(false);
                }}
                disabled={!rejectReason.trim()}
              >
                Confirm Rejection
              </Button>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

export default ReviewCard;
