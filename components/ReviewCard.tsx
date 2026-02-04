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
} from '@/components/ui';

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
    if (score >= 0.90) return 'bg-green-500';
    if (score >= 0.70) return 'bg-yellow-500';
    return 'bg-red-500';
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
    <Card className={`w-full max-w-2xl ${
      highAttentionNeeded ? 'border-red-500 border-2' : ''
    }`}>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle className="text-lg">Content Review</CardTitle>
        <div className="flex items-center gap-2">
          <span className="text-sm text-gray-500">Confidence:</span>
          <Badge className={`${getConfidenceColor(confidence_score)} text-white`}>
            {getConfidenceLabel(confidence_score)} ({confidence_score.toFixed(2)})
          </Badge>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Task ID */}
        <div className="text-xs text-gray-400">
          Task ID: {task_id}
        </div>

        {/* Platform */}
        {platform && (
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium">Platform:</span>
            <Badge variant="outline">{platform}</Badge>
          </div>
        )}

        {/* Generated Content Display */}
        <div className="p-4 bg-gray-50 rounded-lg border">
          <h4 className="text-sm font-medium mb-2">Generated Content:</h4>
          {typeof generated_content === 'string' ? (
            <p className="text-gray-800 whitespace-pre-wrap">
              {generated_content}
            </p>
          ) : (
            <div className="space-y-2">
              <p className="text-sm text-gray-500">
                Type: {generated_content.type}
              </p>
              {generated_content.url && (
                <a 
                  href={generated_content.url} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:underline"
                >
                  View Media
                </a>
              )}
            </div>
          )}
        </div>

        {/* Reasoning Trace */}
        <div className="p-4 bg-blue-50 rounded-lg">
          <h4 className="text-sm font-medium mb-2 text-blue-800">
            Reasoning Trace:
          </h4>
          <p className="text-sm text-blue-700">
            {reasoning_trace}
          </p>
        </div>

        {/* Edit Option */}
        <div className="space-y-2">
          <label className="text-sm font-medium">
            Edit Content (optional):
          </label>
          <Textarea
            value={editedContent}
            onChange={(e) => setEditedContent(e.target.value)}
            placeholder="Enter edited content if changes are needed..."
            className="min-h-[80px]"
          />
        </div>

        {/* Action Buttons */}
        <div className="flex justify-end gap-3 pt-4 border-t">
          <Button
            variant="outline"
            onClick={() => setShowRejectForm(true)}
            className="border-red-200 text-red-600 hover:bg-red-50"
          >
            Reject
          </Button>
          <Button
            variant="outline"
            onClick={() => onApprove(task_id, editedContent || undefined)}
            className="border-yellow-200"
          >
            Request Changes
          </Button>
          <Button
            onClick={() => onApprove(task_id, editedContent || undefined)}
            className="bg-green-600 hover:bg-green-700 text-white"
          >
            Approve & Publish
          </Button>
        </div>

        {/* Reject Form */}
        {showRejectForm && (
          <div className="p-4 bg-red-50 rounded-lg border border-red-200 space-y-3">
            <h4 className="text-sm font-medium text-red-800">
              Reject Content
            </h4>
            <Textarea
              value={rejectReason}
              onChange={(e) => setRejectReason(e.target.value)}
              placeholder="Reason for rejection..."
              className="min-h-[60px]"
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

        {/* High Attention Warning */}
        {highAttentionNeeded && (
          <div className="p-3 bg-red-100 border border-red-300 rounded text-red-800 text-sm">
            ⚠️ <strong>High Attention Needed:</strong> This content has low 
            confidence and requires careful review before publishing.
          </div>
        )}
      </CardContent>
    </Card>
  );
}

export default ReviewCard;
