# Feb 5 Submission — Client Email (≤400 words)

**Subject:** Request to time-box Finance vs Delivery reconciliation (warehouse build)

Hi [Client Team],

As part of our validation while building the centralized data warehouse, we performed an initial reconciliation between the Finance payments data and the Delivery status data. We’re seeing **differences in counts and totals** that prevent a reliable tie-out between financial activity (e.g., “paid”) and operational outcomes (e.g., “delivered”).

At this stage, the root cause is **not yet confirmed**. In legacy environments with multiple source systems and evolving processes, these gaps are commonly driven by a few categories of issues. Examples of what we are seeing patterns consistent with include:
- **Duplicate/replayed transactions** (e.g., retries or multiple records for the same business event), which can inflate Finance totals if not deduplicated correctly.
- **Missing/inconsistent join keys** across systems (e.g., an identifier present in Finance but absent or formatted differently in Delivery), which makes certain records unmatchable.
- **Timing differences** between when a payment is recorded and when delivery events are recorded (late-arriving updates, month-end cutoffs).
- **Definition mismatches** (e.g., how to treat returns, failed deliveries, and refunds when reporting “revenue” vs “successful delivery”).

To avoid embedding incorrect assumptions into the warehouse and later having to rework executive reporting, I recommend a **time-boxed reconciliation investigation (1–2 business days)** to produce a short decision memo that includes:
1) agreed metric definitions (“paid,” “delivered,” “returned/refunded,” etc.),  
2) deduplication + join rules (which keys, which priority, how to handle exceptions),  
3) a documented set of known exceptions and how they will appear in dashboards.

**Options:**
- **Option A (recommended):** Approve the 1–2 day time-box now to confirm drivers and lock reporting rules before we publish metrics from the warehouse.
- **Option B:** Continue on schedule with provisional rules, accepting higher risk of later rework and reporting disputes.

If you approve **Option A**, could you please nominate one point person from Finance and one from Delivery for a short working session? We will share the memo and implementation rules immediately after the time-box concludes.

Thanks,  
Lemlem  
Data Engineering

```
Finance (payments) --[keys + rules]--> Delivery (status events)
         duplicates | missing keys | timing cutoffs | definition drift
```

